class Chatbox {
    constructor() {
        this.args = {
            openButton: document.querySelector('.chatbox__button'),
            chatBox: document.querySelector('.chatbox__support'),
            sendButton: document.querySelector('.send__button')
        }
        this.messages = [];
    }

    display() {
        const {chatBox, sendButton} = this.args;
        sendButton.addEventListener('click', () => this.onSendButton(chatBox))
        chatBox.classList.add('chatbox--active')

        const node = chatBox.querySelector('input');
        node.addEventListener("keyup", ({key}) => {
            if (key === "Enter") {
                this.onSendButton(chatBox)
            }
        })
    }

    onSendButton(chatbox) {
        var textField = chatbox.querySelector('input');
        let text1 = textField.value
        if (text1 === "") {
            return;
        }

        let msg1 = {name: "User", message: text1}
        this.messages.push(msg1);
        fetch($SCRIPT_ROOT + '/watson_response', {
            method: 'POST',
            body: JSON.stringify({message: text1}),
            mode: 'cors',
            headers: {
                'Content-Type': 'application/json'
            },
        })
            .then(r => r.json())
            .then(r => this.addTimeStamps(chatbox, r))
            .then(r => {
                    this.messages.push({name: "SmartVideo", message: r.message});
                    this.updateChatText(chatbox, r)
                    textField.value = ''
                }
            )
            .catch((error) => {
                console.error('Error:', error);
                this.updateChatText(chatbox)
                textField.value = ''
            });
    }

    addTimeStamps(chatbox, r) {

        let final_message = r.message;
        let results = {};
        // * if no results, append "no results found to message"
        if (r.timestamps.length === 0) {
            final_message += "<br><br>Unfortunately I didn't find any results."
        }

        // * if at least 1 result, write initial part of message in html with timestamp
        // * {timestamp} may have what you are looking for.
        if (r.timestamps.length > 0) {
            let timestamp1_seconds = r.timestamps[0]
            let uuid1 = generateUUID()
            final_message += '<br><br><a id=\'' + uuid1 + '\' href=\'#\'>' + secondsToMinutes(timestamp1_seconds) + '</a> may have what you are looking for.'
            results.timestamp1 = timestamp1_seconds
            results.uuid1 = uuid1
        }

        // * if 2 results, write initial part of second message with timestamp
        // * If not {timestamp2} may have what you need
        if (r.timestamps.length > 1) {
            let timestamp2_seconds = r.timestamps[1]
            let uuid2 = generateUUID()
            final_message += '<br><br>If not, <a id="' + uuid2 + '" href="#">' + secondsToMinutes(timestamp2_seconds) + '</a> may have what you need.'
            results.timestamp2 = timestamp2_seconds
            results.uuid2 = uuid2
        }

        results.message = final_message
        return results
    }

    updateChatText(chatbox, results) {
        var html = '';
        this.messages.slice().reverse().forEach(function (item, index) {
            if (item.name === "SmartVideo") {
                html += '<div class="messages__item messages__item--visitor">' + item.message + '</div>'
            } else {
                html += '<div class="messages__item messages__item--operator">' + item.message + '</div>'
            }
        });

        const chatmessage = chatbox.querySelector('.chatbox__messages');
        chatmessage.innerHTML = html;

        //    add video jumps to timestamps
        if (results.timestamp1 !== undefined) {
            make_timestamps_clickable(results.uuid1, results.timestamp1)
        }
        if (results.timestamp2 !== undefined) {
            make_timestamps_clickable(results.uuid2, results.timestamp2)
        }
    }
}

function generateUUID() {
    // credit: https://github.com/IBM/audio_search_on_podcasts/blob/master/static/videojs-markers.js
    var d = new Date().getTime();
    var uuid = 'xxxxxxxx-xxxx-4xxx-yxxx-xxxxxxxxxxxx'.replace(/[xy]/g, function (c) {
        var r = (d + Math.random() * 16) % 16 | 0;
        d = Math.floor(d / 16);
        return (c === 'x' ? r : r & 0x3 | 0x8).toString(16);
    });
    return uuid;
}


function make_timestamps_clickable(id, timestamp) {
    const video = document.getElementById("videoDemo_html5_api"); // have to use this ID for some reason
    document.getElementById(id).addEventListener("click", function (event) {
        video.currentTime = timestamp;
        video.play();
    }, false);
}

function secondsToMinutes(s) {
    return (s - (s %= 60)) / 60 + (9 < s ? ':' : ':0') + s
}

const chatbox = new Chatbox();
chatbox.display();