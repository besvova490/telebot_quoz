import base64
import requests

def get_questions():
    resp = requests.get(
        f'https://opentdb.com/api.php?amount=1&encode=base64'
    )
    question = resp.json()['results'][0]
    question_bloc = {
        'question': base64.b64decode(question["question"]).decode(),
        'correct_answer': base64.b64decode(question["correct_answer"]).decode(),
        'incorrect_answers': base64.b64decode(' '.join(question["incorrect_answers"])).decode().split()
    }
    return question_bloc

print(get_questions())