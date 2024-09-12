# DeafLearning

This project is a research prototype. 

You can access the web app [here](https://dhh-learning.azurewebsites.net/).

This project consists of two stages. First, you will go through an onboarding process where ChatGPT will provide you with options to personalize your learning process a little. These options determine what kinds of questions will be chosen to pop up as you watch the video. Then, you will watch a video, and questions will pop up throughout.

## How To Run it

To run the project locally, run `pip3 install -r requirements.txt` to have all the dependencies installed on your machine, then navigate to root directory and run `python3 app.py`.

## Design Spec

### Functional Requirements

1. Video Playback

The video player should support standard video formats (MP4).
The player should have standard controls (play, pause, volume, fullscreen).

2. Pop-Up Quizzes

Quizzes should appear as overlays on the video at specified timestamps.
The video should pause when a quiz appears and resume upon quiz completion.
The quiz should include at least one question and multiple-choice answers.
Feedback should be given for correct/incorrect answers.

3. Quiz Management

We should be able to add, edit, and delete quizzes without too much effort.
Quizzes should be linked to specific timestamps within the video.
Pop-up positions should be adjustable anywhere on the video screen.

4. AI Interaction 

Allow the user to interact with ChatGPT API at the start.
At the start, to introduce the system and choose the kinds of questions that will appear (visual, emotional, transcript).

### Technical Specifications
1. Frontend
- HTML5: For structuring the web content.
- CSS3: For styling the web application.
- JavaScript: For handling the interactive aspects of the application.

2. Backend
- Python 3.x: Programming language for backend development.
- Flask: Lightweight web framework for handling HTTP requests and responses.

3. Database
- Azure DB

4. Hosting
- Flask development server for local development and testing.
- Deployment on a suitable web server [Microsoft Azure] for production.

### System Architecture
1. Client-Side (Browser)

Video player implemented using HTML5 `video` tag.
JavaScript to handle video events and display pop-up quizzes.

2. Server-Side (Flask Application)

- Serve the HTML, CSS, and JavaScript files.
- Serve the video file to the client.
- Database.
