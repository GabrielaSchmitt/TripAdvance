import pymongo
import streamlit as st
from datetime import datetime
from bson import ObjectId

# Função para configurar o banco e coleções
@st.cache_resource
def setup_database():
    # Recuperar informações do MongoDB Atlas a partir de `st.secrets`
    mongo_secrets = st.secrets["mongo"]
    uri = f"mongodb+srv://{mongo_secrets['username']}:{mongo_secrets['password']}@{mongo_secrets['host']}/{mongo_secrets['cluster']}?retryWrites=true&w=majority"
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

    # Configurar coleção `models`
    if "models" not in db.list_collection_names():
        db.create_collection("models")

    models_collection = db["models"]

    # Criar índices para a coleção `models`
    models_collection.create_index(
        [("is_master", pymongo.ASCENDING)],
        unique=True,
        partialFilterExpression={"is_master": False}  
    )

    models_collection.create_index(
        [("created_at", pymongo.DESCENDING)]
    )

    # Criar exemplo inicial na coleção `models`
    example_model = {
        "model_base64": "example_model_base64_data",
        "scaler_base64": "example_scaler_base64_data",
        "created_at": datetime.utcnow(),
        "metrics": {
            "mean_absolute_error": 10.0,
            "mean_squared_error": 50.0,
            "root_mean_squared_error": 7.1,
            "r2_score": 0.85,
            "mean_absolute_percentage_error": 15.0,
            "accuracy_10_percent": 90.0
        },
        "training_metadata": {
            "processed_files_count": 10,
            "file_ids": [ObjectId("64b0cda9aeed8f0be6aff26f")],  # Referência aos arquivos utilizados
            "s3_model_path": "models/example_model.joblib",
            "s3_scaler_path": "models/example_scaler.joblib",
            "training_job_id": "job_123456",
            "training_duration_minutes": 30
        },
        "is_master": True
    }

    # Verificar se um exemplo já existe
    if models_collection.count_documents({"training_job_id": example_model["training_metadata"]["training_job_id"]}) == 0:
        models_collection.insert_one(example_model)

    return db

# Inicializar banco e coleções
setup_database()