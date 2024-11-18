import streamlit as st
from app.db_conn import get_db
from app.utils import hash_password

def reset_password():
    db = get_db()
    users = db["users"]

    email = st.text_input("Email")
    new_password = st.text_input("Nova Senha", type="password")
    if st.button("Alterar Senha"):
        result = users.update_one(
            {"email": email},
            {"$set": {"password": hash_password(new_password)}}
        )
        if result.matched_count:
            st.success("Senha alterada com sucesso!")
        else:
            st.error("Email não encontrado.")