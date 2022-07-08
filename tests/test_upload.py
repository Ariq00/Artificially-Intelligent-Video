from watson_discovery import delete_transcript, setup_discovery


class TestUpload:
    def test_invalid_youtube_url(self, client):
        response = client.post('/', data=dict(
            video='youtube',
            languageSubmit='us',
            youtubeUrl='not_an_url',
        ), follow_redirects=True)
        assert b"could not find match" in response.data

    def test_large_youtube_video(self, client):
        response = client.post('/', data=dict(
            video='youtube',
            languageSubmit='us',
            youtubeUrl='https://www.youtube.com/watch?v=wnhvanMdx4s',
            # 10 hour video
        ), follow_redirects=True)
        assert b"Video file is greater than 500MB!" in response.data

    def test_silent_youtube_video(self, client):
        response = client.post('/', data=dict(
            video='youtube',
            languageSubmit='us',
            youtubeUrl='https://www.youtube.com/watch?v=aZnPjwXTap4',
            # 5 seconds of silence
        ), follow_redirects=True)

        assert b"Could not analyse video. Video has no audio content!" in response.data

    def test_valid_youtube_url(self, client):
        response = client.post('/', data=dict(
            video='youtube',
            languageSubmit='us',
            youtubeUrl='https://www.youtube.com/watch?v=OFG_OoiMhWE',
            # 17 second YouTube video - Microwaves explained in ten seconds
        ), follow_redirects=True)
        delete_document(response.text)
        assert b"Microwaves explained in ten seconds" in response.data


def delete_document(response_string):
    discovery = setup_discovery()
    document_id_substring = '$DOCUMENT_ID = "'
    index = response_string.find(document_id_substring) + len(
        document_id_substring)
    document_id = response_string[
                  index:index + 36]  # finding the document ID in the html
    delete_transcript(discovery, document_id)
    return "Document deleted from Watson Discovery"
