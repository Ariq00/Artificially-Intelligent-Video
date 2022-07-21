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

    def test_invalid_file(self, client):
        response = client.post('/', data=dict(
            video='file',
            languageSubmit='us',
            file=open('../tests/test_upload_files/not_an_mp4_file.txt', 'rb'),
        ), follow_redirects=True)
        assert b"Please upload an MP3 or MP4 file!" in response.data

    def test_valid_file(self, client):
        response = client.post('/', data=dict(
            video='file',
            languageSubmit='us',
            file=open(
                '../tests/test_upload_files/Microwaves explained in ten seconds.mp4',
                'rb'),
        ), follow_redirects=True)
        delete_document(response.text)
        assert b"Microwaves_explained_in_ten_seconds.mp4" in response.data

    def test_watson_query(self, client):
        document_id = "253ab659-de8c-4f9b-a4e6-572ecb73a121"  # id for microwaves transcript in watson discovery
        response = client.post('/watson_response', json=dict(
            message='When are microwaves discussed?',
            document_id=document_id,
            # microwaves discussed at 5 seconds
        ), follow_redirects=True)
        assert b"5" in response.data


def delete_document(response_string):
    discovery = setup_discovery()
    document_id_substring = '$DOCUMENT_ID = "'
    index = response_string.find(document_id_substring) + len(
        document_id_substring)
    document_id = response_string[
                  index:index + 36]  # finding the document ID in the html
    delete_transcript(discovery, document_id)
    return "Document deleted from Watson Discovery"
