import os

import requests

def get_session():
    """
    Make a session, and log in
    """
    session = requests.Session()
    session.get('https://genesis.sparta.org/sparta/sis/view?gohome=true')

    username = os.getenv('GENESIS_USERNAME')
    password = os.getenv('GENESIS_PASSWORD')
    if not username or not password:
        raise Exception(
            f'"GENESIS_USERNAME and GENESIS_PASSWORD must be defined environment variables for '
            'genesis authentication.'
        )

    request = requests.Request(
        'POST',
        'https://genesis.sparta.org/sparta/sis/j_security_check',
        data={
            'j_username': username,
            'j_password': password
        },
    )
    session.send(request.prepare())

    return session
