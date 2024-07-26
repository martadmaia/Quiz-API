from flask import Flask, request, g
from kuko_data import Kuko
import ssl
from utils import *
from kazoo.client import KazooClient
from setup_db import connect_db

app = Flask(__name__)

zh = KazooClient(hosts='127.0.0.1:2181')

#Métodos para criar/gerir nós Zookeeper

def create_quiz_node(quiz_id):
    """
    Cria um nó quiz, com o identificador do mesmo. Clientes registados neste quiz serão notificados quando se passa à próxima questão.
    """
    zh.ensure_path(f"/quiz/{quiz_id}")

def watch_quiz_node(id_quiz):
    @zh.DataWatch(f"/quiz/{id_quiz}")
    def watch_quiz_node(data, stat, event):
        if event and event.type == 'CHANGED':
            participant_nodes = zh.get_children(f"/quiz/{id_quiz}/participants")
            for participant in participant_nodes:
                print(f"NEXT was called on Quiz. Notification sent to {participant}.")

#Métodos para gerir a ligação à bd

@app.teardown_appcontext
def close_connection(exception):
    """
    Encerrra conexão à base de dados, se esta existir.
    """
    db = getattr(g, "_database", None)
    if db is not None:
        db.close()

def get_db():
    """
    Devolve conexão à base de dados. Se esta ainda não existir no contexto da aplicação, estabelece conexão.
    """
    if "db" not in g:
        g.db = connect_db("kuko.db")

    return g.db

def query_db(query, args=(), one=False):
    """
    Função auxiliar para executar queries na bd.
    Args:
    -query (str): query a executar
    -args (tuple): tuplo com argumentos a passar à query
    """
    cursor = get_db().execute(query, args)
    res = cursor.fetchall()
    cursor.close()
    return (res[0] if res else None) if one else res

#Inicialização de Kuko, que vai comunicar com a bd
kd = Kuko(query_db)

# Rotas da app
@app.get("/")
def home_route():
    return "Welcome to KuKo."

@app.get("/question/<int:id_question>")
def get_question(id_question):
    """
    Rota para aceder à informação (devolve pergunta em si) de uma pergunta com um dado identificador.
    """
    # Como não é uma rota acessível pelo cliente, não faço validação de argumentos.
    # Só id_question é que é relevante, e o seu cast para int já é validado.

    print(f"RECEIVED GET REQUEST at {request.url}")

    question = kd.get_registered_question(id_question)

    if question:
        return return_error_success_msg(detail=GET_QUESTION_SUCESS, code=200, param=question[0])

    else:
        return return_error_success_msg(descriptor=NOT_FOUND_URL, code=404, title=NOT_FOUND_TITLE, detail=ERROR_QUESTION_ID_DOES_NOT_EXIST)

@app.post("/question")
def add_question():
    """ 
    Rota para adicionar uma questão à base de dados. Devolve o identificador da nova questão.
    """
    print(f"RECEIVED POST REQUEST at {request.url}")

    args = request.json

    if len(args) == 4:  # Argumentos corretos

        question = args.get("question")  # pergunta - string
        answers = args.get("answers")  # lista de respostas - list[str]

        try:
            right_answer = int(args.get("right_answer"))  # right_answer - str cast para int
            int(args.get("client_id"))

        except ValueError:
            return return_error_success_msg(descriptor=BAD_REQUEST_URL, title=BAD_REQUEST_TITLE, code=400, detail=POST_QUESTION_INTS_ERROR)

        try:
            list(answers) #tentamos fazer cast para lista, caso não dê, enviamos código 400
        except ValueError:

            return return_error_success_msg(descriptor=BAD_REQUEST_URL, title=BAD_REQUEST_TITLE, code=400, detail=POST_QUESTION_LIST_ERROR)

        success = kd.add_new_question(question, answers, right_answer)

        if success:
            get_db().commit()  # commit das alterações na db

            return return_error_success_msg(code=200, detail=POST_QUESTION_SUCCESS, param=success[0])

        else:
            # Resposta certa indicada fora do [intervalo 1, nrº de respostas dadas]
            return return_error_success_msg(descriptor=BAD_REQUEST_URL,title=BAD_REQUEST_TITLE, code=400, detail=POST_QUESTION_K_ERROR)

    else:
        return return_error_success_msg(descriptor=BAD_REQUEST_URL,title=BAD_REQUEST_TITLE, code=400, detail=BAD_REQUEST_PARAMS)

