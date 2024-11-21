# import streamlit as st
# import pandas as pd
# from app.db_conn import get_db
# import pickle
# from io import BytesIO
# from datetime import datetime, timezone
# from app.validation_and_training import verificar_arquivo, preprocess_data, train_model, plot_metrics_and_data

# def home():
#     if "logged_in" not in st.session_state or not st.session_state["logged_in"]:
#         st.error("Acesso negado. Faça login primeiro.")
#         return

#     db = get_db()
#     uploaded_files = db["uploaded_files"]
#     rush_models = db["rush_models"]  

#     # Baixar Excel padrão
#     st.subheader("Baixar Modelo de Excel")
#     sample_data = pd.DataFrame({
#         "date(DD/MM/YYYY)": ["14/11/2024"],
#         "start_city": ["Curitiba"],
#         "end_city": ["São Paulo"],
#         "airline": ["Gol"],
#         "duration(minutes)": [90],
#         "price(dol)": [1000.0]
#     })
#     to_download = BytesIO()
#     sample_data.to_excel(to_download, index=False, sheet_name="Model")
#     st.download_button(
#         label="Baixar Modelo de Excel",
#         data=to_download,
#         file_name="modelo_viagem.xlsx",
#         mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
#     )

#     # Upload de Excel preenchido
#     st.subheader("Enviar Excel Preenchido")
#     uploaded_file = st.file_uploader("Escolha um arquivo Excel", type=["xlsx"])

#     if uploaded_file:
#        is_valid, result = verificar_arquivo(uploaded_file)

#        if not is_valid:
#         st.error(result)
#         return

#        data = result  # DataFrame retornado pela função de verificação

#        # Obter informações do arquivo
#        file_size = uploaded_file.size
#        user_id = st.session_state["user_id"]

#        # Inserir no banco de dados 'uploaded_files'
#        uploaded_file_doc = uploaded_files.insert_one({
#            "user_id": user_id,
#            "datetime": datetime.now(timezone.utc),
#            "file": uploaded_file.name,
#            "size": file_size,
#            "data": data.to_dict("records"),
#            "trained": False  
#        })
#        uploaded_file_id = uploaded_file_doc.inserted_id  # Recuperando o ID do arquivo inserido
#        st.success(f"Arquivo enviado e armazenado com sucesso! id: {uploaded_file_id}")

#        # A partir daqui, utilizar o resultado nas funções de pré-processamento, treino e métricas
#        try:
#            st.subheader("Treinamento do Modelo")
#            preprocessed_data, scaler = preprocess_data(data)
#            st.write("Dados pré-processados com sucesso.")

#            # Configuração do modelo
#            model_type = st.selectbox("Escolha o tipo de modelo", ["Decision Tree", "KNN"])
#            params = {}

#            if model_type == "Decision Tree":
#                max_depth = st.slider("Profundidade máxima (max_depth)", 1, 20, 5)
#                params["max_depth"] = max_depth
#            elif model_type == "KNN":
#                n_neighbors = st.slider("Número de vizinhos (n_neighbors)", 1, 20, 5)
#                params["n_neighbors"] = n_neighbors

#            if st.button("Treinar Modelo"):
#                # Treinamento do modelo
#                model, metrics = train_model(preprocessed_data, model_type=model_type, params=params)
#                st.success("Modelo treinado com sucesso.")

#                st.write("### Gráficos de Análise:")
#                plot_metrics_and_data(preprocessed_data, metrics)

#                params_dict = params if isinstance(params, dict) else (vars(params) if hasattr(params, '__dict__') else {})
#                metrics_dict = metrics if isinstance(metrics, dict) else (vars(metrics) if hasattr(metrics, '__dict__') else {})
#                scaler_params = dict(scaler.get_params()) if hasattr(scaler, 'get_params') else {}
#                model_bytes = pickle.dumps(model)
 
#             #    # Before the save button, add payload inspection
#             #    st.write("### Payload para Inserção:")
#             #    payload = {
#             #        "user_id": user_id,
#             #        "uploaded_file_id": str(uploaded_file_id),
#             #        "datetime": datetime.utcnow(),
#             #        "model_type": model_type,
#             #        "params": params_dict,
#             #        "metrics": metrics_dict,
#             #        "scaler_params": scaler_params,
#             #        "pickled_model": model_bytes
#             #    } 
#             #    st.write(payload)
                         
#                # Botão para salvar o modelo
#                if st.button("Salvar Modelo"):
#                    try:
#                        # Inserindo o modelo no MongoDB
#                        rush_models.insert_one({
#                             "user_id": user_id,  
#                             "uploaded_file_id": str(uploaded_file_id),  
#                             "datetime": datetime.now(timezone.utc),  
#                             "model_type": model_type,  
#                             "params": params_dict, 
#                             "metrics": metrics_dict,  
#                             "scaler_params": scaler_params,
#                             "pickled_model": model_bytes
#                        })
#                        st.success("Modelo salvo com sucesso no banco de dados!")
#                    except Exception as e:
#                        st.error(f"Erro ao salvar modelo no banco de dados: {e}")

