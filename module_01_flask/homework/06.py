import os
import random
import re
from flask import Flask

app = Flask(__name__)

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
BOOK_FILE = os.path.join(BASE_DIR, 'war_and_peace.txt')

def load_words():
    with open(BOOK_FILE, 'r', encoding='utf-8') as file:
        text = file.read()
        words = re.findall(r'\b[а-яА-Яa-zA-Z]+\b', text)
        return [word for word in words if word]

words_list = load_words()

@app.route('/get_random_word')
def get_random_word():
    if words_list:
        random_word = random.choice(words_list)
        return f"Случайное слово: {random_word}"
    else:
        return "Слова не найдены"

if __name__ == '__main__':
    app.run(debug=True)