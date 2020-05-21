from .helper import Helper

import os

if not os.getenv('GENESIS_USERNAME'):
    print('WARN: "GENESIS_USERNAME" should be a defined environment variable for genesis authentication.')

if not os.getenv('GENESIS_PASSWORD'):
    print('WARN: "GENESIS_PASSWORD" should be a defined environment variable for genesis authentication.')