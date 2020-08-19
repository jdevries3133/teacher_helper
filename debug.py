"""
VS Code debug utility will run this file
"""
import os
from helper.paychex import Paychex

pcx = Paychex(
    os.getenv('PAYCHEX_USR'),
    os.getenv('PAYCHEX_PASS')
)
pcx.login()
pcx.driver.close()