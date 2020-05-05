import requests

from .secrets_genesis import Login

def get_session():
    """
    Make a session, and log in
    """
    session = requests.Session()
    session.get('https://genesis.sparta.org/sparta/sis/view?gohome=true')
    request = requests.Request(
        'POST',
        'https://genesis.sparta.org/sparta/sis/j_security_check',
        data={'j_username': Login.username, 'j_password': Login.password},
    )
    session.send(request.prepare())

    return session
