from typing import Union, List, NamedTuple
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from pathlib import Path
import smtplib
import ssl
import os
import logging

from bs4 import BeautifulSoup

logger = logging.getLogger(__name__)

class Message(NamedTuple):
    html: str
    plain_text: str

class Email:
    def __init__(self, username=None, password=None):
        self.username:str = username if username else ''
        self.password:str = password if password else ''
        # use my default env variables for username and password if none were
        # passed
        if not self.username and (un := os.getenv('EMAIL_USERNAME')):
            self.username = un
        if not self.password and (pw := os.getenv('EMAIL_PASSWORD')):
            self.password = pw
        self.template_dir = Path(Path(__file__).parent, 'html_email_templates')
        self.connection = None

    def __enter__(self):
        context = ssl.create_default_context()
        self.connection = smtplib.SMTP_SSL(
            'smtp.gmail.com',
            port=465,
            context=context,
        )
        self.connection.login(
            self.username,
            self.password,
        )
        return self

    def __exit__(self, *_):
        if self.connection:
            self.connection.close()

    def send(self, *, to, subject, message: Union[Message, List[str]], cc=None, html=False):
        """
        If message is a list, its strings will be wrapped in <p> tags before
        being inserted into the email.

        If message is a tuple, it will be presumed to be 
        """
        if not self.connection:
            raise Exception(
                'Connection must be established in __enter__. Use this class '
                'as a context manager.'
            )
        # init ssl
        me = 'jdevries@empacad.org'
        msg = MIMEMultipart('alternative')
        msg['Subject'] = subject
        msg['From'] = me
        msg['To'] = to
        if cc:
            msg['Cc'] = cc
        if isinstance(message, list):
            html, plain_text = self.make_message(message)
        elif isinstance(message, Message):
            html, plain_text = message
        else:
            raise TypeError(
                f'Invalid message type: {type(message)}. Message must be of '
                'type list or teacherhelper.email.Message'
            )
        part1 = MIMEText(plain_text, 'plain')
        part2 = MIMEText(html, 'html')
        msg.attach(part1)
        msg.attach(part2)
        self.connection.sendmail(me, to, msg.as_string())

    def make_message(self, message: Union[list, str], *, template: Path=None):
        """
        Make a message with an html tempalte. A list will be interpreted
        as a list of paragraphs to be inserted while a string is expected
        to be html text ready to be fully inserted.
        """
        if not template:
            template = Path(self.template_dir, 'default.html')
        # load template
        with open(template, 'r') as htmlf:
            html_template = htmlf.read()

        if isinstance(message, list):
            # generate html paragraphs from list of strings
            html = []
            for i in message:
                if i:
                    html.append(
                        "<p style=\"color: black; font-family: Helvetica, Arial, Sans-Serif;\">"
                          f"{i}"
                        "</p>"
                    )
                else:
                    html.append('<br />')
            html = '\n'.join(html)
            message = '\n\n'.join(message)
        elif isinstance(message, str):
            # presume string should be directly inserted; already valid html
            html = message
            message = '\n'.join(BeautifulSoup(message, features='lxml').findAll(text=True))
        else:
            raise TypeError(
                f'Invalid message type: {type(message)}. Message must be of '
                'type list or str'
            )
        return (
            html_template.replace('{{ email_content }}', html),
            message
        )
