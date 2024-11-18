import streamlit as st
import pymongo

# Initialize connection.
# Uses st.cache_resource to only run once.
@st.cache_resource
def init_connection():
    client = pymongo.MongoClient(**st.secrets["mongo"])
    # Send a ping to confirm a successful connection
    try:
        client.admin.command('ping')
        st.write("Pinged your deployment. You successfully connected to MongoDB!")
    except Exception as e:
        st.error(f"Failed to connect to MongoDB: {e}")
    return client

client = init_connection()

# Verify collections in the database.
# Uses st.cache_data to only rerun after 10 min or if the database changes.
@st.cache_data(ttl=600)
def get_collections():
    db = client.mydb
    collections = db.list_collection_names()  # Fetch all collection names
    return collections

collections = get_collections()

# Print results.
if collections:
    st.write("Collections in the database:")
    for collection in collections:
        st.write(f"- {collection}")
else:
    st.write("No collections found in the database.")

# import streamlit as st
# import pymongo
# from pymongo import MongoClient
# import bcrypt
# from datetime import datetime
# import re
# import time
# from streamlit.runtime.scriptrunner import add_script_run_ctx
# import subprocess

# # Configurações de segurança
# MIN_PASSWORD_LENGTH = 8
# MAX_LOGIN_ATTEMPTS = 3
# LOGIN_TIMEOUT = 300  # 5 minutos em segundos

# # Validações
# def is_valid_email(email):
#     pattern = r'^[\w\.-]+@[\w\.-]+\.\w+$'
#     return re.match(pattern, email) is not None

# def is_strong_password(password):
#     """Verifica se a senha atende aos requisitos mínimos"""
#     if len(password) < MIN_PASSWORD_LENGTH:
#         return False, "Senha deve ter pelo menos 8 caracteres"
#     if not re.search(r"[A-Z]", password):
#         return False, "Senha deve conter pelo menos uma letra maiúscula"
#     if not re.search(r"[a-z]", password):
#         return False, "Senha deve conter pelo menos uma letra minúscula"
#     if not re.search(r"\d", password):
#         return False, "Senha deve conter pelo menos um número"
#     if not re.search(r"[!@#$%^&*(),.?\":{}|<>]", password):
#         return False, "Senha deve conter pelo menos um caractere especial"
#     return True, "Senha válida"

# # Configuração do MongoDB
# def get_database():
#     mongo_uri = f"mongodb+srv://{st.secrets.mongo.username}:{st.secrets.mongo.password}@{st.secrets.mongo.host}/{st.secrets.mongo.cluster}?retryWrites=true&w=majority"
    
#     try:
#         client = MongoClient(mongo_uri)
#         client.admin.command('ping')
#         return client[st.secrets.mongo.cluster]
#     except Exception as e:
#         st.error(f"Erro ao conectar ao MongoDB: {e}")
#         return None

# def hash_password(password):
#     return bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())

# def check_password(password, hashed_password):
#     return bcrypt.checkpw(password.encode('utf-8'), hashed_password)

# def create_user(email, password):
#     try:
#         db = get_database()
#         if db is not None:
#             users = db.users
#             # Verifica email
#             if not is_valid_email(email):
#                 return False, "Formato de email inválido"
            
#             # Verifica senha
#             is_valid, message = is_strong_password(password)
#             if not is_valid:
#                 return False, message
            
#             # Verifica se usuário existe
#             existing_user = users.find_one({"email": email})
#             if existing_user is not None:
#                 return False, "Email já cadastrado"
            
#             # Cria novo usuário
#             user_data = {
#                 "email": email,
#                 "password": hash_password(password),
#                 "created_at": datetime.utcnow(),
#                 "login_attempts": 0,
#                 "last_login_attempt": None
#             }
#             users.insert_one(user_data)
#             return True, "Usuário criado com sucesso"
#         return False, "Erro na conexão com o banco de dados"
#     except Exception as e:
#         return False, f"Erro ao criar usuário: {str(e)}"

# def login_user(email, password):
#     try:
#         db = get_database()
#         if db is not None:
#             users = db.users
#             user = users.find_one({"email": email})
            
#             if user is None:
#                 return False, "Email ou senha incorretos"
            
#             # Verifica bloqueio por tentativas
#             if user.get('login_attempts', 0) >= MAX_LOGIN_ATTEMPTS:
#                 last_attempt = user.get('last_login_attempt')
#                 if last_attempt:
#                     time_passed = (datetime.utcnow() - last_attempt).total_seconds()
#                     if time_passed < LOGIN_TIMEOUT:
#                         remaining = int(LOGIN_TIMEOUT - time_passed)
#                         return False, f"Conta bloqueada. Tente novamente em {remaining} segundos"
#                     else:
#                         # Reset das tentativas após timeout
#                         users.update_one(
#                             {"email": email},
#                             {"$set": {"login_attempts": 0}}
#                         )
            
#             if check_password(password, user['password']):
#                 # Reset das tentativas após login bem-sucedido
#                 users.update_one(
#                     {"email": email},
#                     {
#                         "$set": {
#                             "login_attempts": 0,
#                             "last_login": datetime.utcnow()
#                         }
#                     }
#                 )
#                 return True, "Login realizado com sucesso"
#             else:
#                 # Incrementa tentativas de login
#                 users.update_one(
#                     {"email": email},
#                     {
#                         "$inc": {"login_attempts": 1},
#                         "$set": {"last_login_attempt": datetime.utcnow()}
#                     }
#                 )
#                 return False, "Email ou senha incorretos"
#         return False, "Erro na conexão com o banco de dados"
#     except Exception as e:
#         return False, f"Erro ao fazer login: {str(e)}"

# def main():
#     st.title("Sistema de Autenticação")
    
#     menu = ["Login", "Registrar"]
#     choice = st.sidebar.selectbox("Menu", menu)
    
#     if choice == "Login":
#         st.subheader("Login")
        
#         email = st.text_input("Email")
#         password = st.text_input("Senha", type='password')
        
#         if st.button("Login"):
#             success, message = login_user(email, password)
#             if success:
#                 st.success(message)
#                 st.session_state['logged_in'] = True
#                 st.session_state['email'] = email
#                 time.sleep(2)  # Pequeno delay para mostrar a mensagem de sucesso
#                 st.switch_page("pages/pag1.py")
#             else:
#                 st.error(message)
                
#     else:
#         st.subheader("Criar Nova Conta")
        
#         with st.form("registro"):
#             email = st.text_input("Email")
#             password = st.text_input("Senha", type='password', 
#                                   help="Mínimo 8 caracteres, incluindo maiúsculas, minúsculas, números e caracteres especiais")
#             confirm_password = st.text_input("Confirmar Senha", type='password')
            
#             submit_button = st.form_submit_button("Registrar")
            
#             if submit_button:
#                 if password != confirm_password:
#                     st.error("As senhas não coincidem")
#                 else:
#                     success, message = create_user(email, password)
#                     if success:
#                         st.success(message)
#                         time.sleep(2)  # Pequeno delay para mostrar a mensagem de sucesso
#                         st.session_state['logged_in'] = True
#                         st.session_state['email'] = email
#                         st.switch_page("pages/pag1.py")
#                     else:
#                         st.error(message)

# if __name__ == '__main__':
#     if 'logged_in' not in st.session_state:
#         st.session_state['logged_in'] = False
#     main()