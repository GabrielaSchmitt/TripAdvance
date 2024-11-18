import streamlit as st
from app.pages import login_register, reset_password, home

st.sidebar.title("Navegação")
page = st.sidebar.radio("Ir para", ["Login/Registrar", "Home", "Alterar Dados"])

if page == "Login/Registrar":
    login_register.login_register()
elif page == "Home":
    home.home()
elif page == "Alterar Dados":
    reset_password.reset_password()