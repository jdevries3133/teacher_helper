from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText


class Email:
    def __init__(self, username, password):
        self.username = username
        self.password = password
        self.templated_loaded = False
        self.template_filled = False

    def email(self, students, template_flag):
        if template_flag == 'soundtrap':

            no_pass = [s for s in students if not hasattr(s, 'soundtrap_password')]
            if no_pass:
                nl = '\n'
                raise Exception(
                    f'The following students do not have a password '
                    f'assigned to them:\n{[(i.name + nl) for i in no_pass]}'
                )

            # init ssl
            context = ssl.create_default_context()
            with smtplib.SMTP_SSL('smtp.gmail.com', port=465, context=context) as server:
                server.login(
                    os.getenv('GMAIL_USERNAME'),
                    os.getenv('GMAIL_PASSWORD'),
                )

                for st in students:
                    me = 'john.devries@sparta.org'
                    you = st.email

                    msg = MIMEMultipart('alternative')
                    msg['Subject'] = 'Your Soundtrap Account is Ready!'
                    msg['From'] = me
                    msg['To'] = you
                    text, html = Email.soundtrap_template(st.first_name, st.email, st.soundtrap_password)

                    part1 = MIMEText(text, 'plain')
                    part2 = MIMEText(html, 'html')

                    msg.attach(part1)
                    msg.attach(part2)

                    resp = server.sendmail(me, you, msg.as_string())
                    print(resp)
        return 0

    def import_template(self, html_path, plaintext_path, context, strict=True):
        """
        Import an html email template at the path. Check for valid html,
        ensure that context fields exist in the html and plaintext emails.
        """
        pass