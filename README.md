# TripAdvance

"""bash

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
│       ├── home.py         # Página inicial
│       ├── login_register.py # Página de login/registro
│       ├── reset_password.py # Página para redefinir senha
│
├── venv/                    # Ambiente virtual (não comitar no Git)
│
├── .gitignore               # Arquivos e pastas ignorados pelo Git
├── LICENSE                  # Licença do projeto
├── README.md                # Documentação inicial do projeto
├── requirements.txt         # Dependências do Python para o projeto
└── streamlit_app.py         # Arquivo principal do Streamlit (ponto de entrada)
"""