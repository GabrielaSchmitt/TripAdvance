<h1 align="center">TripAdvance</h1> 

<p> O TripAdvance é um projeto desenvolvido para otimizar e automatizar processos de análise e modelagem de dados relacionados a viagens. A aplicação combina a interface intuitiva do Streamlit, funcionalidades robustas de processamento de dados com Python, e uma infraestrutura de backend escalável com MongoDB e AWS. </p>

## Objetivo do Projeto
<p> O TripAdvance foi projetado para auxiliar na ingestão, processamento, treinamento e gestão de modelos preditivos baseados em dados de viagens. Ele utiliza uma abordagem eficiente para manipular dados carregados pelos usuários, garantindo que: </p>


- Modelos sejam treinados e atualizados automaticamente em horários de baixa demanda.
- Apenas os modelos com melhor desempenho sejam definidos como referência principal ("MASTER").
- Toda a infraestrutura seja integrada a serviços na nuvem para armazenamento seguro e processamento distribuído.


## Principais Funcionalidades

- **Interface do Streamlit**: Interface amigável para upload de arquivos, configuração de treinos e exibição de métricas.
- **Treinamento Automatizado**: Processos de treinamento disparados automaticamente com base em triggers no MongoDB.
- **Step Functions na AWS**: Garantem um pipeline eficiente para pré-processamento, treinamento e armazenamento de modelos.
- **Gestão de Modelos**: Comparação automática de métricas entre modelos para identificar e promover o melhor como "MASTER".
- **Escalabilidade**: Integração com AWS S3 e Lambda para processamento em larga escala e armazenamento seguro.


### Estrutura do projeto 

<p>A estrutura do projeto foi cuidadosamente organizada para garantir modularidade, escalabilidade e facilidade de manutenção. Ela inclui: </p>

- Configuração de ambiente local e remoto.
- Scripts e funções para conexão com o banco de dados e serviços na nuvem.
- Arquivos para gestão de dependências e segredos de API.

```bash

TRIPADVANCE/
│
├── .devcontainer/           # Arquivo de configuração do ambiente de desenvolvimento
│   └── devcontainer.json
│
├── .streamlit/              # Configurações do Streamlit
│   └── secrets.toml         # Configuração de segredos (URI do banco de dados)
│
├── app/                     # Código principal do projeto
│   ├── db_conn.py           # Conexão com o MongoDB
│   ├── utils.py             # Funções auxiliares (ex: hash de senha)
│   ├── setup_qas.py         # Script de configuração inicial do banco de dados
│   └── pages/               # Páginas do Streamlit
│       ├── home.py          # Página inicial
│       ├── login_register.py # Página de login/registro
│       ├── reset_password.py # Página para redefinir senha
|
├── aws/                     # documentação de serviços externos
│   ├── step_function.py     
│   ├── ModelTrainingFunction.py         # lambda de treino
│   ├── preprocess-files-function.py     # lambda de pre processamento
│   ├── SaveModelFunction.py             # lambda para salvar modelo
│   ├── step_function.json               # configuração da step function
|
├── mongodb_services/        # documentação de serviços externos
│   ├── trigger.js           # Trigger configurado internamente
|
├── sample_xlsx/             # exemplos de datasets
│   ├── flights.xlsx        
|
├── venv/                    # Ambiente virtual (não comitar no Git)
│
├── .gitignore               # Arquivos e pastas ignorados pelo Git
├── LICENSE                  # Licença do projeto
├── README.md                # Documentação inicial do projeto
├── requirements.txt         # Dependências do Python para o projeto
└── streamlit_app.py         # Arquivo principal do Streamlit (ponto de entrada)
```

### Integrações

<p>No ambiente do MongoDB Atlas há uma função de trigger que dispara uma Step Function na AWS. Dentro da step function há 3 lambda functions pré-processamento -> treino -> salva modelo. Foi configurado um S3 como storage da AWS. </p>

<p>A ideia é o trigger do mongo rodar todos os dias a meia noite, com uma lógica para verificar a tabela/collection "uploaded_files" juntando todos os arquivos do primeiro adicionado ao último, até que atinja um tamanho mínimo. Assim, é verificado se o horário atual é pertinente ( 00:00 - 06:00 ) para que não sobrecarregue o sistema durante o período em que os usuários estão utilizando, também garantindo a recursão para treinos em sequência particionados. No ambiente da AWS as step functions funcionam como um workflow, assim passará pelo preprocessamento garantindo a normalização dos dados, alimentando a função seguinte de treino que por sua vez processa os dados criando um modelo, e por fim salva o modelo retornando-o para o mongo_db na tabela/collection "models". Antes de salvar é feita uma lógica de comparação entre o modelo do banco cujo campo "MASTER" é verdadeiro, caso as métricas de acurácia do novo modelo se mostrem superiores, este novo modelo passa a ser "MASTER".</p>
