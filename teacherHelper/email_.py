from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from pathlib import Path
import smtplib
import ssl
import os
import logging

logger = logging.getLogger(__name__)


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
        self.connection.close()

    def send(self, *, to, subject, message: list, html=False):
        """
        Accepts kwargs ONLY

        Send plain text emails en masse.

        Set html, and the message should be a tuple:
            message[0] = plain text
            message[1] = html

        The html will still be inserted into the default template, including
        your signature.
        """
        if not isinstance(message, list):
            raise Exception(
                'Message must be a list; an array of paragraphs. Each string '
                'in the list will be mapped to a <p> tag in the html, or '
                'joined with a double newline in the plain text.'
            )
        if not self.connection:
            raise Exception(
                'Connection must be established in __enter__. Use this class '
                'with a context manager.'
            )
        # init ssl
        me = 'jdevries@empacad.org'
        msg = MIMEMultipart('alternative')
        msg['Subject'] = subject
        msg['From'] = me
        msg['To'] = to
        html, text = self.make_message(message)
        part1 = MIMEText(text, 'plain')
        part2 = MIMEText(html, 'html')
        msg.attach(part1)
        msg.attach(part2)
        self.connection.sendmail(me, to, msg.as_string())

    def make_message(self, message: list, raise_exception=True):
        """
        Make a message with the default html template.
        """
        # load template
        with open(Path(self.template_dir, 'default.html'), 'r') as htmlf:
            html_message = htmlf.read()

        # generate html; text strings become paragraphs and blank strings
        # become <br /> elements.
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
        return (
            html_message.replace('{{insert}}', '\n'.join(html)),
            '\n\n'.join(message)
        )
