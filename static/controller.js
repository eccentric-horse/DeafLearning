// linear look up is fine for small amount of questions
// can do any optimizations later, handling rewind,
// ensuring questions are ordered by timestamp in array
// to cut down search during timeupdate handler, could
// also do something like register timeout event and
// manage video controls to get more exact timing, to do
// this could use a player library like video.js
// or something.
let questions = []
let expectedVideoPosition = 0;

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
        video.elem.question = undefined;
        video.elem.play();
    }

    isAtQuestion() {
        let delta =  Math.abs(video.elem.currentTime - (this.timestamp / 1000));
        return delta < 0.01;
    }

    pauseAtQuestion() {
        if(!this.isAtQuestion())
            video.elem.currentTime = this.timestamp / 1000;
        video.elem.pause();
    }

    logAnswer(selectedAnswer) {
        const time_answered = Date.now() - this.time_shown;
        const answer_index = selectedAnswer.getAttribute('answer-index');
        const question_index = selectedAnswer.parentNode.getAttribute("question-index");
        const log_url = `/log-answer?ta=${time_answered}&ai=${answer_index}&qi=${question_index}`;
        fetch(log_url).then(response => {
            console.log(response);
        });
    }

    checkAnswer(selectedAnswer) {
        this.logAnswer(selectedAnswer);
        if(this.answerHandler(selectedAnswer)) {
            this.answeredQuestion();
        }
    }

    showQuestion() {
        if(this.element.style.display != 'block') {
            video.elem.questionOpen = true;
            video.elem.question = this;
            this.element.style.display = 'block'; // Display the pop-up container
            this.time_shown = Date.now();

            // always ensure question is shown at the right place
            this.pauseAtQuestion();
        }
    }
  }

function registerQuestion(element, timestamp, handler) {
    let question = new Question(element, timestamp, handler);
    questions.push(question);
    element.question = question;
    let questionContent = element.children[1].getInnerHTML();
    // keep questions array ordered by timestamp to speed up question lookup
    // the index of this questions array is not related to the one on the server!!!
    // use the attribute of the question element to get that index
    questions.sort((a, b) => (a.timestamp - b.timestamp));
    console.log(`Registered question with id ${element.id} at ${timestamp} ms. Question: ${questionContent}}`);
}

function getQuestionIfReady() {
    // change structure to sort by ts and just pull from the index
    // the next question
    let timeMs = Math.floor(video.elem.currentTime * 1000);
    for(let question of questions) {
        if(timeMs >= question.timestamp && !question.answered) {
            return question;
        }
    }
}

function videoTimeUpdate(event) {
    console.log("videoTimeUpdate called");

    let question = getQuestionIfReady();
    // don't manage timeupdates when seeking
    if(question && !video.elem.seeking) {
        if(!video.elem.questionOpen) {
            question.showQuestion();
        } else {
            video.elem.question.pauseAtQuestion();
        }
    }
}

function videoSeeked(event) {
    console.log("videoSeeked called");
    let question = getQuestionIfReady();
    if(question && !video.elem.questionOpen) {
        question.showQuestion();
    } else {
        // ensure video autoplays if we are rewinding
        video.elem.play();
    }
}

function videoSeeking(event) {
    console.log("videoSeeking called");

    let question = getQuestionIfReady();
    if(!question) return;

    if(!video.elem.questionOpen) {
        question.showQuestion();
    } else {
        video.elem.question.pauseAtQuestion();
    }
}

function videoPlay(event) {
    // need to check if the video is open
    // and that the question would be ready
    // to block unpausing and single stepping
    // video
    console.log("videoPlay called");
    let question = getQuestionIfReady();
    if(video.elem.questionOpen && question) {
        video.elem.question.pauseAtQuestion();
    }
 }

 function videoWaiting(evernt) {
    console.log("Video is waiting for more data. Forcing rewind in case stuck after question.");
    if(!video.elem.questionOpen) {
        video.elem.currentTime = video.elem.currentTime - 1;
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
    const congratsMessages = ["Brilliant job, that is correct!", "Awesome answer, you are correct!", "Wonderful, that is the correct answer!", "Great work, you got the right answer!", "Correct, you are killing it!"];
    if(selectedAnswer.getAttribute("correct")) {
        alert(congratsMessages[Math.random() * congratsMessages.length >> 0]);
        return true;
    } else {
        alert("Incorrect, please try again.\nYou can also rewind if you need to watch again - \"Reference Start Timestamp\" tells you the best place to go back to for this particular question.");
        return false;
    }
}

function initializeApp() {
    fetch('/get-questions' + document.location.search)
        .then(response => response.json())
        .then(data => {
            const container = document.getElementById('questions-container');

            data.forEach((item, question_index) => {
                const questionContainer = document.createElement('div');
                questionContainer.id = `question-${question_index + 1}`;
                questionContainer.setAttribute("question-index", question_index);
                questionContainer.className = 'popup-container';

                const questionHeader = document.createElement('h3');
                questionHeader.textContent = `Quiz Question`;
                questionContainer.appendChild(questionHeader);

                if (`${item.question_type}` !== "transcript") {
                    const questionInfo = document.createElement('p1');
                    if (`${item.question_type}` === "emotion")
                        questionInfo.textContent = "It seems like most DHH learners have confusion here. We generated this question to support your understanding:";
                    else
                        questionInfo.textContent = "It seems like visual movements tend to be overwhelming here. We generated this question to support your visual attention:";
                    questionContainer.appendChild(questionInfo);
                }

                const questionText = document.createElement('p');
                questionText.textContent = item.question;
                questionContainer.appendChild(questionText);

                item.answers.forEach((answer, answer_index) => {
                    const answerButton = document.createElement('button');
                    answerButton.className = 'answer';
                    answerButton.textContent = answer.answer;

                    if (answer.correct) {
                        answerButton.setAttribute("correct", true);
                    }

                    answerButton.setAttribute("answer-index", answer_index);

                    questionContainer.appendChild(answerButton);
                });

                const transcriptTime = document.createElement('h2');
                transcriptTime.textContent = `Reference Start Timestamp: ${millisToMinutesAndSeconds(item.transcript_timestamp_start)}`;
                questionContainer.appendChild(transcriptTime)

                const questionOrder = document.createElement('h4');
                questionOrder.textContent = `This is question #${item.order}`
                questionContainer.appendChild(questionOrder);

                const questionsLeft = document.createElement('h4');
                questionsLeft.textContent = `There are ${10 - item.order} questions left`
                questionContainer.appendChild(questionsLeft);

                container.appendChild(questionContainer);
                registerQuestion(questionContainer, item.time_stamp, answerHandler);
            });

            registerAllAnswers(); // Register answer event listeners
            video.elem.addEventListener('timeupdate', videoTimeUpdate); // Listen for time updates
            video.elem.addEventListener('play', videoPlay); // Listen for play events
            video.elem.addEventListener('seeking', videoSeeking); // manage seeking
            video.elem.addEventListener('seeked', videoSeeked); // manage seeked
            video.elem.addEventListener("waiting", videoWaiting); // hack

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
