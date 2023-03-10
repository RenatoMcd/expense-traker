# Expense Tracker
#### Video Demo:  <https://youtu.be/6qHpi3hsOp8>
## Description:

For the final project I decided to build a simple web app built with Python, Flask, and SQLite3 for tracking expenses and income.

### Prerequisites

Before you get started, make sure you have the following software installed on your computer:

- [Python 3](https://www.python.org/downloads/)
- [Flask](http://flask.pocoo.org/docs/1.0/installation/)
- [SQLite3](https://www.sqlite.org/index.html)

### Features

In this app you can:

- Register and login so that all your data will be stored under your session.
- Add expenses (simply click on the `Add Expense` button, fill in the category, date, description and amount and it will be added to the table)
- Add income (click on the `Add Income` button, and fill the same parameters)
- View current balance, total expenses and total income
- View total expenses grouped by categories in a doughnut graph using Chart.js
- Filter data by month (simply select the month and all the data will be filtered only the movements of the selected month)
- Reset previous filters (click the reset button under the month selector input and it will be showcasing the total amounts again)
- View detailed table of all movements (date, actegory, description, amount)
- Delete or edit expenses or income


#### app.py:
In app.py we have 9 main functions:
1. <u>login():</u>
    - Fill in your username and password, and it will check in the database if they match
    - If you forget to fill in one of the inputs a message will flash giving you feedback
2. <u>register():</u>
    - Fill in your desired username and password and confirm the password in the last field.
    - If the username was not taken, and the passwords match it will add you in the database, otherwise a message will be flashed giving you feedback.
3. <u>logout():</u>
    - Clears the session
4. <u>index():</u>
    - If accessed via `GET`:
        - Queries the database for ***all*** the expenses and income inputed by the user and renders index.html passing the data that was queried
    - If accessed via `POST`:
        - Queries the database for the expenses and income inputed in the ***selected month*** and renders index.html passing the data that was queried
5. <u>delete(id, amount):</u>
    - Using the id and amount passed via the HTTP request, deleted the expense or income from the database and updates the users' balace
6. <u>edit_expense():</u>
    - Using the movement_id, updates the expense taking into acount the new data filled in by the user
    - Updates the balance acordingly
7. <u>edit_income():</u>
    - Using the movement_id, updates the income taking into acount the new data filled in by the user
    - Updates the balance acordingly
8. <u>add_expense():</u>
    - Adds the expense taking into acoount the data filled in by the user
    - If you forget or incorrectly fill in one of the inputs a message will flash giving you feedback
9. <u>add_income():</u>
    - Adds the income taking into acoount the data filled in by the user
    - If you forget or incorrectly fill in one of the inputs a message will flash giving you feedback

#### helpers.py:
In helpers. py we have 2 funtions:
1. <u>login_required(f):</u>
    - this is used as a decorator in the app.py functions that required a user session in order to run correctly
2. <u>eur(value):</u>
    - used to make a jinja finter to format a value into a currency like value

