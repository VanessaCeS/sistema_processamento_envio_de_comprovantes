import os
import mysql.connector
from dotenv import load_dotenv
load_dotenv('.env')

def criar_banco_de_dados():
    conexao = mysql.connector.connect(
        host= os.getenv("db_server"),
        user=os.getenv("api_login"),
        password=("db_password")
    )
    cursor = conexao.cursor()

    cursor.execute("CREATE DATABASE IF NOT EXISTS contabilidade_rh")

    cursor.execute("USE contabilidade_rh")

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS usuarios (
            id INT AUTO_INCREMENT PRIMARY KEY,
            id_a INT,
            senha VARCHAR(255),
            email VARCHAR(255),
            nome VARCHAR(255),
            usuario VARCHAR(255),
            ultimo_acesso DATETIME,
            data_criacao DATETIME DEFAULT CURRENT_TIMESTAMP,
            data_atualizacao DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
        )
    """)

    cursor.close()
    conexao.close()

    print("Banco de dados 'contabilidade_rh' e tabela 'usuarios' criados com sucesso.")
