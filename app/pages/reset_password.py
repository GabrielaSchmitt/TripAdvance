import streamlit as st
from app.db_conn import get_db
from app.utils import hash_password

def reset_password():
    if "logged_in" not in st.session_state or not st.session_state["logged_in"]:
        st.error("Acesso negado. Faça login primeiro.")
        return

    db = get_db()
    users = db["users"]

    # Carregar informações do usuário
    user_id = st.session_state["user_id"]
    user = users.find_one({"_id": user_id})

    # Exibir dados do usuário
    st.subheader("Dados do Usuário")
    name = st.text_input("Nome", value=user["name"]).strip().lower() 
    email = st.text_input("Email", value=user["email"]).strip().lower() 
    new_password = st.text_input("Nova Senha (opcional)", type="password")

    # Botão para salvar alterações
    if st.button("Salvar Alterações"):
        update_fields = {"name": name, "email": email}
        if new_password:
            update_fields["password"] = hash_password(new_password)
        users.update_one({"_id": user_id}, {"$set": update_fields})
        st.success("Dados atualizados com sucesso!")