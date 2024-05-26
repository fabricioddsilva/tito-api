import mysql.connector
from flask import Flask, request, render_template, redirect, url_for, session
import agenda
from dotenv import load_dotenv
import os
import hash

load_dotenv()

# Conexão com o banco de dados
mydb = mysql.connector.connect(
    host=os.getenv("host"),
    user=os.getenv("user"),
    password=os.getenv("password"),
    database=os.getenv("database")
)

# Inicializando o Flask
app = Flask(__name__)
app.secret_key = os.getenv("key")

# Redirecionamento para a página de eventos


@app.route('/')
def home():
    return redirect(url_for('eventos'))

# Endpoint de criação de eventos


@app.route('/evento/novo', methods=['POST', 'GET'])
def form():

    # Caso a requisição for post
    if request.method == 'POST':

        req = request.form

        cursor = mydb.cursor()

        sql = f"INSERT INTO eventos (nome, data_evento, hora_inicio, hora_fim, descricao, qtd_visitantes) VALUES ('{req['nome']}','{req['data']}','{req['hora_inicio']}','{req['hora_fim']}', '{req['descricao']}','{req['visitantes']}')"

        cursor.execute(sql)

        mydb.commit()

        if (200):
            agenda.agenda(req['nome'], req['data'],
                          req['hora_inicio'], req['hora_fim'], req['descricao'])
            print("Evento Criado com sucesso!")

        return redirect(url_for('eventos'))

    return render_template("novo_evento.html")

# Endpoint para mostrar todos os eventos


@app.route('/eventos', methods=['GET'])
def eventos():
    username = None

    #Verificando se a um usuário logado
    if 'username' in session:
        username = session['username']

    # Criação do cursor para executar comandos
    cursor = mydb.cursor()

    # Executando o comando SQL
    # cursor.execute('SELECT e.id, e.nome, data_evento, hora_inicio, hora_fim, descricao, count(evento_id), qtd_visitantes '
    #                + 'FROM eventos as e JOIN visitantes as v ON e.id = v.evento_id GROUP BY e.id')
    cursor.execute("SELECT * FROM eventos")

    # Recebendo os dados
    todos_eventos = cursor.fetchall()

    # # Caso o evento não possua nenhum visitante
    # if todos_eventos == []:

    #     cursor.execute('SELECT * FROM eventos')

    #     lista_eventos = cursor.fetchall()

    #     eventos = list()

    #     for evento in lista_eventos:

    #         eventos.append(
    #             {
    #                 'id': evento[0],
    #                 'nome': evento[1],
    #                 'data': evento[2],
    #                 'hora_inicio': evento[3],
    #                 'hora_fim': evento[4],
    #                 'descricao': evento[5],
    #                 'vagas': evento[6]
    #             }
    #         )

    #         cursor.close()

    #         return render_template("eventos.html", eventos=eventos, username=username)

    # Tratando os dados recebidos
    eventos = list()
    for evento in todos_eventos:
        eventos.append(
            {
                'id': evento[0],
                'nome': evento[1],
                'data': evento[2],
                'hora_inicio': evento[3],
                'hora_fim': evento[4],
                'descricao': evento[5],
                'vagas': evento[6]
            }
        )

    # Terminado a execução do cursor
    cursor.close()

    # Renderizando o template em html e atribuindo os dados a variável eventos
    return render_template("eventos.html", eventos=eventos, username=username)

# Endpoint de inscrição de visitantes recebendo o ID do evento


@app.route("/visitante/<id>", methods=['POST', 'GET'])
def visitante(id):

    # Caso a requisição for post, executa o processo de inscrição
    if request.method == 'POST':
        req = request.form

        cursor = mydb.cursor()

        cursor.execute(f"SELECT * FROM visitantes WHERE evento_id = {id}")

        resultados = cursor.fetchall()

        # Verificando no banco caso já exista o cpf cadastrado nessa visita
        for resultado in resultados:

            if req['cpf'] in resultado:

                # Caso o cpf já esteja cadastrado, renderiza o form.html com a mensagem
                return render_template("novo_visitante.html", msg='CPF já cadastrado nesse evento')

            # Caso o cpf não esteja cadastrado, executa a inscrição normalmente
            else:
                sql = f"INSERT INTO visitantes (nome, cpf, evento_id) VALUES ('{req['nome']}','{req['cpf']}','{id}')"
                cursor.execute(sql)
                mydb.commit()
                if (200):
                    print('Visitante adicionado com sucesso')
                    return redirect(url_for('eventos'))
                else:
                    return redirect(url_for('eventos'))

    # Renderiza o template com o formulário para inscrição
    return render_template("novo_visitante.html")


