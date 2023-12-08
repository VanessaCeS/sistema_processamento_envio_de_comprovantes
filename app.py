import os
import bcrypt
import pymssql
from flask_bcrypt import Bcrypt
from werkzeug.utils import secure_filename
from rotina_rpas import dividir_e_renomear_pdf_rpas
from rotina_contra_cheque import dividir_e_renomear_pdf_contra_cheque
from flask import Flask, flash, redirect, render_template, request, session


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
UPLOAD_FOLDER = 'pdfs'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

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
                return render_template("cadastrar_folha_pagamento.html", nome=nome)
            else:
                mensagem = 'Usuário ou senha inválidos. Tente novamente.'
                return render_template("login.html", mensagem=mensagem, color=color_danger)
        else: 
            mensagem = "Usuário não cadastrado. Para mais informações consulte o suporte."
            return render_template("login.html", mensagem=mensagem, color=color_danger)

    return render_template("login.html")

@app.route('/folha-pagamento', methods=['POST', 'GET'])
def cadastrar_folha_pagamento():
    if 'user_id' not in session:
            mensagem = 'Usuário não tem permissão para acessar essa página. Faça o login e tente novamente.'
            return render_template("login.html", mensagem=mensagem, color=color_danger)
    if request.method == 'POST':
        if 'arquivo' not in request.files:
            flash('Nenhum arquivo enviado')
            return redirect(request.url)
        arquivo = request.files['arquivo']
        if arquivo and allowed_file(arquivo.filename):
            filename = secure_filename(arquivo.filename)
            arquivo_salvo = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            arquivo.save(arquivo_salvo)
        tipo = request.form['pagamento']
        mes_referencia = request.form['mes_referencia']
        if tipo == 'contra_cheque':
            dividir_e_renomear_pdf_contra_cheque(arquivo_salvo, mes_referencia)
        elif tipo == 'rpas':
            dividir_e_renomear_pdf_rpas(arquivo_salvo, mes_referencia)
        flash('Dados enviados e serão processados.')
        return redirect('/folha-pagamento')  

    return render_template('cadastrar_folha_pagamento.html')

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in {'pdf'} 

@app.route("/logout")
def logout():
    session.pop("user_id", None)
    return redirect("/")

if __name__ == "__main__":
    app.run()
