import streamlit as st
import pandas as pd
from pymongo import MongoClient
import bcrypt
from datetime import datetime

# Configuração da conexão com MongoDB Atlas
def get_database():
    # Construindo a string de conexão do MongoDB Atlas usando os secrets
    mongo_uri = f"mongodb+srv://{st.secrets['mongo']['username']}:{st.secrets['mongo']['password']}@{st.secrets['mongo']['host']}/?retryWrites=true&w=majority&appName={st.secrets['mongo']['cluster']}"
    
    try:
        client = MongoClient(mongo_uri)
        # Teste a conexão
        client.admin.command('ping')
        return client[st.secrets['mongo']['cluster']]
    except Exception as e:
        st.error(f"Erro ao conectar com MongoDB: {str(e)}")
        return None

# Funções de autenticação
def hash_password(password):
    return bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())

def check_password(password, hashed_password):
    return bcrypt.checkpw(password.encode('utf-8'), hashed_password)

def create_user(username, password):
    db = get_database()
    if not db:
        return False, "Erro de conexão com o banco de dados"
    
    existing_user = db.users.find_one({'username': username})
    if existing_user:
        return False, "Usuário já existe"
    
    hashed_pw = hash_password(password)
    db.users.insert_one({
        'username': username,
        'password': hashed_pw,
        'created_at': datetime.now()
    })
    return True, "Usuário criado com sucesso"

def verify_login(username, password):
    db = get_database()
    if not db:
        return False
    
    user = db.users.find_one({'username': username})
    if user and check_password(password, user['password']):
        return True
    return False

# Interface principal
def main():
    st.set_page_config(page_title="Sistema de Upload", layout="wide")
    
    # Tenta estabelecer conexão com o banco
    db = get_database()
    if not db:
        st.error("Não foi possível conectar ao banco de dados. Verifique as configurações.")
        return
    
    # Inicialização de estado da sessão
    if 'logged_in' not in st.session_state:
        st.session_state['logged_in'] = False

    if not st.session_state['logged_in']:
        tab1, tab2 = st.tabs(["Login", "Registrar"])
        
        with tab1:
            st.header("Login")
            login_username = st.text_input("Usuário", key="login_username")
            login_password = st.text_input("Senha", type="password", key="login_password")
            
            if st.button("Entrar"):
                if verify_login(login_username, login_password):
                    st.session_state['logged_in'] = True
                    st.success("Login realizado com sucesso!")
                    st.rerun()
                else:
                    st.error("Usuário ou senha inválidos")
        
        with tab2:
            st.header("Registrar")
            reg_username = st.text_input("Usuário", key="reg_username")
            reg_password = st.text_input("Senha", type="password", key="reg_password")
            reg_password_confirm = st.text_input("Confirmar Senha", type="password", key="reg_password_confirm")
            
            if st.button("Registrar"):
                if reg_password != reg_password_confirm:
                    st.error("As senhas não coincidem")
                else:
                    success, message = create_user(reg_username, reg_password)
                    if success:
                        st.success(message)
                    else:
                        st.error(message)
    
    else:
        st.header("Home Screen")
        st.write("Bem-vindo ao sistema!")
        
        # Upload de arquivo Excel
        uploaded_file = st.file_uploader("Escolha um arquivo Excel", type=['xlsx', 'xls'])
        
        if uploaded_file is not None:
            try:
                df = pd.read_excel(uploaded_file)
                st.success("Arquivo carregado com sucesso!")
                st.write("Preview dos dados:")
                st.dataframe(df.head())
                
                if st.button("Salvar dados no MongoDB"):
                    records = df.to_dict('records')
                    db.excel_data.insert_many(records)
                    st.success("Dados salvos com sucesso no MongoDB!")
            
            except Exception as e:
                st.error(f"Erro ao processar arquivo: {str(e)}")
        
        if st.button("Logout"):
            st.session_state['logged_in'] = False
            st.rerun()

if __name__ == "__main__":
    main()