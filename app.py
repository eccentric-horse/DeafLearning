from flask import Flask, render_template, request, jsonify, session, redirect, url_for
from flask_session import Session
from cachelib.file import FileSystemCache
from question_util import choose_questions, get_question_types
from db_util import save_answer_data, save_selected_questions, save_survey_data

import os
import uuid

app = Flask(__name__)
app.secret_key = os.environ['SESSION_SECRET']

app.config['SESSION_PERMANENT'] = True
app.config['SESSION_TYPE'] = 'cachelib'
app.config['SESSION_USE_SIGNER'] = False
app.config['SESSION_SERVER_SIDE'] = True
app.config['SESSION_SERIALIZATION_FORMAT'] = 'json'
app.config['SESSION_CACHELIB'] = FileSystemCache(threshold=2048, cache_dir="sessions")
Session(app)

@app.route('/')
def index() -> "html":
    session.clear()
    session['uuid'] = str(uuid.uuid4())
    return render_template('interaction.html')

@app.route('/ask', methods = ["POST"])
def do_ask() -> "html":
    prompt = request.form['input_string']
    results, complete = get_question_types(prompt)
    if complete:
        session['question_types'] = results
        return redirect(url_for('questions', qt=results))

    return render_template('response.html',
                           the_input_string = prompt,
                           the_results = results,)

@app.route('/get-questions', methods=['GET'])
def get_questions():
    # don't generate new questions on refresh for the same session
    questions = session.get('questions')
    if not questions:
        input_list = request.args.getlist('qt')
        questions = choose_questions(input_list)
        # save the questions that were sent so we can look up the associated data
        session['questions'] = questions
        # log them also
        save_selected_questions(questions)
    return jsonify(questions)

# Path to get the video play
@app.route('/questions')
def questions() -> "html":
    return render_template('questions.html')

@app.route('/log-answer', methods=['GET'])
def log_answer():
    question_index = request.args.get('qi', type=int)
    answer_index = request.args.get('ai', type=int)
    time_answer = request.args.get('ta', type=int)

    client_questions = session.get('questions', None)

    # valid parameters
    if not client_questions:
        return "Client not found", 400
    if question_index < 0 or question_index >= len(client_questions):
        return "Invalid question index", 400

    question_data = client_questions[question_index]

    if answer_index < 0 or answer_index >= len(question_data.get("answers", [])):
        return "Invalid answer index", 400

    # answer metadata to db
    save_answer_data(question_data, answer_index, time_answer)

    # return status ok
    return "", 200

@app.route('/survey', methods=['GET', 'POST'])
def survey():
    if request.method == 'POST':
        save_survey_data(request.form.to_dict())
        return render_template("survey_success.html")
    else:
        from pprint import pprint
        pprint(session['questions'])
        return render_template('survey.html', 
                                questions=session['questions'],
                                qt=session.get('question_types', []))

if __name__ == '__main__':
    app.run(debug=True)