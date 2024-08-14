# SmartDoc
There are three elements within this SmartDoc series: SmartPM, SmartPMHTML, and SmartMentorship. SmartPM opens a tikz wizard that allows the user to enter in the necessary information to automate an electron microscope preventitive maintenance procedure. SmartPMHTML does the same thing, except it's run through HTML, meaning it hosts a development server on your local machine (a website) to have you enter this information in. SmartMentorship operates the same way as SmartPMHTML, except with a different purpose. Its is to automate the mentorship checklist required for a new engineer to be able to work on certain EM machines.

## Purpose:
In general, this project was undertaken to try and automate and simplify how engineers conduct PMs and mentorship by creating an API that pulls known but difficult to access information from SmartSEM.

## Note:
The programs compiling the LaTeX templates make a lot of temporary and placeholder files. Also, to be able to compile these .tex files into .pdfs, miktex is required.

## Glossary:
Folders
- SmartMentorship: Where all of the SmartMentorship related items are located.
    - static: Flasks folder naming conventions for images
    - templates: Flasks folder naming conventions for html documents
- SmartPM: Where all  the SmartPM related items are located
- SmartPMHTML: Where all the SmartPMHTML related items are located
    - static: Flasks folder naming conventions for images
    - templates: Flasks folder naming conventions for html documents