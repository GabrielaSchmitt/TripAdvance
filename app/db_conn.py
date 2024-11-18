import pymongo
import streamlit as st

@st.cache_resource
def get_db():
    mongo_secrets = st.secrets["mongo"]
    uri = mongo_secrets["host"]
    client = pymongo.MongoClient(uri)
    return client["tripadv_qas"]