import multiprocessing

import mongoengine
import pytest
from selenium import webdriver
from selenium.webdriver import EdgeOptions
from webdriver_manager.microsoft import EdgeChromiumDriverManager
from werkzeug.security import generate_password_hash
import os
import glob
from models import Video, User
from setup_app import create_app


@pytest.fixture(scope='session')
def app(request):
    """ Returns a session wide Flask app """
    _app = create_app()
    ctx = _app.app_context()
    ctx.push()
    _app.config["WTF_CSRF_ENABLED"] = False

    yield _app

    ctx.pop()


@pytest.fixture(scope='session')
def client(app):
    """ Exposes the Werkzeug test client for use in the tests. """
    with app.test_client() as client:
        with client.session_transaction() as sess:
            sess['user_id'] = "test"
    return client


@pytest.fixture(scope='function', autouse=True)
def db(app):
    mongoengine.disconnect()
    mongoengine.connect('test_db', host='mongomock://localhost')

    yield

    Video.objects.delete()
    User.objects.delete()

    for filename in glob.glob("./static/video/test*"):
        os.remove(filename)


@pytest.fixture(scope='function')
def user(db):
    user = User(first_name="Person", last_name='One',
                email='test_user1@test.com',
                password=generate_password_hash("Test_password1"),
                email_verified=True)
    user.save()
    return user


@pytest.fixture(scope='class')
def driver(request):
    options = EdgeOptions()
    options.add_argument('--no-sandbox')
    options.add_argument('--headless')
    options.add_argument('--disable-dev-shm-usage')
    driver = webdriver.Edge(EdgeChromiumDriverManager().install(),
                            options=options)
    request.cls.driver = driver
    yield
    driver.close()


@pytest.fixture(scope='class')
def run_app(app):
    # Fixture for running flask app with selenium webdriver
    process = multiprocessing.get_context('fork').Process(target=app.run,
                                                          args=())
    process.start()

    yield process
    process.terminate()
