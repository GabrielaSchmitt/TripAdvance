import streamlit as st
from app.db_conn import get_db
from app.utils import hash_password, check_password

def login_register():
    db = get_db()
    users = db["users"]

    # Tabs para alternar entre Login e Registro
    tab1, tab2 = st.tabs(["Login", "Registrar-se"])

    # Aba de Login
    with tab1:
        email = st.text_input("Email")
        password = st.text_input("Senha", type="password")
        if st.button("Login"):
            user = users.find_one({"email": email})
            if user and check_password(password, user["password"]):
                st.success(f"Bem-vindo, {user['name']}!")
            else:
                st.error("Email ou senha incorretos.")

    # Aba de Registro
    with tab2:
        name = st.text_input("Nome")
        email = st.text_input("Email")
        password = st.text_input("Senha", type="password")
        if st.button("Registrar"):
            if users.find_one({"email": email}):
                st.error("Email já cadastrado.")
            else:
                hashed_password = hash_password(password)
                users.insert_one({"name": name, "email": email, "password": hashed_password})
                st.success("Usuário registrado com sucesso!")