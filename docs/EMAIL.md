# Easy Email Wrapper

The email module allows you to send emails through your own email address via
SMTP very easily. Note that if you use gmail with two factor authentication,
you will need to
[create an app password](https://support.google.com/accounts/answer/185833?hl=en)
to make this work. Otherwise, and for most email clients, the username and
password you normally use to login will do the trick!

## `teacherhelper.Email` Class Reference

### `Email.__init__(self, username=None, password=None)`

Returns a new Emailer instance, ready to create an SMTP connection with the
provided credentials. `__init__` will also create the `email_templates`
subdirectory inside of `HELPER_DATA` if it doesn't already exist. `HELPER_DATA` is
`~/.teacherhelper` unless you have defined another location as an environment
variable.

### `Email.__enter__` and `Email.__exit__`

`Email` should be used as a context manager. The SMTP connection will be opened
inside the context manager and closed upon exiting. If you try to use the
`.send` method without `__enter__` first having been called, a `ValueError`
will be raised.

### `Email.send(...)`

Full Signature:

```python
    def send(
        self,
        *,
        to: str,
        subject: str,
        message: str,
        cc: str=None,       # TODO: should support a list
        bcc: str=None,      # TODO: should support a list
        template_name: str='default.html'
    ): ...
```

Simple utility for sending an email. Helpful for mail merges!

_message_ should be a string of markdown text, which will be converted into
html and plain text email attachments.

_template_name_ is passed to `Email.make_html_message`.

### `make_html_message(...)`

Full signature:

```python
def make_html_message(
        self,
        markdown_message: str,
        template_name: str='default.html',
): ...
```

_template_name_ is the name of an html email template in the
`$HELPER_DATA/email_templates` directory. An email template can be any html file
with the literal substring `{{ email_content }}` in it. _markdown_message_ will
be converted into html, and that html will replace the `{{ email_content }}`
tag.

This library comes with a default template named `default.html`. It will be
copied to `$HELPER_DATA/email_templates/default.html`, and you can use that as
a starting point for customization or replace it with your own template.
