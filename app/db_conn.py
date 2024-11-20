# import pymongo
# import streamlit as st

# @st.cache_resource
# def get_db():
#     mongo_secrets = st.secrets["mongo"]
#     uri = mongo_secrets["host"]
#     client = pymongo.MongoClient(uri)
#     return client["tripadv_qas"]
import pymongo
import streamlit as st
from pymongo.errors import ServerSelectionTimeoutError

@st.cache_resource
def get_db():
    try:
        mongo_secrets = st.secrets["mongo"]
        host = mongo_secrets["host"]
        username = mongo_secrets["username"]
        password = mongo_secrets["password"]
        cluster = mongo_secrets["cluster"]

        uri = f"mongodb+srv://{username}:{password}@{host}/{cluster}?retryWrites=true&w=majority"

        client = pymongo.MongoClient(uri, serverSelectionTimeoutMS=20000, connectTimeoutMS=20000)
        client.admin.command("ping")  # Verify the connection
        return client["tripadv_qas"]

    except ServerSelectionTimeoutError as e:
        st.error("Could not connect to MongoDB. Please check your network or database configuration.")
        st.error(f"Timeout Details: {e}")
        return None
    except Exception as e:
        st.error("An unexpected error occurred while connecting to the database.")
        st.error(f"Error Details: {e}")
        return None