document.getElementById("saveVideo").addEventListener("click", add_to_db)

function add_to_db() {
    fetch($SCRIPT_ROOT + '/save_video', {
        method: 'POST',
        body: JSON.stringify({
            filepath: $VIDEO_FILEPATH,
            document_id: $DOCUMENT_ID,
            title: $VIDEO_TITLE,
            summary: $SUMMARY,
            sentiment: $SENTIMENT,
            score: $SCORE,
            concepts: $CONCEPTS
        }),
        mode: 'cors',
        headers: {
            'Content-Type': 'application/json'
        },
    })
        .then(r => r.json())
        .then(() => {
            const save_button = document.getElementById("saveVideo");
            save_button.innerHTML = "Video saved!"
            save_button.classList.add("disabled")
        })
        .catch((error) => {
            console.error('Error:', error);
        });
}
