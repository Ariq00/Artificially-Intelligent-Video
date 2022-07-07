import pytest
from selenium import webdriver
from selenium.webdriver import ChromeOptions
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
                password=generate_password_hash("password1"))
    user.save()
    return user


@pytest.fixture(scope='class')
def chrome_driver(request):
    """ Fixture for selenium webdriver with options to support running in
    GitHub actions """
    options = ChromeOptions()
    options.add_argument("--headless")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--disable-gpu")
    options.add_argument("--start-maximized")
    # options.add_argument("--window-size=1920,1080")
    options.add_argument("--window-size=1200x600")
    chrome_driver = webdriver.Chrome(options=options)
    request.cls.driver = chrome_driver
    yield
    chrome_driver.close()


@pytest.fixture(scope='class')
def run_app(app):
    """
    Fixture to run the Flask app
    """
    process = multiprocessing.Process(target=app.run, args=())
    process.start()
    yield process
    process.terminate()
