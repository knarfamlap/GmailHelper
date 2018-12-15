from flask import Flask
from flask import render_template
from quickstart import messageSnippets

app = Flask(__name__)

print(len(messageSnippets))

@app.route('/')
def main_page(message = messageSnippets):
    #rendering messages snippets
    return render_template('messages.html', message=message)
