import streamlit as st
import pandas as pd
from app.db_conn import get_db
from io import BytesIO
from datetime import datetime

def home():
    if "logged_in" not in st.session_state or not st.session_state["logged_in"]:
        st.error("Acesso negado. Faça login primeiro.")
        return

    db = get_db()
    uploaded_files = db["uploaded_files"]

    # Baixar Excel padrão
    st.subheader("Baixar Modelo de Excel")
    sample_data = pd.DataFrame({
        "date(DD/MM/YYYY)": ["14/11/2024"],
        "start_city": ["Curitiba"],
        "end_city": ["São Paulo"],
        "airline": ["Gol"],
        "duration(minutes)": [90],
        "price(dol)": [1000.0]
    })
    to_download = BytesIO()
    sample_data.to_excel(to_download, index=False, sheet_name="Model")
    st.download_button(
        label="Baixar Modelo de Excel",
        data=to_download,
        file_name="modelo_viagem.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )

    # Upload de Excel preenchido
    st.subheader("Enviar Excel Preenchido")
    uploaded_file = st.file_uploader("Escolha um arquivo Excel", type=["xlsx"])

    if uploaded_file:
        try:
            # Ler dados do arquivo enviado
            data = pd.read_excel(uploaded_file)

            # Colunas esperadas no arquivo
            expected_columns = [
                "date(DD/MM/YYYY)", "start_city", "end_city", 
                "airline", "duration(minutes)", "price(dol)"
            ]

            # Verificar se as colunas estão corretas
            if list(data.columns) != expected_columns:
                st.error("O arquivo não está no formato esperado. Verifique as colunas.")
                return
            
            # Verificar se o arquivo contém apenas o modelo vazio
            if data.empty:
                st.error("O arquivo está vazio. Preencha os dados antes de enviar.")
                return

            # Verificar linhas com dados ausentes
            if data.isnull().any().any():
                st.error("O arquivo contém células vazias. Preencha todos os campos.")
                return

            # Conversão e validação de tipos
            try:
                data["date(DD/MM/YYYY)"] = pd.to_datetime(data["date(DD/MM/YYYY)"], format="%d/%m/%Y")
                data["start_city"] = data["start_city"].astype(str)
                data["end_city"] = data["end_city"].astype(str)
                data["airline"] = data["airline"].astype(str)
                data["duration(minutes)"] = data["duration(minutes)"].astype(int)
                data["price(dol)"] = data["price(dol)"].astype(float)
            except ValueError as e:
                st.error(f"Erro de conversão de tipos: {e}")
                return

            # Obter informações do arquivo
            file_size = uploaded_file.size
            user_id = st.session_state["user_id"]

            # Inserir no banco de dados
            uploaded_files.insert_one({
                "user_id": user_id,
                "datetime": datetime.utcnow(),
                "file": uploaded_file.name,
                "size": file_size,
                "data": data.to_dict("records"),
                "trained": False  # Será usado futuramente para marcar arquivos processados
            })
            st.success("Arquivo enviado e armazenado com sucesso!")
        except Exception as e:
            st.error(f"Erro ao processar o arquivo: {e}")