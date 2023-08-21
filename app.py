import os
import bcrypt
import pymssql
from extrair import principal
from flask_bcrypt import Bcrypt
from flask import Flask, redirect, render_template, request, session


padrao_email =  r"^[a-zA-Z0-9._%+-]+@costaesilvaadv\.com\.br$"
color_danger = "#ff0000"
color_success = "#008800"

secret_key = os.getenv('secret_key')
database = os.getenv('db_databese_dev')
user = os.getenv('db_username_dev')
password = os.getenv('db_password_dev')
server = os.getenv('db_server_dev')

app = Flask(__name__)

bcryptObj = Bcrypt(app)

app.secret_key = secret_key 

def conectar():
    return pymssql.connect(host=server, user=user, password=password, database=database)

def criptografar_senha(senha):
    return bcryptObj.generate_password_hash(senha).decode('utf-8')

def verificar_senha(hash_senha, senha):
    if bcryptObj.check_password_hash(hash_senha, senha):
        pass
    else: 
        mensagem = "Email ou senha inválidos."
        return render_template('index.html', mensagem=mensagem, color=color_danger)


@app.route('/', methods=['POST', 'GET'])
def login():
    if request.method == 'POST':
        email = request.form["email"]
        senha = request.form["senha"]
        conn = conectar()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM usuarios_robo_pagamento WHERE email = %s", (email,))
        usuario = cursor.fetchone()
        cursor.close()
        conn.close()
        if usuario:
            session['user_id'] = usuario[0]
            stored_hashed_password = usuario[-1].encode('utf-8')
            if bcrypt.checkpw(senha.encode('utf-8'), stored_hashed_password):
                session['user_id'] = usuario[0]
                session['email'] = usuario[2]
                nome = usuario[1]
                return render_template("home.html", nome=nome)
            else:
                mensagem = 'Usuário ou senha inválidos. Tente novamente.'
                return render_template("index.html", mensagem=mensagem, color=color_danger)
        else: 
            mensagem = "Usuário não cadastrado. Para mais informações consulte o suporte."
            return render_template("index.html", mensagem=mensagem, color=color_danger)

    return render_template("index.html")

@app.route("/home", methods=['POST', 'GET'])
def home():
    return render_template('home.html')

@app.route('/planilha', methods=['POST', 'GET'])
def subir_planilha_adm_sap():
    if 'user_id' not in session:
            mensagem = 'Usuário não tem permissão para acessar essa página. Faça o login e tente novamente.'
            return render_template("index.html", mensagem=mensagem, color=color_danger)
    if request.method == 'POST':
        arquivo = request.form['file']
        data_arquivo = request.form['dt_previsao_credito']
        tipo = request.form['tipo_documento']
        principal(arquivo, data_arquivo, tipo)
    return render_template('enviar_arquivo.html')

@app.route("/logout")
def logout():
    session.pop("user_id", None)
    return redirect("/")


if __name__ == "__main__":
    app.run()
