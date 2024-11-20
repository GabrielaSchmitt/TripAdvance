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
        # Retrieve secrets
        mongo_secrets = st.secrets["mongo"]
        host = mongo_secrets["host"]
        username = mongo_secrets["username"]
        password = mongo_secrets["password"]
        cluster = mongo_secrets["cluster"]

        # Build the URI
        uri = f"mongodb+srv://{username}:{password}@{host}/{cluster}?retryWrites=true&w=majority"

        # Adjust timeout settings
        client = pymongo.MongoClient(uri, serverSelectionTimeoutMS=20000, connectTimeoutMS=20000)

        # Attempt a connection
        client.admin.command("ping")
        return client["tripadv_qas"]

    except ServerSelectionTimeoutError as e:
        st.error("Error: Unable to connect to the MongoDB server. Please try again later.")
        st.error(f"Details: {e}")
        return None
    except Exception as e:
        st.error("An unexpected error occurred.")
        st.error(f"Details: {e}")
        return None