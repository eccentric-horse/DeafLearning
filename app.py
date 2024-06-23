from flask import Flask, render_template, request
from AI_interaction import answer_question

app = Flask(__name__)

@app.route('/')
def index() -> "html":
    return render_template('interact.html')

@app.route('/ask', methods = ["POST"])
def do_ask() -> "html":
    input_string = request.form['input_string']
    results = answer_question(input_string)
    return render_template('response.html', 
                           the_input_string = input_string,
                           the_results = results,)

if __name__ == '__main__':
    app.run(debug=True)