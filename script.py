from flask import Flask
from flask import render_template
from quickstart import main

app = Flask(__name__)


messageSnippets = main()
@app.route('/')
def main_page(messageList = messageSnippets):
    #rendering messages snippets
    return render_template('messages.html', messageList=messageList)
