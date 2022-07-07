from models import User


class TestRegistration:
    def test_registration_successful(self, client, user):
        user_count = len(User.objects())
        response = client.post('/register', data=dict(
            first_name='Test',
            last_name='User',
            email='test_user2@test.com',
            password='password',
            password_repeat='password'
        ), follow_redirects=True)
        assert len(User.objects()) - user_count == 1
        assert b"Thank you for signing up Test!" in response.data

    def test_email_already_registered(self, client, user):
        response = client.post('/register', data=dict(
            first_name='Test',
            last_name='User',
            email='test_user1@test.com',
            password='password',
            password_repeat='password'
        ), follow_redirects=True)
        assert b"Email address already in use" in response.data

    def test_passwords_not_matching(self, client, user):
        response = client.post('/register', data=dict(
            first_name='Test',
            last_name='User',
            email='test_user1@test.com',
            password='password',
            password_repeat='different_password'
        ), follow_redirects=True)
        assert b"Passwords must match" in response.data

    def test_login(self, client, user):
        response = client.post('/login', data=dict(
            email=user.email,
            password='test_password'
        ), follow_redirects=True)
        assert b"Welcome Person. You are now logged in!" in response.data
