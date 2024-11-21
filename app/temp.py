from pymongo import ASCENDING
from db_conn import get_db
from datetime import datetime, timezone
import pickle

def setup_rush_models_collection():
    db = get_db()

    # Verificar se a coleção 'rush_models' existe
    if 'rush_models' not in db.list_collection_names():
        print("Coleção 'rush_models' não encontrada. Criando...")
        db.create_collection('rush_models')
        print("Coleção 'rush_models' criada com sucesso.")
    else:
        print("Coleção 'rush_models' já existe.")

    # Criar índices para a coleção 'rush_models'
    rush_models = db['rush_models']
    
    # Índice para o campo 'user_id' (para buscas rápidas pelos modelos de um usuário)
    rush_models.create_index([("user_id", ASCENDING)], name="user_id_index")
    print("Índice 'user_id' criado na coleção 'rush_models'.")
    
    # Índice para o campo 'uploaded_file_id' (para associar o modelo ao arquivo carregado)
    rush_models.create_index([("uploaded_file_id", ASCENDING)], name="uploaded_file_id_index")
    print("Índice 'uploaded_file_id' criado na coleção 'rush_models'.")

    # Inserir um documento de teste para verificar a estrutura
    try:
        # Criar dados de teste simulando a estrutura real
        test_params = {"max_depth": 5}
        test_metrics = {"accuracy": 0.95, "mse": 0.05}
        test_scaler_params = {"feature_range": (0, 1)}
        test_model_bytes = pickle.dumps("test_model")  # Simulando um modelo serializado

        test_doc = {
            "user_id": "test_user",
            "uploaded_file_id": "test_file_id",
            "datetime": datetime.now(timezone.utc),
            "model_type": "Decision Tree",
            "params": test_params,
            "metrics": test_metrics,
            "scaler_params": test_scaler_params,
            "pickled_model": test_model_bytes
        }

        # Inserir documento de teste
        rush_models.insert_one(test_doc)
        print("Documento de teste inserido com sucesso!")

        # Remover documento de teste
        rush_models.delete_one({"user_id": "test_user"})
        print("Documento de teste removido. Collection pronta para uso!")

    except Exception as e:
        print(f"Erro ao testar a estrutura da collection: {e}")

if __name__ == "__main__":
    setup_rush_models_collection()