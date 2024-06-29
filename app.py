from flask import Flask, render_template, request, jsonify, send_file, session, redirect, url_for
from question_util import choose_questions, get_question_types

app = Flask(__name__)
app.secret_key = 'this should be in an environment variable or secret vault or something'

@app.route('/')
def index() -> "html":
    return render_template('interaction.html')

@app.route('/ask', methods = ["POST"])
def do_ask() -> "html":
    prompt = request.form['input_string']
    results, complete = get_question_types(prompt)
    if complete:
        return redirect(url_for('questions', qt=results))

    return render_template('response.html', 
                           the_input_string = prompt,
                           the_results = results,)

@app.route('/get-questions', methods=['GET'])
def get_questions():
    input_list = request.args.getlist('qt')
    result = choose_questions(input_list)
    return jsonify(result)

# Path to get the video play
@app.route('/questions')
def questions() -> "html":
    return render_template('questions.html')

@app.route('/video')
def video():
    # Specify the correct path to your video file
    video_path = 'videos/input_file.mp4'
    return send_file(video_path, as_attachment=True)

if __name__ == '__main__':
    app.run(debug=True)