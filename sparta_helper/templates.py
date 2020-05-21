from pathlib import Path

class Email:
    @staticmethod
    def soundtrap(first_name, email, password):
        plain_text = (
            f'Hey there {first_name}, I have some great news, your soundtrap account'
            ' is officially all ready to go! Thank you for signing up, and I hope you e'
            'njoy playing around with this exciting music making platform! Here is your '
            f'username and password:\n\nUsername:\t\t{email}\nPassword:\t\t{password}'
            '\n\nThanks again for signing up, and I hope you enjoy Sountrap! You can log in '
            'to soundtrap at https://www.soundtrap.com/edu. Also, check out Zach Vergano\'s '
            'compositions available in the google drive folder below. They are truly outstanding, '
            'and I hope that they will inspire you to make similar compositions of your own.'
            '\n\nhttps://drive.google.com/open?id=1ZxxnYHUbDEh7XI8Pa_42plrDjAzpIjRW\n\nHave fun!!'
        )

        with open('/Users/JohnDeVries/repos/teacher_helper/sparta_helper/html_email_templates/soundtrap_account_ready.html', 'r') as html_io:
            html = html_io.read()
        return plain_text, html

if __name__ == "__main__":
    import pyperclip
    pyperclip.copy(Email.soundtrap('test', 'test', 'test')[0])