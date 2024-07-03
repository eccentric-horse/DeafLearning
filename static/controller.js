// linear look up is fine for small amount of questions
// can do any optimizations later, handling rewind,
// ensuring questions are ordered by timestamp in array
// to cut down search during timeupdate handler, could 
// also do something like register timeout event and
// manage video controls to get more exact timing, to do
// this could use a player library like video.js
// or something.



let questions = []
// Keeps track of what question we are waiting next for (eliminates the need for linear look up)
let counter = 0

const video = {
    get elem() {
      return document.getElementById('interactive-video');
    },
};

class Question {
    constructor(element, timestamp, handler) {
      this.timestamp = timestamp;
      this.element = element;
      this.answered = false;
      this.answerHandler = handler;
    }

    answeredQuestion() {
        this.answered = true;
        ++counter; // Increment counter so that next question can be checked now
        this.hideQuestion();
    }

    hideQuestion() {
        this.element.style.display = 'none'; // Hide the pop-up container
        video.elem.questionOpen = false;
        video.elem.play();
    }
    
    checkAnswer(selectedAnswer) {
        if(this.answerHandler(selectedAnswer)) {
            this.answeredQuestion();
        }
    }

    showQuestion() {
        if(this.element.style.display != 'block') {
            video.elem.pause();
            video.elem.questionOpen = true;
            this.element.style.display = 'block'; // Display the pop-up container
        }
    }
  }

function registerQuestion(element, timestamp, handler) {
    let question = new Question(element, timestamp, handler);
    questions.push(question);
    element.question = question;
    console.log(`Registered question with id ${element.id} at ${timestamp} ms.`);
}

function shouldShowQuestionTick(event) {
    let timeMs = Math.floor(video.elem.currentTime * 1000);
    console.log("shouldShowQuestionTick currentTime = " + timeMs + " ms");

    // Loads in the next question as dictated by the counter
    // Question will either be waiting for the video timestamp to pass its own, so that it can pop up, or
    // it is currently visible on-screen waiting to be answered - user can rewind to watch prior content again
    let question = questions.at(counter);

    // Check if there is a question open right now
    if (video.elem.questionOpen) { // If so, worry about time control
        if (timeMs > question.timestamp) { // Checks if new video timestamp is after when the question is supposed to pop up
            video.elem.currentTime = question.timestamp / 1000; // Forces video back to question pop-up time
        } else if (timeMs < question.timestamp - 1000) { // Checks if new video timestamp was rewinded by more than a second
            question.hideQuestion(); // Putting the current question aside for now
        }
    } else { // If not, check if the next question in the list is ready to pop-up
        if (timeMs >= question.timestamp && !question.answered) { // Checks if question is ready to pop up, and if it is unanswered (technically not needed)
            question.showQuestion(); // Appear!
        }
    }
}

function manageVideoPlay(event) {
    // hack so someone can't play while a question is open
    if(video.elem.questionOpen) {
        video.elem.pause();
    }
}

function registerAllAnswers() {
    let answers = document.getElementsByClassName("answer");
    for(let answer of answers) {
        // this will need to change if the popup stucture changes 
        // and becomes more fancy later, but can cross that bridge
        // when we come to it.
        answer.addEventListener("click", (event) => {
            answer.parentNode.question.checkAnswer(answer);
        });
    }
}

function answerHandler(selectedAnswer) {
    if(selectedAnswer.getAttribute("correct")) {
        alert("Yes that is right!");
        return true;
    } else {
        alert("No that is not quite right.");
        return false;
    }
}

function initializeApp() {
    fetch('/get-questions' + document.location.search) 
        .then(response => response.json())
        .then(data => {
            const container = document.getElementById('questions-container');

            data.forEach((item, index) => {
                const questionContainer = document.createElement('div');
                questionContainer.id = `question-${index + 1}`;
                questionContainer.className = 'popup-container';

                const questionHeader = document.createElement('h3');
                questionHeader.textContent = `Quiz Question`;
                questionContainer.appendChild(questionHeader);

                const questionText = document.createElement('p');
                questionText.textContent = item.question;
                questionContainer.appendChild(questionText);

                item.answers.forEach(answer => {
                    const answerButton = document.createElement('button');
                    answerButton.className = 'answer';
                    answerButton.textContent = answer.answer;

                    if (answer.correct) {
                        answerButton.setAttribute("correct", true);
                    }

                    questionContainer.appendChild(answerButton);
                });

                container.appendChild(questionContainer);
                registerQuestion(questionContainer, item.time_stamp, answerHandler);
            });

            // Sorts the questions list by their timestamp in ascending order
            questions.sort(function(a, b) {
                return a.timestamp - b.timestamp;
            });
            // For verifying sort
            // console.log("Questions sorted, timestamps are now ordered as follow:")
            // for (let question of questions) {
            //     console.log(question.timestamp)
            // }

            registerAllAnswers(); // Register answer event listeners
            video.elem.addEventListener('timeupdate', shouldShowQuestionTick); // Listen for time updates
            video.elem.addEventListener('play', manageVideoPlay); // Listen for play events
        })
        .catch(error => {
            console.error('Error fetching questions:', error);
        });
}

document.body.onload = initializeApp;