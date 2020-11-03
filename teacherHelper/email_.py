from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from pathlib import Path
import smtplib
import ssl
import os


class Email:
    def __init__(self, username=None, password=None):
        self.username = username
        self.password = password
        # use my default env variables for username and password if none were
        # passed
        if not self.username:
            self.username = os.getenv('EMAIL_USERNAME')
        if not self.password:
            self.password = os.getenv('EMAIL_PASSWORD')
        self.template_dir = Path(Path(__file__).parent, 'html_email_templates')

    def send(self, to, subject, message: list, html=False):
        """
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
        # init ssl
        context = ssl.create_default_context()
        with smtplib.SMTP_SSL('smtp.gmail.com', port=465, context=context) as server:
            server.login(
                self.username,
                self.password
            )
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
            server.sendmail(me, to, msg.as_string())

    def make_message(self, message):
        """
        Make a message with the default html template.
        """
        # html
        with open(Path(self.template_dir, 'default.html'), 'r') as htmlf:
            html_message = htmlf.read()
        paragraphs = '\n'.join([
            f"<p style=\"font-family: Helvetica, Arial, Sans-Serif;\">{i}</p>"
            for i in message
        ])
        return html_message.replace('{{insert}}', paragraphs), '\n\n'.join(message)
