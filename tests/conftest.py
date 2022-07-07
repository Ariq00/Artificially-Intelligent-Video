import pytest
from selenium import webdriver
from selenium.webdriver import EdgeOptions
from webdriver_manager.microsoft import EdgeChromiumDriverManager
import multiprocessing
from setup_app import create_app
import mongoengine
from models import Video, User
from werkzeug.security import generate_password_hash


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
    return app.test_client()


@pytest.fixture(scope='function', autouse=True)
def db(app):
    mongoengine.disconnect()
    mongoengine.connect('test_db', host='mongomock://localhost')
    yield

    Video.objects.delete()
    User.objects.delete()


@pytest.fixture(scope='function')
def user(db):
    """ Creates a user without a profile. """
    user = User(first_name="Person", last_name='One',
                email='test_user1@test.com',
                password=generate_password_hash("test_password"))
    user.save()
    return user


@pytest.fixture(scope='class')
def driver(request):
    options = EdgeOptions()
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
