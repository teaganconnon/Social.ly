from flask import Flask, render_template, request, url_for, flash, redirect
from YouTube import sponsors

import pandas as pd

app = Flask(__name__)
app.config['SECRET_KEY'] = 'dev'

messages = [{'title': 'Message One',
             'content': 'Message One Content'},
            {'title': 'Message Two',
             'content': 'Message Two Content'}
            ]

tables = pd.DataFrame(data={})

@app.route('/')
def index():
    return render_template('index.html', messages=messages)

@app.route('/find/', methods=('GET', 'POST'))
def find():
    if request.method == 'POST':
        search_terms = request.form['search_terms']
        keywords = request.form['keywords']

        search_terms.split(',').sort()
        keywords.split(',').sort()

        if not search_terms:
            flash('Search terms are required!')
        else:
            tables = sponsors.sponsor_search(search_terms=search_terms, keyword_terms=keywords)
            return redirect(url_for('tables'))

    return render_template('find.html')

@app.route('/tables')
def show_tables():
    return render_template('view.html', tables=[tables.to_html(classes='data')], titles = ['na', 'Results'])