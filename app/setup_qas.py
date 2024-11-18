import pymongo
import streamlit as st

# Função para criar o banco e a coleção oficial
@st.cache_resource
def setup_tripadv_qas():
    mongo_secrets = st.secrets["mongo"]
    uri = mongo_secrets["host"]
    client = pymongo.MongoClient(uri)
    db = client["tripadv_qas"]  # Banco oficial
    users_collection = db["users"]  # Coleção oficial

    # Criar um exemplo inicial na coleção
    example_user = {
        "name": "Crazy Frog",
        "email": "frog.gmail.com",
        "password": "$frog"
    }
    # Verificar se o exemplo já existe para evitar duplicações
    if users_collection.count_documents({"email": example_user["email"]}) == 0:
        users_collection.insert_one(example_user)

    return db

# Inicializar banco e coleção
setup_tripadv_qas()