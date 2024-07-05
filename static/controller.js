// linear look up is fine for small amount of questions
// can do any optimizations later, handling rewind,
// ensuring questions are ordered by timestamp in array
// to cut down search during timeupdate handler, could 
// also do something like register timeout event and
// manage video controls to get more exact timing, to do
// this could use a player library like video.js
// or something.
let questions = []

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
    let questionContent = element.children[1].getInnerHTML();
    console.log(`Registered question with id ${element.id} at ${timestamp} ms. Question: ${questionContent}}`);
}

function shouldShowQuestionTick(event) {
    let timeMs = Math.floor(video.elem.currentTime * 1000);
    console.log("shouldShowQuestionTick currentTime = " + timeMs + " ms");
    for(let question of questions) {
        if(timeMs >= question.timestamp && !question.answered) {
            question.showQuestion();
            break;
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
                questionHeader.textContent = `[ ${item.question_type} ] Quiz Question`;
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

                const transcriptTime = document.createElement('h2');
                transcriptTime.textContent = `Reference Timestamp: ${millisToMinutesAndSeconds(item.transcript_timestamp_start)}`;
                questionContainer.appendChild(transcriptTime)

                const questionOrder = document.createElement('h4');
                questionOrder.textContent = `Current Question: Q ${item.order}`
                questionContainer.appendChild(questionOrder);

                const questionsLeft = document.createElement('h4');
                questionsLeft.textContent = `${10 - item.order} questions left`
                questionContainer.appendChild(questionsLeft);

                container.appendChild(questionContainer);
                registerQuestion(questionContainer, item.time_stamp, answerHandler);
            });

            registerAllAnswers(); // Register answer event listeners
            video.elem.addEventListener('timeupdate', shouldShowQuestionTick); // Listen for time updates
            video.elem.addEventListener('play', manageVideoPlay); // Listen for play events
        })
        .catch(error => {
            console.error('Error fetching questions:', error);
        });
}

function millisToMinutesAndSeconds(millis) {
    var minutes = Math.floor(millis / 60000);
    var seconds = ((millis % 60000) / 1000).toFixed(0);
    return minutes + ":" + (seconds < 10 ? '0' : '') + seconds;
}

document.body.onload = initializeApp;