@app.post("/qset")
def add_qset():
    """
    Rota para adicionar um qset à base de dados. Devolve o identificador do novo qset, bem como os identificadores das perguntas que o compõem.
    """
    print(f"RECEIVED POST REQUEST at {request.url}")
    args = request.json

    if len(args) == 2:

        questions = args.get("questions")  # identificadores das questões - list[str]

        try:
            [int(x) for x in questions]
        except ValueError:
            return return_error_success_msg(descriptor=BAD_REQUEST_URL, title=BAD_REQUEST_TITLE, code=400, detail=POST_QSET_LIST_ERROR)

        success = kd.add_new_question_set(questions)

        if success:
            get_db().commit()

            return return_error_success_msg(detail=POST_QSET_SUCCESS, code=200, param=str(success[0]) + "\nQSet questions: " + ";".join(questions))

        else:
            return return_error_success_msg(descriptor=BAD_REQUEST_URL,title=BAD_REQUEST_TITLE, code=400, detail=POST_QSET_IDS_DONT_EXIST)

    else:
        return return_error_success_msg(descriptor=BAD_REQUEST_URL,title=BAD_REQUEST_TITLE, code=400, detail=BAD_REQUEST_PARAMS)

@app.get("/quiz/<int:id_quiz>")
def get_quiz_status(id_quiz):
    """
    Rota para aceder ao estado de um quiz existente na base de dados.
    """
    print(f"RECEIVED GET REQUEST at {request.url}")

    quiz_status = kd.get_quiz_status(id_quiz)

    if quiz_status:
        return return_error_success_msg(
            detail=GET_QUIZ_STATUS_SUCCESS, code=200, param=quiz_status[0]
        )

    else:
        return return_error_success_msg(descriptor=NOT_FOUND_URL, code=404, title=NOT_FOUND_TITLE, detail=GET_QUIZ_STATUS_ERROR)

@app.post("/quiz")
def add_quiz():
    """
    Rota para adicionar um quiz à base de dados. Devolve o identificador do novo quiz.
    """
    print(f"RECEIVED POST REQUEST at {request.url}")
    args = request.json

    if len(args) == 3:

        qset_id = args.get("qset_id")
        scores = args.get("scores")

        try:
            int(qset_id)
            [int(score) for score in scores]
        except ValueError:
            return return_error_success_msg(descriptor = BAD_REQUEST_URL, code = 400, title = BAD_REQUEST_TITLE, detail=POST_QUIZ_INTS_ERROR)

        success = kd.add_new_quiz(qset_id, scores)

        # Quando há erro, devolve-se False, e uma mensagem de erro
        # Quando não há erro, devolve-se identificador do novo quiz e o seu state
        # Sempre um tuplo com 2 elementos
        if success[0]:
            get_db().commit()
            create_quiz_node(success[0][0]) #Criamos znode, que será watched pelos participantes
            # print("Nó criado", zh.get(f"/quiz/{success[0][0]}"))
                
            return return_error_success_msg(detail=POST_QUIZ_SUCCESS, param=success[0][0], code=200)
        else:
            return return_error_success_msg(descriptor=BAD_REQUEST_URL, code=400, title=BAD_REQUEST_URL, detail=success[1])

    else:
        return return_error_success_msg(descriptor=BAD_REQUEST_URL, title=BAD_REQUEST_TITLE, detail=BAD_REQUEST_PARAMS, code=400)

