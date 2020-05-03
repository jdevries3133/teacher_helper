## Getting it to work
# Naming convention for source data
Source data must be named in a specific way. A filename should consist of three
specific parts:
```
[flag (-h or -g)] [grade level] [name (of teacher or group)]
```
For example,
```
-h3Masterson.csv
```
A "-h" and "-g" flags tells the program to parse students as homerooms or groups,
respectively. Homerooms have more academic-related methods, like automatically
following up on missing grades, whereas groups should be used for extracurricular
or sports groups. They include methods appropriate to those cases.

In terms of the header row, as long as the headers include ```ID``` and ```name```,
there is a method for getting everything else through the web API.

