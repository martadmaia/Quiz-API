import time
from sqlite3 import IntegrityError

class Kuko:

    def __init__(self, query_function):
        self.query_db = query_function

    def get_registered_question(self, question_id):
        """
        Devolve questão existente na base de dados, dado um question_id.

        Args:
        - question_id (int): identificador da questão a procurar na BD

        Returns:
        - tuple: composto por descrição da questão e respostas possíveis
        """
        question_info =  self.query_db(
            "SELECT question, answers FROM question WHERE question.id_question = ?",
            (question_id,),
            one = True
        )

        return question_info

    def add_new_question(self, question, answers, right_answer):
        """
        Insere questão na base de dados. Retorna id da questão que foi inserida.

        Args:
        - question (str): questão dada
        - answers (list[str]): lista de respostas possíveis
        - right_answer (int): resposta certa

        Returns:
        - insert_id (int): identificador da questão que foi criada
        """
        if right_answer < 1 or right_answer > len(answers):
            return False
        else:
            # Inserimos na bd nova questão.
            self.query_db(
                "INSERT INTO question (question, answers, k) VALUES (?, ?, ?)",
                (question, ";".join(answers), right_answer)
            )
            insert_id = self.query_db("SELECT last_insert_rowid()", one=True)

            return insert_id

    def add_new_question_set(self, question_list):
        """
        Insere qset na base dados, dada uma lista de perguntas.

        Args:
        - question_list (list[str]): lista de identificadores de questões associadas ao qset

        Returns:
        - insert_id (int): identificador do qset que foi criado
        """
        # Verificamos se perguntas existem
        for question_id in question_list:
            if len(self.query_db("SELECT * FROM question WHERE question.id_question = ?",(question_id, ))) == 0: #questão não existe na bd
                return False

        # Inserimos qset na BD
        self.query_db(
            "INSERT INTO qset (questions) VALUES (?)",
            (";".join([str(i) for i in question_list]),),
        )
        insert_id = self.query_db("SELECT last_insert_rowid()", one = True)

        return insert_id

    def add_new_quiz(self, qset_id, scores_list):
        """
        Insere novo Quiz na base de dados.
        
        Args:
        - qset_id (str): identificador do qset
        - scores_list (list[str]): lista de pontuações associadas ao qset dado

        Returns:
        - insert_id (int): identificador do quiz que foi criado
        """
        # Vemos se qset existe na bd
        qset_info = self.query_db(
            "SELECT questions FROM qset WHERE qset.id_qset = ?", (qset_id, ), one = True
        )

        if not qset_info:
            return (False, "Qset doesn't exist in database")

        # Vemos se o nº de perguntas do qset, corresponde ao nº de scores dado
        if len(qset_info[0].split(";")) != len(scores_list):
            return (
                False,
                "Number of scores passed doesn't match number of questions in qset"
            )

        self.query_db(
            "INSERT INTO quiz (id_qset, points, timestamp_p) VALUES (?, ?, ?)",
            (qset_id, ";".join([str(i) for i in scores_list]), round(time.time()))
        ) 

        insert_id = self.query_db("SELECT last_insert_rowid()", one = True)

        return (insert_id, "PREPARED")

    def get_quiz_status(self, id_quiz):
        """
        Retorna estado de um dado quiz.

        Args:
        - id_quiz (int): identificador do quiz a procurar

        Returns:
        - quiz_status (str): estado do quiz
        """
        quiz_status = self.query_db("SELECT state FROM quiz WHERE id_quiz = ?", (id_quiz,), one = True)

        return quiz_status

    def launch_quiz(self, id_quiz):
        """
        Atualiza valor de atributo "state" de um dado quiz. Valor passa para "ONGOING".
        
        Args:
        - id_quiz(int): identificador do quiz
        """
        # Verificamos se quiz existe na bd
        if len(self.query_db("SELECT * FROM quiz WHERE id_quiz = ?", (id_quiz,))) == 0:
            return False

        self.query_db("UPDATE quiz SET state = 'ONGOING' WHERE id_quiz = ?", (id_quiz,))

        return True

    def register_participant(self, id_quiz, id_participant):
        """
        Atualiza os participantes de um quiz, na base de dados.
        
        Args:
        - id_quiz(int): identificador do quiz
        - id_participant(int): identificador do participante a registar

        Returns:
        - existing_participants (str): string com ids dos participantes atualizado
        """
        # Verificamos se quiz existe na bd
        quiz_info = self.query_db(
            "SELECT state, participants FROM quiz WHERE id_quiz = ?",
            (id_quiz,),
            one=True
        )

        if not quiz_info:
            return (False, "Quiz doesn't exist in the database.")

        # Verificamos se estado do quiz é PREPARED
        if quiz_info[0] != "PREPARED":
            return (False, "Quiz is not accepting new participants at this time.")

        # Adicionamos id do participante a participants
        existing_participants = quiz_info[1]

        if not existing_participants:
            existing_participants = str(id_participant)
        elif str(id_participant) in existing_participants:
            return (False, f"Participant is already registered in quiz {id_quiz}.")
        else:
            existing_participants += ";" + str(id_participant)

        self.query_db(
            "UPDATE quiz SET participants = ? WHERE id_quiz = ?",
            (existing_participants, id_quiz),
        )

        # Retornamos id do quiz e participantes inscritos
        return (id_quiz, existing_participants)

    def get_current_question(self, id_quiz, id_participant):
        """
        Retorna a pergunta atual do quiz.
        
        Args:
        - id_quiz(int): identificador do quiz
        - id_participant(int): identificador do participante

        Returns:
        - question_info (list[str]): lista com pergunta e respostas possíveis
        """
        # Verificamos se quiz existe na bd
        quiz_info = self.query_db(
            "SELECT q.state, q.id_qset, q.participants, q.question_i, qs.questions FROM quiz q JOIN qset qs ON q.id_qset = qs.id_qset WHERE q.id_quiz = ?",
            (id_quiz, ), one = True
        )

        if not quiz_info:
            return (False, "Quiz doesn't exist in the database.")

        # Verificamos se estado do quiz é ONGOING
        if quiz_info[0] != "ONGOING":
            return (False, "Quiz is currently not ongoing.")

        # Verificamos se partcipante está inscrito no quiz
        if quiz_info[2]:
            if str(id_participant) not in quiz_info[2]:
                return (False, "Participant is not registered in quiz.")
        else:
            return (False, "Participant is not registered in quiz.")

        question_info = self.query_db(
            "SELECT question, answers FROM question WHERE id_question = ?",
            (quiz_info[-1].split(";")[quiz_info[3]], )
        )

        return (True, question_info)

    def answer_question(self, id_quiz, answer, id_participant):
        """
        Regista resposta dada pelo participante. Atualiza base de dados. Retorna registo da resposta e se a mesma está correta ou não.
        
        Args:
        - id_quiz(int): identificador do quiz
        - answer(int): resposta dada pelo participante
        - id_participant(int): identificador do participante

        Returns:
        - str: string que indica se resposta está correta ou não
        """
        quiz_info = self.query_db("SELECT q.state, q.id_qset, q.participants, q.question_i, qs.questions FROM quiz q JOIN qset qs ON q.id_qset = qs.id_qset WHERE q.id_quiz = ?", (id_quiz, ), one=True)

        # Verificamos se quiz existe
        if not quiz_info:
            return (False, "Quiz doesn't exist in the database.")

        # Verificamos se estado do quiz é ONGOING
        if quiz_info[0] != "ONGOING":
            return (False, "Quiz is currently not ongoing.")

        # Verificamos se partcipante está inscrito no quiz
        if quiz_info[2]:
            if str(id_participant) not in quiz_info[2]:
                return (False, "Participant is not registered in quiz.")
        else:
            return (False, "Participant is not registered in quiz.")

        question_info = self.query_db(
            "SELECT answers, k FROM question WHERE id_question = ?",
            (quiz_info[-1].split(";")[quiz_info[3]], ), one=True)

        if answer > len(question_info[0].split(";")) or answer < 1:
            return (False, f"Invalid answer (answer must be number between 1 and {len(question_info[0])}).")
        
        try:
            self.query_db(
                "INSERT INTO results (id_quiz, question_i, participant, answer) VALUES (?, ?, ?, ?)",
                (id_quiz, quiz_info[3], id_participant, answer)
            )
        except IntegrityError:
            return (False, f"Participant {id_participant} has already registered an answer to this question.")

        return (True, "Correct" if answer == question_info[1] else "Incorrect")

    def go_to_next_question(self, id_quiz):
        """
        Avança para a próxima pergunta, caso esta exista. Atualiza registo de quiz, com id dado na base de dados. Se já não houverem mais perguntas, muda-se o estado do quiz para "ENDED". Devolve a próxima pergunta a ser respondida pelos participantes.
        
        Args:
        - id_quiz(int): id do quiz
        """
        quiz_info = self.query_db(
            "SELECT q.state, q.question_i, qs.questions FROM quiz q JOIN qset qs ON q.id_qset = qs.id_qset WHERE q.id_quiz = ?",
            (id_quiz, ), one = True)

        # Verificamos se quiz existe
        if not quiz_info:
            return (False, "Quiz doesn't exist in the database.")

        # Verificamos se estado do quiz é ONGOING
        if quiz_info[0] != "ONGOING":
            return (False, "Quiz is currently not ongoing.")

        # Verificamos se quiz já está na útlima pergunta
        if quiz_info[1] == len(quiz_info[-1].split(";")) - 1:
            self.query_db(
                "UPDATE quiz SET state = ? WHERE id_quiz = ?", ("ENDED", id_quiz)
            )
            return (True, "Quiz has no more questions")
        else:
            self.query_db(
                "UPDATE quiz SET question_i = ? WHERE id_quiz = ?",
                (quiz_info[1] + 1, id_quiz)
            )

            # Get da nova questão
            # question_info = self.query_db(
            #     "SELECT question, answers FROM question WHERE id_question = ?",
            #    ( quiz_info[-1].split(";")[quiz_info[1] + 1], ), one = True
            # )

            return (True,)

    def get_quiz_report(self, id_quiz):
        """
        Devolve relatório dos resultados de um quiz, incluindo as pontuações obtidas por cada participante do mesmo.
        
        Args:
        - id_quiz(int): identificador do quiz

        Returns:
        - scores (dict): dicionário em que chaves são ids dos participantes do quiz, e valores a sua pontuação no mesmo
        """
        quiz_info = self.query_db(
            "SELECT q.state, q.points, qs.questions, re.* FROM quiz q LEFT OUTER JOIN qset qs ON q.id_qset = qs.id_qset LEFT OUTER JOIN results re ON re.id_quiz = q.id_quiz WHERE q.id_quiz = ?",
            (id_quiz, ),
        )

        # Verificamos se quiz existe
        if not quiz_info:
            return (False, "Quiz doesn't exist in the database.")
        elif len(quiz_info) == 1 and quiz_info[0][-1] == None:
            return (False, "Quiz has no registered answers. Unable to calculate scores.")

        # Verificamos se estado do quiz é ONGOING
        if quiz_info[0][0] != "ENDED":
            return (False, "Quiz is ongoing.")

        scores = {}

        for result in quiz_info:
            question_right_answer = self.query_db(
                "SELECT k FROM question WHERE id_question = ?",
                (result[2].split(";")[result[4]], ), one = True
            )[0]

            if scores.get(result[5]):
                scores[result[5]] += int(result[1].split(";")[result[4]]) if question_right_answer == result[-1] else 0
                
            else:
                scores[result[5]] = int(result[1].split(";")[result[4]]) if question_right_answer == result[-1] else 0

        return (id_quiz, scores)