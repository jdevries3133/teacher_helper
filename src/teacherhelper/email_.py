from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from pathlib import Path
import shutil
import smtplib
import ssl
import os

import markdown

from ._data_dir import DATA_DIR


class Email:
    def __init__(self, username=None, password=None):
        self.email_addr = username or os.getenv('EMAIL_USERNAME', '')
        self.password = password or os.getenv('EMAIL_PASSWORD', '')
        self.connection = None

        # create ~/.teacherhelper/email_templates if needed
        self.template_dir = Path(
            DATA_DIR,
            '.teacherhelper',
            'email_templates'
        )
        if not self.template_dir.exists():
            os.makedirs(self.template_dir)
        default_template = Path(self.template_dir, 'default.html')
        if not default_template.exists():
            shutil.copyfile(
                Path(Path(__file__).parent, 'email_default_template.html'),
                default_template
            )

    def __enter__(self):
        context = ssl.create_default_context()
        self.connection = smtplib.SMTP_SSL(
            'smtp.gmail.com',
            port=465,
            context=context,
        )
        self.connection.login(
            self.email_addr,
            self.password,
        )
        return self

    def __exit__(self, *_):
        if self.connection:
            self.connection.close()
        self.connection = None

    def send(
        self,
        *,
        to: str,
        subject: str,
        message: str,
        cc: str=None,       # TODO: should support a list
        bcc: str=None,      # TODO: should support a list
        template_name: str='default.html'
    ):
        """
        Simple utility for sending an email. Helpful for mail merges!

        *message* should be a string of markdown text, which will be
        converted into html and plain text email attachments.

        *template_name* is the name of an html email template in
        ~/.teacherhelper/email_templates. An email template can be any html
        file with the template tag `{{ email_content }}` in it. The markdown
        input will be converted into html, and that html will replace the
        `{{ email_content }}` tag.
        """
        if not self.connection:
            raise ValueError(
                'Connection must be established in __enter__. Use this class '
                'as a context manager'
            )
        me = self.email_addr
        msg = MIMEMultipart('alternative')
        msg['Subject'] = subject
        msg['From'] = me
        msg['To'] = to
        if cc:
            msg['Cc'] = cc
        if bcc:
            msg['Bcc'] = bcc

        html = self.make_html_message(message, template_name)

        part1 = MIMEText(message, 'plain')
        part2 = MIMEText(html, 'html')
        msg.attach(part1)
        msg.attach(part2)
        self.connection.sendmail(me, to, msg.as_string())

    def make_html_message(
            self,
            markdown_message: str,
            template_name: str='default.html',
    ):
        template_path = Path(self.template_dir, template_name)

        with open(template_path, 'r') as fp:
            template = fp.read()
            html = template.replace('{{ email_content }}', markdown.markdown(markdown_message))

        return html
