import streamlit as st
from app.db_conn import get_db
from app.utils import hash_password, check_password

def login_register():
    db = get_db()
    
    if db is None:
        st.error("Failed to connect to the database. Please try again later.")
        return  # Stop further execution if the database is not connected

    # Proceed if the connection is successful
    try:
        users = db["users"]  # Access the 'users' collection
        st.write("Connected to the users collection!")
        # Add further logic for login or registration
    except Exception as e:
        st.error("An error occurred while accessing the users collection.")
        st.error(f"Details: {e}")

    # Tabs para Login e Registro
    tab1, tab2 = st.tabs(["Login", "Registrar-se"])

    # Aba de Login
    with tab1:
        email = st.text_input("Email", key="login_email").strip().lower() 
        password = st.text_input("Senha", type="password", key="login_password")
        if st.button("Login"):
            user = users.find_one({"email": email})
            if user and check_password(password, user["password"]):
                st.session_state["logged_in"] = True
                st.session_state["user_id"] = user["_id"]
                st.success("Login realizado com sucesso!")
            else:
                st.error("Email ou senha incorretos.")

    # Aba de Registro
    with tab2:
        name = st.text_input("Nome", key="register_name").strip().lower() 
        email = st.text_input("Email", key="register_email").strip().lower() 
        password = st.text_input("Senha", type="password", key="register_password")
        if st.button("Registrar"):
            if users.find_one({"email": email}):
                st.error("Email já cadastrado.")
            else:
                hashed_password = hash_password(password)
                users.insert_one({"name": name, "email": email, "password": hashed_password})
                st.success("Usuário registrado com sucesso!")