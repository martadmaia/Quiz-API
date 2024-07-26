import sqlite3
from os.path import isfile

def connect_db(dbname):
    """
    Estabelece conexão com base de dados, dado nome da mesma.
    Se base de dados não existir, é executado um ficheiro sql para a criação e inserção de dados na mesma.

    Args:
    - dbname (str): nome da base de dados.

    Return:
    - connection (Connection): conexão à base de dados.
    """
    db_is_created = isfile(dbname)  # Existe ficheiro da base de dados?
    connection = sqlite3.connect("kuko.db")
    cursor = connection.cursor()
    if not db_is_created:
        with open("schema.sql", "r") as sql_file:
            sql_script = sql_file.read()

        cursor.executescript(sql_script)
        connection.commit()
    return connection

