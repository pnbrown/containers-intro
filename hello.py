from flask import Flask, flash, redirect, render_template, request, session, abort
from random import choice
import json

app = Flask(__name__)

def read_quotes(filename):
    with open('quotes.txt') as f:
        lines = (l.strip() for l in f)
        return [json.loads(l) for l in lines if l]

@app.route("/")
def index():
    return "Nigel's Container Intro Workshop. Append /hello/$your_name to the url."

# @app.route("/hello/<string:name>")
@app.route("/hello/<string:name>/")
def hello(name):
    quotes = read_quotes('quotes.txt')
    authors = list(set(author for _, author in quotes))
    quote, _ = choice(quotes)
    author = choice(authors)
    return render_template(
        'view.html', **locals())

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=80)
