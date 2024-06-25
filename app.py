from flask import Flask, render_template, request, jsonify, send_file
from AI_interaction import answer_question
from chooseQuestions import chooseQuestions

app = Flask(__name__)

@app.route('/')
def index() -> "html":
    return render_template('interaction.html')

@app.route('/ask', methods = ["POST"])
def do_ask() -> "html":
    input_string = request.form['input_string']
    results = answer_question(input_string)
    return render_template('response.html', 
                           the_input_string = input_string,
                           the_results = results,)

@app.route('/get-questions', methods=['GET'])
def get_questions():
    # This input file list should be figured out by ChatGPT
    input_list = ['transcript', 'emotion', 'movement']
    result = chooseQuestions(input_list)
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