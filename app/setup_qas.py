import pymongo
import streamlit as st
from datetime import datetime
from bson import ObjectId

# Função para configurar o banco e coleções
@st.cache_resource
def setup_database():
    # Recuperar informações do MongoDB Atlas a partir de `st.secrets`
    mongo_secrets = st.secrets["mongo"]
    uri = mongo_secrets["host"]
    client = pymongo.MongoClient(uri)
    db = client["tripadv_qas"]  # Nome do banco de produção

    # Configurar coleção `users`
    users_collection = db["users"]
    # Criar exemplo inicial na coleção `users`
    example_user = {
        "name": "Crazy Frog",
        "email": "frog.gmail.com",
        "password": "$frog"
    }
    # Verificar se o exemplo já existe para evitar duplicações
    if users_collection.count_documents({"email": example_user["email"]}) == 0:
        users_collection.insert_one(example_user)

    # Configurar coleção `uploaded_files`
    if "uploaded_files" not in db.list_collection_names():
        db.create_collection("uploaded_files")

    uploaded_files_collection = db["uploaded_files"]

    # Adicionar índices, se necessário
    uploaded_files_collection.create_index("user_id")  # Índice no campo `user_id`

    # Criar exemplo inicial na coleção `uploaded_files`
    example_file = {
        "user_id": ObjectId("64b0cda9aeed8f0be6aff26f"),  # Substitua por um ObjectId válido
        "datetime": datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%SZ"),
        "file": "meu_arquivo.xlsx",
        "size": 2048,  # Tamanho em bytes
        "data": [
            {
                "date(DD/MM/YYYY)": "2024-11-14T00:00:00Z",
                "start_city": "Curitiba",
                "end_city": "São Paulo",
                "airline": "Gol",
                "duration(minutes)": 90,
                "price(dol)": 1000.0
            }
        ],
        "trained": False
    }

    # Verificar se um exemplo já existe
    if uploaded_files_collection.count_documents({"file": example_file["file"]}) == 0:
        uploaded_files_collection.insert_one(example_file)

    return db

# Inicializar banco e coleções
setup_database()