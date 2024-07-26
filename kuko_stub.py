import requests
from kazoo.client import KazooClient

class KukoStub:

    def __init__(self, localhost, port, cert, client_id):
        """
        Cria instância de KukoStub. Guarda endereço e porto da aplicação para onde serão enviados os pedidos.
        Args:
        - localhost(str): endereço do servidor
        - port(str): porto
        - cert (tuple): tuplo com chaves ssl
        - client_id (int): identificador do cliente
        """
        self.host = localhost
        self.port = port
        self.cert = cert
        self.client_id = client_id
        self.zh = KazooClient(hosts='127.0.0.1:2181')

        self.zh.start()

    def handle_notif(self, data, stat, event):
        """
        Função callback quando se recebe uma notificação de mudança num nó quiz em que o participante está inscrito. Consoante o valor da mudança, efetua pedido na rota /get ou /rel, para receber a pergunta atual do quiz ou o relatório do mesmo, respetivamente.
        """
        print("Received notification. Change in znode...")
        data = data.decode()
        if event and data:
            if data == "next":
                print("Requesting new question...")
                self.get(event.path.split("/")[-1], self.client_id)
            elif data == "rel":
                print("Requesting quiz report...")
                self.rel(event.path.split("/")[-1], self.client_id)

    def add_participant(self, id_quiz, participant_id):
        """
        Cria nó participante - filho de um dado quiz - para receber notificações quando se altera o nó quiz.

        Args:
        - id_quiz (int): identificador do quiz
        - participant_id (int): identificador do participante
        """
        self.zh.ensure_path(f"/quiz/{id_quiz}/participants/{participant_id}")
        self.zh.DataWatch(f"/quiz/{id_quiz}", func=self.handle_notif)
        print("Nó criado", self.zh.get(f"/quiz/{id_quiz}/participants/{participant_id}"))
        print("Fihos - participantes registados no quiz", self.zh.get_children(f"/quiz/{id_quiz}/participants"))
    
    def close_zh(self):
        """
        Encerra client Kazoo
        """
        self.zh.close()
    
    def post_question(self, question, answers, right_answer, client_id):
        """
        Formula o pedido a enviar ao servidor para criação de uma pergunta. Cria um pedido POST para a route /question, com os parâmetros necessários à criação de uma pergunta.
        Args:
        - question(str): pergunta
        - answers(list(str)): respostas possíveis à pergunta
        - right_answer(str): resposta certa
        - client_id(int): id do cliente
        """
        # Parâmetros
        params = {
            "question": question,
            "answers": answers,
            "right_answer": right_answer,
            "client_id": client_id,
        }

        try:
            r = requests.post("https://localhost:5000/question", json=params, verify='root.pem', cert=self.cert)
            print("POSTED", params, "to", r.url)
            
            response = r.json()
            print("SERVER RESPONSE:", response)

        except requests.exceptions.JSONDecodeError as e:
            print("Coudn't decode message.\nError:", e)
        except requests.exceptions.RequestException as e:
            print("An error occurred.\nError:", e)

    def qset(self, questions, client_id):
        """
        Formula o pedido a enviar ao servidor para criação de um qset. Cria um pedido POST para a route /qset, com os parâmetros necessários à criação de um qset.
        Args:
        - questions(list(str)): ids das perguntas a associar ao qset
        - client_id(int): id do cliente
        """
        params = { 
            "questions": questions, 
            "client_id": client_id
            }
        
        try:
            r = requests.post("https://localhost:5000/qset", json=params, verify='root.pem', cert=self.cert)
            print("POSTED", params, "to", r.url)
            
            response = r.json()
            print("SERVER RESPONSE:", response)

        except requests.exceptions.JSONDecodeError as e:
            print("Coudn't decode message.\nError:", e)
        except requests.exceptions.RequestException as e:
            print("An error occurred.\nError:", e)

    def quiz(self, qset_id, scores, client_id):
        """
        Formula o pedido a enviar ao servidor para criação de um quiz. Cria um pedido POST para a route /quiz, com os parâmetros necessários à criação de um quiz.
        Args:
        - qset_id(str): id do qset a associar ao quiz
        - scores(list(str)): pontuações a atribuir às perguntas associadas ao qset
        - client_id(int): id do cliente
        """
        params = { 
            "qset_id": qset_id, 
            "scores": scores,
            "client_id": client_id
            }
        
        try:
            r = requests.post("https://localhost:5000/quiz", json=params, verify='root.pem', cert=self.cert)
            print("POSTED", params, "to", r.url)
            
            response = r.json()
            print("SERVER RESPONSE:", response)

        except requests.exceptions.JSONDecodeError as e:
            print("Coudn't decode message.\nError:", e)
        except requests.exceptions.RequestException as e:
            print("An error occurred.\nError:", e)

    def launch(self, quiz_id, client_id):
        """
        Formula o pedido a enviar ao servidor para lançar um quiz. Cria um pedido POST para a route /launch/, com os parâmetros necessários à criação de um quiz.
        Args:
        - quiz_id(str): id do quiz a lançar
        - client_id(int): id do cliente
        """
        params = {
            "client_id": client_id
            }

        try:
            r = requests.post(f"https://localhost:5000/launch/{quiz_id}", json=params, verify='root.pem', cert=self.cert)
            print("POSTED", params, "to", r.url)
            
            response = r.json()
            print("SERVER RESPONSE:", response)

        except requests.exceptions.JSONDecodeError as e:
            print("Coudn't decode message.\nError:", e)
        except requests.exceptions.RequestException as e:
            print("An error occurred.\nError:", e)
    
    def next(self, quiz_id, client_id):
        """
        Formula o pedido a enviar ao servidor para passar à próxima pergunta num quiz. Cria um pedido POST para a route /next/, com os parâmetros necessários para passar para a próxima questão do dado quiz.
        Args:
        - quiz_id(str): id do quiz
        - client_id(int): id do cliente
        """
        params = { 
            "client_id": client_id
        }

        try:
            r = requests.post(f"https://localhost:5000/next/{quiz_id}", json=params, verify='root.pem', cert=self.cert)
            print("POSTED", params, "to", r.url)
            
            response = r.json()
            print("SERVER RESPONSE:", response)

        except requests.exceptions.JSONDecodeError as e:
            print("Coudn't decode message.\nError:", e)
        except requests.exceptions.RequestException as e:
            print("An error occurred.\nError:", e)

    def reg(self, quiz_id, client_id):
        """
        Formula o pedido a enviar ao servidor para registar um participante num quiz. Cria um pedido POST para a route /reg/, com os parâmetros necessários para registar um participante num dado quiz.
        Args:
        - quiz_id(str): id do quiz
        - client_id(int): id do cliente
        """
        params = { 
            "client_id": client_id
            }
        
        try:
            r = requests.post(f"https://localhost:5000/reg/{quiz_id}", json=params, verify='root.pem', cert=self.cert)
            print("POSTED", params, "to", r.url)
            
            response = r.json()
            if r.status_code == 200:
                self.add_participant(quiz_id, client_id)
            print("SERVER RESPONSE:", response)

        except requests.exceptions.JSONDecodeError as e:
            print("Coudn't decode message.\nError:", e)
        except requests.exceptions.RequestException as e:
            print("An error occurred.\nError:", e)

    def get(self, quiz_id, client_id):
        """
        Formula o pedido a enviar ao servidor para obter a pergunta atual do quiz. Envia pedido GET.
        Args:
        - quiz_id(str): id do quiz
        - client_id(int): id do cliente
        """
        try:
            r = requests.get(f"https://localhost:5000/get/{quiz_id}?client_id={client_id}", verify='root.pem', cert=self.cert)
            print("REQUESTED", r.url)
            
            
            response = r.json()
            print("SERVER RESPONSE:", response)

        except requests.exceptions.JSONDecodeError as e:
            print("Coudn't decode message.\nError:", e)
        except requests.exceptions.RequestException as e:
            print("An error occurred.\nError:", e)

    def ans(self, quiz_id, answer_given, client_id):
        """
        Formula o pedido a enviar ao servidor para responder à pergunta atual de um quiz. Cria um pedido POST para a route /ans/, com os parâmetros necessários para registar uma resposta à pergunta atuak do dado quiz.
        Args:
        - quiz_id(str): id do quiz
        - answer_given(str): resposta dada pelo cliente
        - client_id(int): id do cliente
        """
        params = { 
            "answer_given": answer_given, 
            "client_id": client_id
            }
        
        try:
            r = requests.post(f"https://localhost:5000/ans/{quiz_id}", json=params, verify='root.pem', cert=self.cert)
            print("POSTED", params, "to", r.url)
            
            response = r.json()
            print("SERVER RESPONSE:", response)

        except requests.exceptions.JSONDecodeError as e:
            print("Coudn't decode message.\nError:", e)
        except requests.exceptions.RequestException as e:
            print("An error occurred.\nError:", e)

    def rel(self, quiz_id, client_id):
        """
        Formula o pedido a enviar ao servidor para receber o relatório final da prestação dos participantes de um dado quiz.
        Args:
        - quiz_id(str): id do quiz
        - client_id(int): id do cliente
        """

        try:
            r = requests.get(f"https://localhost:5000/rel/{quiz_id}?client_id={client_id}", verify='root.pem', cert=self.cert)
            print("REQUESTED", r.url)
            
            response = r.json()
            print("SERVER RESPONSE:", response)

        except requests.exceptions.JSONDecodeError as e:
            print("Coudn't decode message.\nError:", e)
        except requests.exceptions.RequestException as e:
            print("An error occurred.\nError:", e)
        
    def get_question(self, question_id, client_id):
        """
        Formula o pedido a enviar ao servidor para pesquisar uma questão existente.
        Args:
        - quiz_id(str): id da questão
        - client_id(int): id do cliente
        """
        try:
            r = requests.get(f"https://localhost:5000/question/{question_id}?client_id={client_id}", verify='root.pem', cert=self.cert)
            print("REQUESTED", r.url)
            
            response = r.json()
            print("SERVER RESPONSE:", response)

        except requests.exceptions.JSONDecodeError as e:
            print("Coudn't decode message.\nError:", e)
        except requests.exceptions.RequestException as e:
            print("An error occurred.\nError:", e)
    
    def get_quiz_status(self, quiz_id, client_id):
        """
        Formula o pedido a enviar ao servidor para obter o estado de um dado quiz.
        Args:
        - quiz_id(str): id da questão
        - client_id(int): id do cliente
        """
        try:
            r = requests.get(f"https://localhost:5000/quiz/{quiz_id}?client_id={client_id}", verify='root.pem', cert=self.cert)
            print("REQUESTED", r.url)
            
            response = r.json()
            print("SERVER RESPONSE:", response)

        except requests.exceptions.JSONDecodeError as e:
            print("Coudn't decode message.\nError:", e)
        except requests.exceptions.RequestException as e:
            print("An error occurred.\nError:", e)

