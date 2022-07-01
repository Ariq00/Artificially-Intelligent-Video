function add_concept_timestamps() {
    for (let i in $CONCEPTS) {
        let concept = $CONCEPTS[i]
        fetch($SCRIPT_ROOT + '/watson_response', {
            method: 'POST',
            body: JSON.stringify({message: $CONCEPTS[i]}),
            mode: 'cors',
            headers: {
                'Content-Type': 'application/json'
            },
        })
            .then(r => r.json())
            .then(r => {
                make_concept_clickable(concept, r.timestamps[0])
            })
            .catch((error) => {
                console.error('Error:', error);
            });
    }
}

function make_concept_clickable(id, timestamp) {
    const video = document.getElementById("videoDemo_html5_api"); // have to use this ID for some reason
    const section = document.getElementById("key_concepts_section")

    if (timestamp !== undefined) {

        // add to the inner html
        let concept_card =
            '<div class="col-sm-4">' +
            '<div class="pt-2">' +
            '<div class="card">' +
            '<div class="card-body">' +
            '<h4 class="card-title"><a id="' + id +
            '" href="#">' + id + '</a>' +
            '</h4>' +
            '</div>' +
            '</div>' +
            '</div>' +
            '</div>'

        section.insertAdjacentHTML("beforeend", concept_card);

        document.getElementById(id).addEventListener("click", function (event) {
            video.currentTime = timestamp;
            video.play();
        }, false);
    }
}

window.onload = function () { // have to set 5 second timeout or no timestamps are returned
    setTimeout(function () {
        add_concept_timestamps()
    }, 5000);

};

