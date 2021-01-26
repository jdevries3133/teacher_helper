<h1 id="paychex">Paychex</h1>

> Here is documentation on more specific methods which I later removed
> from the top-level readme because it seemed gratuitous.

### Overview

Paychex class can clock in and out of paychex using headless Google Chrome,
selenium, and chromedriver.

### Methods

**`self.login(self)`**

Launch headless chrome and login to paychex. Unless you setup the Imap module
to get your OTP from your email, you will have to input it. This method does
not necessarily need to be called, because functions that require you to login
are protected by the `@login_first` decorator, which checks for `self.is_logged_in`
and calls this method if not.

**`self.get_clock_state(self)`**

This returns the **LOCALLY CACHED** clock state. Can be used to check whether
the Browser should be opened, or to query the user for whether they want to
clock in or out when it's ambiguous.

**`self.set_clock_state(self)`**

This opens the browser, logs in, and gets the clock state from the website.
It does not take any arguments, or allow the state to by manually overridden.

**`@ login_first` decorator**

These methods will check whether `self.is_logged_in` is true and run
`self.login` if necessary.
