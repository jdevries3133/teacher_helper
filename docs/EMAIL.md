# Emailer

The email module allows you to send emails through your own email address via
SMTP very easily. Note that if you use gmail with two factor authentication,
you will need to
[create an app password](https://support.google.com/accounts/answer/185833?hl=en)
to make this work. Otherwise, and for most email clients, the username and
password you normally use to login will do the trick!

## class `teacherhelper.Email`

### `Email.__init__(self, username=None, password=None)`

Returns a new Emailer instance, ready to create an SMTP connection with the
provided credentials. `__init__` will also create a folder `$HELPER_DATA/email_templates`,
which includes a default email template. You can modify this template if you
want, it won't be overwritten if it exists. See also the [setup guide](../setup)
for details about `$HELPER_DATA`.

### Environment Variables

You can also define environment variables, `EMAIL_USERNAME` and `EMAIL_PASSWORD`
instead of passing these values via the init function.

### Context Manager

`Email` should be used as a context manager. The SMTP connection will be opened
inside the context manager and closed upon exiting. If you try to use the
`.send` method outside the context manager, a `ValueError`
will be raised.

```python
with Email('me@example.com', 'mypass') as emailer:
    ...
```

### `Email.send(...) -> None: ...`

Full signature:

```python
    def send(
        self,
        *,
        to: str,
        subject: str,
        message: str,
        cc: str=None,
        bcc: str=None,
        template_name: str='default.html'
    ): ...
```

Simple utility for sending an email. Helpful for mail merges!

_message_ should be a string of markdown text, which will be converted into a
multipart email with html and plain text attachments.

_template_name_ is passed to `Email.make_html_message`.

### `Email.make_html_message(self, markdown_message: str, template_name: str='default.html')`

_template_name_ is the name of an html email template in the
`$HELPER_DATA/email_templates` directory. An email template can be any html file
with the literal substring `{{ email_content }}` in it. _markdown_message_ will
be converted into html, and that html will replace the `{{ email_content }}`
tag. For the plain text attachment, the literal markdown string is used. This
_will not_ include the html template, so the html template should be
presentational only, and the message should stand alone even if it is not
wrapped in the template content. For example, the template could be used
for a header & footer, email signature, pretty frame around the message, etc.

This library comes with a default template named `default.html`. It will be
copied to `$HELPER_DATA/email_templates/default.html`, and you can use that as
a starting point for customization or replace it with your own template. It
will not be overwritten if it exists, and this action is performed during
`Email.__init__`.
