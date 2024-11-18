import streamlit as st
from app.pages import _home, login_register, reset_password

st.sidebar.title("Navegação")
page = st.sidebar.radio("Ir para", ["Home", "Login/Registrar", "Alterar Senha"])

if page == "Home":
    _home.display()
elif page == "Login/Registrar":
    login_register.login_register()
elif page == "Alterar Senha":
    reset_password.reset_password()