@app.post("/launch/<int:id_quiz>")
def launch_quiz(id_quiz):
    """
    Rota para "lançar" um dado quiz, isto é, mudar o seu estado para "ONGOING" (altera registo deste quiz na base de dados).
    """
    print(f"RECEIVED POST REQUEST at {request.url}")
    args = request.json

    if len(args) == 1:

        success = kd.launch_quiz(id_quiz)

        if success:
            get_db().commit()

            return return_error_success_msg(code=200, detail=POST_LAUNCH_QUIZ_SUCCESS)

        else:
            return return_error_success_msg(descriptor=NOT_FOUND_URL, code=404, title=NOT_FOUND_TITLE, detail=GET_QUIZ_STATUS_ERROR)

    else:
        return return_error_success_msg(descriptor=BAD_REQUEST_URL, title=BAD_REQUEST_TITLE, detail=BAD_REQUEST_PARAMS, code=400)

@app.post("/next/<int:id_quiz>")
def go_to_next_question(id_quiz):
    """
    Rota para avançar para a próxima pergunta num dado quiz.
    """
    print(f"RECEIVED POST REQUEST at {request.url}")
    args = request.json

    if len(args) == 1:  # Só é passado no body do request client_id

        success = kd.go_to_next_question(id_quiz)

        if len(success) == 2:
            if success[0] and "questions" in success[1]: #No more questions
                get_db().commit() #commit pq passámos estado para ended e alterámos timestamp_e
                zh.set(f"/quiz/{id_quiz}", "rel".encode()) #alteramos valor de data do node quiz/id_quiz para rel - isto é, já não tem mais perguntas, e participantes devem pedir o relatório
                # print("Nó depois de mudarmos data", zh.get(f"/quiz/{id_quiz}"))

                return return_error_success_msg(detail=POST_NEXT_SUCCESS_NO_MORE_QUESTIONS, code=200)
            else:
                if "database" in success[1]:
                    return return_error_success_msg(descriptor=NOT_FOUND_URL, code=404, title=NOT_FOUND_TITLE, detail=GET_QUIZ_STATUS_ERROR)
                else:
                    return return_error_success_msg(descriptor=BAD_REQUEST_URL, code=400, title=BAD_REQUEST_TITLE, detail=NEXT_ERROR)
            
        elif success[0]: #tem mais perguntas
            get_db().commit()
            
            zh.set(f"/quiz/{id_quiz}", "next".encode()) #alteramos data para next - participantes devem pedir pergunta atual
            # print("Nó depois de mudarmos data", zh.get(f"/quiz/{id_quiz}"))
            
            return return_error_success_msg(detail=POST_NEXT_SUCCESS_QUESTION, code=200)
        
            
    else:
        return return_error_success_msg(descriptor=BAD_REQUEST_URL, title=BAD_REQUEST_TITLE, detail=BAD_REQUEST_PARAMS, code=400)

@app.post("/reg/<int:id_quiz>")
def add_participant(id_quiz):
    """
    Rota para adicionar participante a dado quiz. Retorna participantes inscritos neste.
    """
    print(f"RECEIVED POST REQUEST at {request.url}")
    args = request.json

    if len(args) == 1:

        participant_id = args.get("client_id")

        try:
            int(participant_id)
        except ValueError:
            return return_error_success_msg(descriptor = BAD_REQUEST_URL, code = 400, title = BAD_REQUEST_TITLE, detail=POST_REG_INTS_ERROR)

        success = kd.register_participant(id_quiz, participant_id)

        if success[0]:
            get_db().commit()
            
            return return_error_success_msg(detail=POST_REG_SUCCESS, code=200, param=success[1])
        else:
            if "database" in success[1]:
                return return_error_success_msg(descriptor=NOT_FOUND_URL, code=404, title=NOT_FOUND_TITLE, detail=GET_QUIZ_STATUS_ERROR)
            else:
                return return_error_success_msg(descriptor = BAD_REQUEST_URL, code = 400, title = BAD_REQUEST_TITLE, detail=success[1])
            
    else:
        return return_error_success_msg(descriptor=BAD_REQUEST_URL, title=BAD_REQUEST_TITLE, detail=BAD_REQUEST_PARAMS, code=400)

