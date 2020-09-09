# Helper.do_stuff

## Work in Progress

In the midst of major refactor. The code is the documentation.

## from helper.paychex import Paychex

### Overview

Paychex class can clock in and out of paychex. `__init__` takes two positional
arguments; `username`, and `password`.

### Methods

**`self.clock()`**

This is the primary top-level function – the one that is called by passing
"clock" as a single argument to the shell. It takes into consideration the time
of day, cached clock state, and real site state, and makes a determination about
whether to press the button or not. It then updates the clock state and closes
the headless browser.

**`self.login()`**

Launch headless chrome and login to paychex. Unless you setup the Imap module
to get your OTP from your email, you will have to input it.

**`self.clock_in()`**

Clock in. The @login_first decorator is applied, so if you haven't done that yet,
it will happen upon calling this method.

This method does not mindlessly press the button in paychex. It first reads the
DOM and checks if you're already clocked in. It may push the button, or may just
close the borwser if you're already clocked in. Either way,
**you will be clocked in when all is said and done**

**`self.clock_out()`**

Same as clock in, but clock out.

**`self.get_clock_state()`**

This returns the **LOCALLY CACHED** clock state. Can be used to check whether
the Browser should be opened.

**`self.set_clock_state()`**

This opens the browser, logs in, and gets the clock state from the website.
It does not take any arguments, or allow the state to by manually overridden.

**`@login_first decorator`**

These methods will check whether `self.is_logged_in` is true.
