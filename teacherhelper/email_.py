from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from pathlib import Path
import shutil
import smtplib
import ssl
import os
from typing import Union

import markdown

from ._data_dir import get_data_dir


class Email:
    def __init__(self, username=None, password=None):
        self.email_addr = username or os.getenv("EMAIL_USERNAME", "")
        self.password = password or os.getenv("EMAIL_PASSWORD", "")
        self.connection = None

        # create ~/.teacherhelper/email_templates if needed. Copy the default
        # template into there if it doesn't already exist
        self.template_dir = get_data_dir() / ".teacherhelper" / "email_templates"
        if not self.template_dir.exists():
            os.makedirs(self.template_dir)
        default_template = Path(self.template_dir, "default.html")
        if not default_template.exists():
            shutil.copyfile(
                Path(Path(__file__).parent, "default_email_template.html"),
                default_template,
            )

    def __enter__(self):
        context = ssl.create_default_context()
        self.connection = smtplib.SMTP_SSL(
            "smtp.gmail.com",
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
        to: Union[str, list],
        subject: str,
        message: str,
        cc: Union[list, str] = "",
        bcc: Union[list, str] = "",
        template_name: str = "default.html"
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
        # ensure that to, cc, and bcc are strings
        to = to if isinstance(to, str) else ", ".join(to)
        cc = cc if isinstance(cc, str) else ", ".join(cc) if cc else ""
        bcc = bcc if isinstance(bcc, str) else ", ".join(bcc) if bcc else ""

        if not self.connection:
            raise ValueError(
                "Connection must be established in __enter__. Use this class "
                "as a context manager"
            )
        me = self.email_addr
        msg = MIMEMultipart("alternative")
        msg["Subject"] = subject
        msg["From"] = me
        msg["To"] = to
        if cc:
            msg["Cc"] = cc
        if bcc:
            msg["Bcc"] = bcc

        html = self.make_html_message(message, template_name)

        part1 = MIMEText(message, "plain")
        part2 = MIMEText(html, "html")
        msg.attach(part1)
        msg.attach(part2)
        self.connection.sendmail(me, to, msg.as_string())

    def make_html_message(
        self,
        markdown_message: str,
        template_name: str = "default.html",
    ):
        template_path = Path(self.template_dir, template_name)

        with open(template_path, "r") as fp:
            template = fp.read()
            html = template.replace(
                "{{ email_content }}", markdown.markdown(markdown_message)
            )

        return html
