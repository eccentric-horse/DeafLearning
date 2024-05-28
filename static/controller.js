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
    console.log(`Registered question with id ${element.id} at ${timestamp} ms.`);
}

function shouldShowQuestionTick(event) {
    let timeMs = Math.floor(video.elem.currentTime * 1000);
    console.log("shouldShowQuestionTick currentTime = " + timeMs + " ms");
    for(let question of questions) {
        if(timeMs >= question.timestamp && !question.answered) {
            question.showQuestion();
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

function initializeApp() {
    registerAllAnswers();
    video.elem.addEventListener('timeupdate', shouldShowQuestionTick);
    video.elem.addEventListener('play', manageVideoPlay);

}

document.body.onload = initializeApp;