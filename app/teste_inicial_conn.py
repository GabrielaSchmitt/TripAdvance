import streamlit as st
import pymongo

# Initialize connection
@st.cache_resource
def init_connection():
    mongo_secrets = st.secrets["mongo"]
    uri = mongo_secrets["host"]
    client = pymongo.MongoClient(uri)
    
    # Ping para verificar conexão
    try:
        client.admin.command('ping')
        st.write("Pinged your deployment. Successfully connected to MongoDB!")
    except Exception as e:
        st.error(f"Failed to connect to MongoDB: {e}")
        raise e

    return client

client = init_connection()

# Acessar a coleção 'users' do banco de dados 'sample_mflix'
@st.cache_data(ttl=600)
def get_sample_users():
    db = client["sample_mflix"]  # Nome do database
    collection = db["users"]  # Nome da coleção
    return list(collection.find().limit(10))  # Buscar os 10 primeiros documentos

users = get_sample_users()

# Exibir os resultados
if users:
    st.write("Users in sample_mflix.users:")
    for user in users:
        st.write(user)
else:
    st.write("No users found in the collection.")