#        except Exception as e:
#            st.error(f"Erro no processo de treinamento: {e}")

import streamlit as st
import pandas as pd
from app.db_conn import get_db
import pickle
from io import BytesIO
from datetime import datetime, timezone
from app.validation_and_training import verificar_arquivo, preprocess_data, train_model, plot_metrics_and_data

def home():
    if "logged_in" not in st.session_state or not st.session_state["logged_in"]:
        st.error("Acesso negado. Faça login primeiro.")
        return

    db = get_db()
    uploaded_files = db["uploaded_files"]
    rush_models = db["rush_models"]  

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
        is_valid, result = verificar_arquivo(uploaded_file)

        if not is_valid:
            st.error(result)
            return

        data = result  # DataFrame retornado pela função de verificação

        # Obter informações do arquivo
        file_size = uploaded_file.size
        user_id = st.session_state["user_id"]

        # Inserir no banco de dados 'uploaded_files'
        uploaded_file_doc = uploaded_files.insert_one({
            "user_id": user_id,
            "datetime": datetime.now(timezone.utc),
            "file": uploaded_file.name,
            "size": file_size,
            "data": data.to_dict("records"),
            "trained": False  
        })
        uploaded_file_id = uploaded_file_doc.inserted_id  # Recuperando o ID do arquivo inserido
        st.success(f"Arquivo enviado e armazenado com sucesso! id: {uploaded_file_id}")

        try:
            st.subheader("Treinamento do Modelo")
            preprocessed_data, scaler = preprocess_data(data)
            st.write("Dados pré-processados com sucesso.")

            # Configuração do modelo
            model_type = st.selectbox("Escolha o tipo de modelo", ["Decision Tree", "KNN"])
            params = {}

            if model_type == "Decision Tree":
                max_depth = st.slider("Profundidade máxima (max_depth)", 1, 20, 5)
                params["max_depth"] = max_depth
            elif model_type == "KNN":
                n_neighbors = st.slider("Número de vizinhos (n_neighbors)", 1, 20, 5)
                params["n_neighbors"] = n_neighbors

            # Criando duas colunas para os botões
            col1, col2 = st.columns(2)

            with col1:
                train_button = st.button("Treinar Modelo")

            if train_button:
                # Armazenar resultados do treinamento em session_state
                model, metrics = train_model(preprocessed_data, model_type=model_type, params=params)
                st.session_state['trained_model'] = model
                st.session_state['model_metrics'] = metrics
                st.session_state['model_params'] = params
                st.session_state['model_scaler'] = scaler
                st.session_state['model_type'] = model_type
                st.session_state['uploaded_file_id'] = uploaded_file_id
                
                st.success("Modelo treinado com sucesso.")
                st.write("### Gráficos de Análise:")
                plot_metrics_and_data(preprocessed_data, metrics)

            # Botão de salvar só aparece depois que o modelo foi treinado
            with col2:
                if 'trained_model' in st.session_state:
                    save_button = st.button("Salvar Modelo")
                    if save_button:
                        try:
                            # Preparar dados para salvar
                            model = st.session_state['trained_model']
                            metrics = st.session_state['model_metrics']
                            params = st.session_state['model_params']
                            scaler = st.session_state['model_scaler']
                            model_type = st.session_state['model_type']
                            
                            # Converter dados para formato adequado
                            params_dict = params if isinstance(params, dict) else (vars(params) if hasattr(params, '__dict__') else {})
                            metrics_dict = metrics if isinstance(metrics, dict) else (vars(metrics) if hasattr(metrics, '__dict__') else {})
                            scaler_params = dict(scaler.get_params()) if hasattr(scaler, 'get_params') else {}
                            model_bytes = pickle.dumps(model)

                            # Inserir no MongoDB
                            result = rush_models.insert_one({
                                "user_id": user_id,
                                "uploaded_file_id": str(uploaded_file_id),
                                "datetime": datetime.now(timezone.utc),
                                "model_type": model_type,
                                "params": params_dict,
                                "metrics": metrics_dict,
                                "scaler_params": scaler_params,
                                "pickled_model": model_bytes
                            })
                            
                            if result.inserted_id:
                                st.success(f"Modelo salvo com sucesso! ID: {result.inserted_id}")
                            else:
                                st.error("Erro ao salvar o modelo: Nenhum ID retornado")
                            
                        except Exception as e:
                            st.error(f"Erro ao salvar modelo no banco de dados: {e}")

        except Exception as e:
            st.error(f"Erro no processo de treinamento: {e}")