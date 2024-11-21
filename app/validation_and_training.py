import streamlit as st
import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.tree import DecisionTreeRegressor
from sklearn.neighbors import KNeighborsRegressor
from sklearn.metrics import mean_absolute_error, mean_squared_error
from sklearn.preprocessing import MinMaxScaler
import matplotlib.pyplot as plt

def verificar_arquivo(uploaded_file):
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
            return False, "O arquivo não está no formato esperado. Verifique as colunas."

        # Verificar se o arquivo contém apenas o modelo vazio
        if data.empty:
            return False, "O arquivo está vazio. Preencha os dados antes de enviar."

        # Verificar linhas com dados ausentes
        if data.isnull().any().any():
            return False, "O arquivo contém células vazias. Preencha todos os campos."

        # Conversão e validação de tipos
        try:
            data["date(DD/MM/YYYY)"] = pd.to_datetime(data["date(DD/MM/YYYY)"], format="%d/%m/%Y")
            data["start_city"] = data["start_city"].astype(str)
            data["end_city"] = data["end_city"].astype(str)
            data["airline"] = data["airline"].astype(str)
            data["duration(minutes)"] = data["duration(minutes)"].astype(int)
            data["price(dol)"] = data["price(dol)"].astype(float)
        except ValueError as e:
            return False, f"Erro de conversão de tipos: {e}"

        # Retorna o DataFrame validado
        return True, data
    except Exception as e:
        return False, f"Erro ao processar o arquivo: {e}"

def preprocess_data(df):
    """
    Realiza o pré-processamento dos dados para o modelo.
    """
    try:
        # Remover valores nulos
        df = df.dropna()

        # Garantir que as colunas necessárias sejam numéricas
        df['price(dol)'] = pd.to_numeric(df['price(dol)'], errors='coerce')  # Erros serão convertidos para NaN
        df['duration(minutes)'] = pd.to_numeric(df['duration(minutes)'], errors='coerce')

        # Remover linhas com NaN após conversão
        df = df.dropna(subset=['price(dol)', 'duration(minutes)'])

        # Normalização da duração
        scaler = MinMaxScaler()
        df['duration(minutes)'] = scaler.fit_transform(df[['duration(minutes)']])

        return df, scaler
    except Exception as e:
        raise ValueError(f"Erro no pré-processamento dos dados: {e}")

def train_model(df, model_type="Decision Tree", params=None):
    """
    Treina o modelo com os dados fornecidos.
    """
    try:
        # Divisão dos dados
        X = df[['duration(minutes)']]
        y = df['price(dol)']
        X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

        # Escolha do modelo
        if model_type == 'Decision Tree':
            model = DecisionTreeRegressor(max_depth=params.get('max_depth', 5), random_state=42)
        elif model_type == 'KNN':
            model = KNeighborsRegressor(n_neighbors=params.get('n_neighbors', 5))
        else:
            raise ValueError("Tipo de modelo não suportado.")

        # Treinamento
        model.fit(X_train, y_train)
        y_pred = model.predict(X_test)

        # Avaliação do modelo
        mae = mean_absolute_error(y_test, y_pred)
        mse = mean_squared_error(y_test, y_pred)
        rmse = np.sqrt(mse)

        metrics = {
            "MAE": mae,
            "MSE": mse,
            "RMSE": rmse
        }

        return model, metrics
    except Exception as e:
        raise ValueError(f"Erro no treinamento do modelo: {e}")

def plot_metrics_and_data(df, metrics):
    """
    Exibe gráficos e métricas do modelo treinado no Streamlit.
    """
    try:
        # Gráfico de dispersão para relação entre duração e preço
        st.write("### Relação entre Duração e Preço")
        fig, ax = plt.subplots(figsize=(8, 6))
        ax.scatter(df['duration(minutes)'], df['price(dol)'], c='blue', alpha=0.7)
        ax.set_title("Relação entre Duração e Preço")
        ax.set_xlabel("Duração (normalizada)")
        ax.set_ylabel("Preço (USD)")
        ax.grid(True)
        st.pyplot(fig) 

        # Exibir métricas no Streamlit
        st.write("### Métricas do Modelo:")
        for metric, value in metrics.items():
            st.write(f"**{metric}:** {value:.2f}")

    except Exception as e:
        raise ValueError(f"Erro na plotagem ou exibição de métricas: {e}")