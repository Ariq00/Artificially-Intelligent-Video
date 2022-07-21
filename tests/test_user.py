from tests.test_auth import login


class TestAuthentication:
    def test_no_results_saved_videos(self, client, user):
        login(client, user)
        response = client.get("/search_saved_videos?searchQuery=Test?query")
        assert b"No results found" in response.data

    def test_upload_multiple_youtube(self, client, user):
        login(client, user)
        response = client.post('/upload_multiple_videos', data=dict(
            video='youtube',
            languageSubmit='us',
            youtubeUrls='https://www.youtube.com/watch?v=OFG_OoiMhWE',
            # 17 second YouTube video - Microwaves explained in ten seconds
        ), follow_redirects=True)
        assert b'Success' in response.data
