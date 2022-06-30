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
                console.log(r)
                make_concept_clickable(concept, r.timestamps[0])
            })
            .catch((error) => {
                console.error('Error:', error);
            });
    }
}

function make_concept_clickable(id, timestamp) {
    const video = document.getElementById("videoDemo_html5_api"); // have to use this ID for some reason
    if (timestamp !== undefined) {
        document.getElementById(id).addEventListener("click", function (event) {
            video.currentTime = timestamp;
            video.play();
        }, false);
    } else { // this is just to remove the hyperlink for concepts without timestamp
        const hyperlink = document.getElementById(id);
        const link_removed = document.createElement('p');
        link_removed.innerHTML = hyperlink.innerHTML
        hyperlink.parentNode.replaceChild(link_removed, hyperlink)
    }
}

window.onload = function () { // have to set 5 second timeout or no timestamps are returned
    setTimeout(function () {
        add_concept_timestamps()
    }, 5000);

};

