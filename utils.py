from flask import jsonify

def return_error_success_msg(descriptor = None, code = None, title = None, detail = None, param = None):
    
    if not descriptor and detail:
        msg = {
            "message": f"{detail}{param if param else ''}",
            "httpStatus": code
        }
    else:
        msg = {
            "describedBy": descriptor,
            "httpStatus": code,
            "title": title,
            "detail": detail
        }

    print("SENT", msg)
    return jsonify(msg), code

NOT_FOUND_URL = "http://example.com/notfound"

NOT_FOUND_TITLE = "NOT FOUND"

INTERNAL_SERVER_ERROR_URL = "http://example.com/internalservererror"

INTERNAL_SERVER_ERROR_TITLE = "INTERNAL SERVER ERROR"

BAD_REQUEST_URL = "http://example.com/badrequest"

BAD_REQUEST_TITLE = "BAD REQUEST"

ERROR_QUESTION_ID_DOES_NOT_EXIST = "Question with given id does not exist in the database."

INTERNAL_SERVER_ERROR = "Something went wrong retrieving the information."

GET_QUESTION_SUCESS = "Question successfully retrieved from database.\nQuestion Info: "

POST_QUESTION_SUCCESS = "Question successfully added to the database.\nQuestion ID: "

POST_QUESTION_ERROR_CODE = "Invalid data submitted (command code to add a question must be 10)",

POST_QUESTION_INTS_ERROR = "Invalid data submitted (right answer must be a number between 1 and the number of possible answers given. Client id must be a positive integer)."

POST_QUESTION_LIST_ERROR = "Invalid data submitted (possible answers must be a list)."

POST_QUESTION_K_ERROR = "Invalid data submitted (right answer must be a number between 1 and the number of possible answers given)."

BAD_REQUEST_PARAMS = "Insufficient parameters."

POST_QSET_SUCCESS = "QSet successfully added to the database.\nQSet ID: "

POST_QSET_ERROR_CODE = "Invalid data submitted (command code to add a qset must be 20)",

POST_QSET_LIST_ERROR = "Invalid data submitted. Field - questions to add to qset - must be a list of valid question ids - integers)."

POST_QSET_IDS_DONT_EXIST = "Invalid data submitted (given question IDS don't correspond to existing data in the database)."

GET_QUIZ_STATUS_SUCCESS = "Successfully retrieved quiz information from database.\nQuiz status: "

GET_QUIZ_STATUS_ERROR = "Quiz with given id does not exist in the database."

POST_QUIZ_SUCCESS = "Quiz successfully added to the database.\nQuiz ID: "

POST_QUIZ_ERROR_CODE = "Invalid data submitted (command code to add a quiz must be 30)",

POST_QUIZ_INTS_ERROR = "Invalid parameters. Scores passed and qset id must be integers."

POST_LAUNCH_ERROR_CODE = "Invalid data submitted (command code to launch a quiz must be 40)"

POST_LAUNCH_QUIZ_SUCCESS = "Quiz successfully launched."

POST_NEXT_ERROR_CODE = "Invalid data submitted (command code to launch a quiz must be 50)"

POST_NEXT_SUCCESS_NO_MORE_QUESTIONS = "Quiz has no more questions. Changed status to ENDED"

POST_NEXT_SUCCESS_QUESTION = "Sucessfully advanced to next question."

POST_REG_CODE_ERROR = "Invalid data submitted (command code to launch a quiz must be 60)"

POST_REG_INTS_ERROR = "Invalid parameters. Client id must be integer."

POST_REG_SUCCESS = "Participant successfully added to quiz.\nParticipants: "

GET_CURRENT_QUESTION_SUCCESS = "Sucessfully retrieved quiz's current question.\nCurrent Question: "

POST_ANS_INTS_ERROR = "Answer given and client id must be integers."

POST_ANS_CODE_ERROR = "Invalid data submitted (command code to launch a quiz must be 80)"

POST_ANS_SUCCESS = "Sucessfully registered answer.\nCorrect answer? "

GET_REL_SUCCESS = "Sucessfully retrieved report.\nScores: "

GET_QSET_QUESTIONS_SUCCESS = "Successfully retrieved qset questions.Questions: "

GET_QSET_QUESTIONS_ERROR = "Qset with given ID doesn't exist in database."

NEXT_ERROR = "Quiz is currently not ongoing"