#Suprimir este erro:
# /usr/lib/python3/dist-packages/urllib3/connection.py:455: SubjectAltNameWarning: Certificate for localhost has no `subjectAltName`, falling back to check for a `commonName` for now. This feature is being removed by major browsers and deprecated by RFC 2818. (See https://github.com/urllib3/urllib3/issues/497 for details.)
#   warnings.warn(
import urllib3
urllib3.disable_warnings(urllib3.exceptions.SubjectAltNameWarning)

import sys
from kuko_stub import *

COMMANDS_CODES_MAP = {
    "QUESTION": [10, 5],
    "QSET": [20, 2],
    "QUIZ": [30, 3],
    "LAUNCH": [40, 2],
    "NEXT": [50, 2],
    "REG": [60, 2],
    "GET": [70, 2,],
    "ANS": [80, 3],
    "REL": [90, 2],
    "GET_QUESTION": [100, 2],
    "GET_QUIZ_STATUS": [110, 2]
}

def validate_input(input):
    """
    Valida estrutura do input dado e dados passados.
    Args:
    - input (str) : pedido enviado pelo cliente
    """
    input_split = input.strip("\n").strip().split(";")
     # Se o pedido vier mal estruturado, não irá passar na seguinte validação - número de elementos do pedido

    # Para verificar se são passados, no mínimo, os argumentos necesssários no comando

    if input_split[0] in COMMANDS_CODES_MAP:
        if len(input_split) < COMMANDS_CODES_MAP[input_split[0]][-1]:
            return False
    else:
        return False

    # Verificações específicas para cada comando
    match input_split[0]:
        case "QUESTION" | "LAUNCH" | "REG" | "GET" | "NEXT" | "REL" | "GET_QUESTION" | "GET_QUIZ_STATUS":
            # Verificamos se podemos fazer cast para int, ou seja, se são passados inteiros válidos como ids, etc.
            try:
                n = int(input_split[-1])
            except ValueError:
                return False
        case "QSET" | "QUIZ" | "ANS":
            try:
                n = [int(id) for id in input_split[1:]]
            except ValueError:
                return False

    return True

### código do programa principal ###
def main():
    
    id_client = int(sys.argv[1])
    # Crio instância de kuko_stub - esta fará os requests
    client_cert = ("./client/cli.crt", "./client/cli.key")
    client_stub = KukoStub("localhost", 5000, client_cert, id_client)
    
    while True:
        try:
            input_user = input("comando > ")
        except EOFError:
            # Para quando lemos os comandos de um ficheiro
            break 

        if input_user == "EXIT":
            break
        elif not validate_input(input_user):
            print("Invalid Input...")
            continue

        input_split = input_user.strip("\n").strip().split(";")

        #Consoante o comando: determino o método correspondente no stub, crio uma lista com o código correspondente e os argumentos necessários.
        actions_map = {
            "QUESTION": (
                client_stub.post_question,
                [  # código comando
                    input_split[1],  # pergunta
                    input_split[2:-1],  # respostas
                    input_split[-1],  # resposta certa
                    id_client,
                ],
            ),
            "QSET": (
                client_stub.qset,
                [
                    input_split[1:],  # perguntas do set
                    id_client,
                ],
            ),
            "QUIZ": (
                client_stub.quiz,
                [
                    input_split[1],  # id do qset
                    input_split[2:],  # pontuações
                    id_client,
                ],
            ),
            "LAUNCH": (
                client_stub.launch,
                [
                    input_split[-1],  # id do quiz
                    id_client,
                ],
            ),
            "NEXT": (
                client_stub.next,
                [
                    input_split[-1],  # id do quiz
                    id_client,
                ],
            ),
            "REG": (
                client_stub.reg,
                [
                    input_split[-1],  # id do quiz
                    id_client,
                ],
            ),
            "GET": (
                client_stub.get,
                [
                    input_split[-1],  # id do quiz
                    id_client,
                ],
            ),
            "ANS": (
                client_stub.ans,
                [
                    input_split[1],  # id do quiz
                    input_split[-1],  # resposta dada
                    id_client,
                ],
            ),
            "REL": (
                client_stub.rel,
                [
                    input_split[-1],  # id do quiz
                    id_client,
                ],
            ),
            "GET_QUESTION": (
                client_stub.get_question,
                [
                    input_split[-1],  # id da questão
                    id_client,
                ],
            ),
            "GET_QUIZ_STATUS": (
                client_stub.get_quiz_status,
                [
                    input_split[-1],  # id do quiz
                    id_client,
                ],
            ),

        }

        func, params = actions_map[input_split[0]]
        response = func(*params)

    client_stub.close_zh()


if __name__ == "__main__":
    main()