@app.route("/login", methods=['GET', 'POST'])
def login():

    if request.method == 'POST':
        
        erro_validacao =  render_template("login.html", msg='Usuario, Senha ou Matricula Incorretos!!')    
    
        req = request.form

        cursor = mydb.cursor()

        cursor.execute(f"SELECT usuario, senha, matricula FROM funcionarios WHERE matricula = '{req['matricula']}'")

        resultado = cursor.fetchall()
        
        if resultado != [None]:
            for dado in resultado:
                if req['usuario'] in dado:
                    if req['senha'] in dado:
                        session['username'] = req['usuario']
                        return redirect(url_for('eventos'))
                    else:
                        return erro_validacao
                else:
                    return erro_validacao
    
    return render_template("login.html")

@app.route("/funcionario", methods = ['GET','POST'])
def funcionario():
    if request.method == 'POST':
        req = request.form
        cursor = mydb.cursor()
        cursor.execute(f"INSERT INTO funcionarios (usuario, email, senha, matricula) VALUES ('{req['usuario']}','{req['email']}','{req['senha']}','{req['matricula']}')")
        mydb.commit()
        if (200):
            return render_template("login.html", msg = 'Funcionario Cadastrado com Sucesso!!')
        else:
            return render_template("funcionario.html", msg = 'Ocorreu um erro no cadastro do funcionário.')
    return render_template('funcionario.html')    

@app.route("/editar/<id>", methods = ['GET', 'POST'])
def editar_evento(id):

    cursor = mydb.cursor()
    
    cursor.execute(f"SELECT nome, data_evento, hora_inicio, hora_fim, descricao, qtd_visitantes FROM eventos WHERE id = {id}")
    
    resultados = cursor.fetchall()
    
    evento = list()
    
    for resultado in resultados:
        evento.append(
            {
                "nome" : resultado[0],
                "data_evento" : resultado[1],
                "hora_inicio" : resultado[2],
                "hora_fim" : resultado[3],
                "descricao" : resultado[4],
                "visitantes" : resultado[5]
            }
        )
        
        if request.method == 'POST' and request.form['_method'] == 'patch':
            req = request.form
            cursor.execute(f"UPDATE eventos SET nome = '{req['nome']}', data_evento = '{req['data']}', hora_inicio = '{req['hora_inicio']}', hora_fim = '{req['hora_fim']}', descricao = '{req['descricao']}', qtd_visitantes = '{req['visitantes']}' ")
            mydb.commit()
            if(200):
                return redirect(url_for('eventos'))
            else:
                render_template('editar_evento.html', msg = 'Não foi possível alterar o evento')
                
        return render_template('editar_evento.html', evento = evento)
    
@app.route('/deletar/<id>', methods=['GET','POST'])
def deletar_evento(id):
    if request.method == 'POST':
        req = request.form
        
        cursor = mydb.cursor()
        cursor.execute(f"SELECT matricula FROM funcionarios WHERE matricula = '{req['matricula']}'")
        verificacao = cursor.fetchall()
        if verificacao == []:
            return render_template("verificacao.html", msg = 'Matrícula Inválida')
        else:
            cursor.execute(f"DELETE FROM eventos WHERE id = {id}")
            mydb.commit()
            return redirect(url_for('eventos'))
        
            
    return render_template("verificacao.html")
    

@app.route('/deslogar')
def logout():
    session.pop('username', None)
    return redirect(url_for('eventos'))




# Executando o aplicativo
if __name__ == '__main__':
    app.run()
