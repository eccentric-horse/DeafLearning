from flask import Flask, render_template, send_file

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('questions.html')

@app.route('/video')
def video():
    # Specify the correct path to your video file
    video_path = 'videos/input_file.mp4'
    return send_file(video_path, as_attachment=True)

if __name__ == '__main__':
    app.run(debug=True)