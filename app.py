from flask import Flask, render_template, request, jsonify, send_file
import re
from AI_interaction import answer_question
from chooseQuestions import chooseQuestions
from utitlities import ChatTemplate

app = Flask(__name__)
chat_template = ChatTemplate.from_file('questionTypes.json')
chat_history = ''
print("CHAT HISTORY\n" + chat_history)
done_pattern = r'QUESTIONS(.*)DONE'

@app.route('/')
def start() -> "html":
    chat_history.join(["ChatBot: ", chat_template.template['messages'][-1]['content']])
    print("CHAT HISTORY\n" + chat_history)
    return render_template('welcome.html', chatbot_message=chat_history)


@app.route('/onboarding', methods=['POST'])
def onboarding() -> "html":
    # Grab user input from text box
    prompt = request.form['user_input']
    # Append to textual chat history for printing on the screen
    chat_history.join(["You: ", prompt])
    # Store to memory as chat context / history
    chat_template.template['messages'].append({'role': 'user', 'content': prompt})
    # Generate a response based on the updated chat template
    message = chat_template.completion({}).choices[0].message
    # Check if the message content contains 'DONE'
    if 'DONE' in message.content:
        # Apply the provided regex pattern to extract desired information
        # Return the extracted information, stripped of leading and trailing whitespace
        return re.search(done_pattern, message.content, re.DOTALL).group(1).strip()
    # Append response to textual chat history for printing
    chat_history.join(["ChatBot: ", f'{message.content}'])
    # Store to memory as chat context / history
    chat_template.template['messages'].append({'role': message.role, 'content': message.content})
    print("CHAT HISTORY\n" + chat_history)
    return render_template('welcome.html', chatbot_message=chat_history)


@app.route('/interaction')
def index() -> "html":
    return render_template('interaction.html')


@app.route('/ask', methods=["POST"])
def do_ask() -> "html":
    input_string = request.form['input_string']
    results = answer_question(input_string)
    return render_template('response.html',
                           the_input_string=input_string,
                           the_results=results, )


@app.route('/get-questions', methods=['GET'])
def get_questions():
    # This input file list should be figured out by ChatGPT
    # input_list = get_question_types()
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