@app.get("/get/<int:id_quiz>")
def get_current_question(id_quiz):
    """
    Rota para aceder à pergunta atual de um dado quiz ONGOING.
    """
    print(f"RECEIVED GET REQUEST at {request.url}")
    participant_id = request.args.get("client_id")

    try:
        int(participant_id)
    except ValueError:
        return return_error_success_msg(descriptor = BAD_REQUEST_URL, code = 400, title = BAD_REQUEST_TITLE, detail=POST_REG_INTS_ERROR)

    if participant_id:

        success = kd.get_current_question(id_quiz, participant_id)

        if success[0]:
            return return_error_success_msg(detail=GET_CURRENT_QUESTION_SUCCESS, code=200, param=success[1][0])
        else:
            if "database" in success[1]:
                return return_error_success_msg(descriptor=NOT_FOUND_URL, code=404, title=NOT_FOUND_TITLE, detail=GET_QUIZ_STATUS_ERROR)
            else:
                return return_error_success_msg(descriptor = BAD_REQUEST_URL, code = 400, title = BAD_REQUEST_TITLE, detail=success[1])
    else:
        return return_error_success_msg(descriptor=BAD_REQUEST_URL, title=BAD_REQUEST_TITLE, detail=BAD_REQUEST_PARAMS, code=400)

@app.post("/ans/<int:id_quiz>")
def answer_question(id_quiz):
    """
    Rota para responder à pergunta atual de um dado quiz.
    """
    print(f"RECEIVED POST REQUEST at {request.url}")
    args = request.json

    participant_id = args.get("client_id")
    try:
        answer_given = int(args.get("answer_given"))
        int(participant_id)
    except ValueError:
        return return_error_success_msg(descriptor = BAD_REQUEST_URL, code = 400, title = BAD_REQUEST_TITLE, detail=POST_ANS_INTS_ERROR)

    if len(args) == 2:

        success = kd.answer_question(id_quiz, answer_given, participant_id)

        if success[0]:
            get_db().commit()

            return return_error_success_msg(detail=POST_ANS_SUCCESS, code=200, param=success[-1])
        else:
            if "database" in success[1]:
                return return_error_success_msg(descriptor=NOT_FOUND_URL, code=404, title=NOT_FOUND_TITLE, detail=GET_QUIZ_STATUS_ERROR)
            else:
                return return_error_success_msg(descriptor = BAD_REQUEST_URL, code = 400, title = BAD_REQUEST_TITLE, detail=success[1])
    else:
        return return_error_success_msg(descriptor=BAD_REQUEST_URL, title=BAD_REQUEST_TITLE, detail=BAD_REQUEST_PARAMS, code=400)

@app.get("/rel/<int:id_quiz>")
def get_quiz_report(id_quiz):
    """
    Rota para aceder ao relatório do quiz - isto é, prestação de todos os participantes inscritos no mesmo.
    """
    print(f"RECEIVED GET REQUEST at {request.url}")
    success = kd.get_quiz_report(id_quiz)

    if success[0]:
        return return_error_success_msg(detail=GET_REL_SUCCESS, code=200, param=success[1])
    else:
        if "database" in success[1]:
                return return_error_success_msg(descriptor=NOT_FOUND_URL, code=404, title=NOT_FOUND_TITLE, detail=GET_QUIZ_STATUS_ERROR)
        else:
                return return_error_success_msg(descriptor = BAD_REQUEST_URL, code = 400, title = BAD_REQUEST_TITLE, detail=success[1])


if __name__ == "__main__":
    context = ssl.SSLContext(protocol=ssl.PROTOCOL_TLS_SERVER)
    context.verify_mode = ssl.CERT_REQUIRED
    context.load_verify_locations(cafile='root.pem')
    context.load_cert_chain(certfile='./server/serv.crt',keyfile='./server/serv.key')
    zh.start()
    
    app.run('localhost', ssl_context=context)
    
try:
    zh.close()
except Exception as e:
    print("Something wrong when closing Zookeeper connection...", e)

