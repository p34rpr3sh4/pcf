const msgerForm = get(".msger-inputarea");
const msgerInput = get(".msger-input");
const msgerChat = get(".msger-chat");

var chat_last_time = {};

const BOT_MSGS = [
    "Hi, how are you?",
    "Ohh... I can't understand what you trying to say. Sorry!",
    "I like to play games... But I don't know how to play!",
    "Sorry if my answers are not relevant. :))",
    "I feel sleepy! :("
];

// Icons made by Freepik from www.flaticon.com
const BOT_IMG = "https://image.flaticon.com/icons/svg/327/327779.svg";
const PERSON_IMG = "https://image.flaticon.com/icons/svg/145/145867.svg";
const BOT_NAME = "BOT";
const PERSON_NAME = "Sajad";


msgerForm.forEach(div => {
    div.addEventListener("submit", event => {
        event.preventDefault();

        original_element = event.srcElement || event.originalTarget;
        const msgText = original_element[1].value;
        const chat_id = original_element[0].value;
        if (!msgText) return;


        url = chat_id + '/sendmessage';
        data = {
            'csrf_token': csrf_token,
            'message': msgText
        };

        var body = 'csrf_token=' + encodeURIComponent(csrf_token) + '&message=' + encodeURIComponent(msgText);
        var request = new XMLHttpRequest();
        request.open('POST', url, false);
        request.setRequestHeader('Content-Type', 'application/x-www-form-urlencoded');
        request.send(body);
        let last_time = Number.parseInt(request.response);

        if (chat_last_time[chat_id] === undefined) {
            chat_last_time[chat_id] = 0;
        }

        if (last_time > chat_last_time[chat_id]) {
            chat_last_time[chat_id] = last_time;
        }

        appendMessage(div.id, current_user_email, PERSON_IMG, "right", msgText, last_time);
        original_element[1].value = "";

        //botResponse();
    });
});

function htmlspecialchars( html){
  var div =  document.createElement('div');
  div.innerText = html;
  return div.innerHTML;
}

function appendMessage(chat_id, name, img, side, text, time) {
    //   Simple solution for small apps
    const msgHTML = `
    <div class="msg ${side}-msg">
      <div class="msg-img" style="background-image: url(${img})"></div>

      <div class="msg-bubble">
        <div class="msg-info">
          <div class="msg-info-name">${htmlspecialchars(name)}</div>
          <div class="msg-info-time">${formatDate(new Date(time))}</div>
        </div>

        <div class="msg-text" style="word-break: break-all; white-space:pre-wrap;">${htmlspecialchars(text)}</div>
      </div>
    </div>
  `;
    old_form = document.querySelector(".msger-inputarea");
    msgerChat.forEach(div => {
        if (div.id===chat_id){
            div.insertAdjacentHTML("beforeend", msgHTML);
            div.scrollTop += 500;
        }
    });
}


// Utils
function get(selector, root = document) {
    return root.querySelectorAll(selector);
}

function formatDate(date) {
    const h = "0" + date.getHours();
    const m = "0" + date.getMinutes();
    const month = "0" + date.getMonth();
    const year = String(date.getFullYear());
    const day = "0" + date.getDate();


    return `${h.slice(-2)}:${m.slice(-2)} ${day.slice(-2)}.${month.slice(-2)}.${year}`;
}

function random(min, max) {
    return Math.floor(Math.random() * (max - min) + min);
}

function getall_json(chat_id){
    return $.getJSON(chat_id + "/getall.json", {}, async=false);
}


function get_all_messages(chat_id, current_user_email, chat_last_time) {
    var request = new XMLHttpRequest();
    request.open('GET', chat_id + "/getall.json", false);
    request.send(null);
    let j_data = JSON.parse(request.response);
    last_time = 0;
    for (let message of j_data) {
        let side = 'left';
        if (message['email'] === current_user_email) {
            side = 'right';
        }
        appendMessage(chat_id, message['email'], PERSON_IMG, side, message['message'], message['time']);
        last_time = message['time'];
        console.log(message);
    }
    chat_last_time[chat_id] = last_time;
    return last_time;
}

function check_new_messages(chat_id, current_user_email, chat_last_time){
    if (chat_last_time[chat_id] === undefined){
        chat_last_time[chat_id] = 0;
    }
    console.log('Checking new messages');
    var request = new XMLHttpRequest();
    last_time = chat_last_time[chat_id]
    request.open('GET', chat_id + "/getnewmessages/"+String(last_time)+"/", false);
    request.send(null);
    let j_data = JSON.parse(request.response);
    for (let message of j_data) {
        let side = 'left';
        if (message['email'] === current_user_email) {
            side = 'right';
        }
        appendMessage(chat_id, message['email'], PERSON_IMG, side, message['message'], message['time']);
        last_time = message['time'];
        console.log(message);
    }
    chat_last_time[chat_id] = last_time;
    return last_time;
}
