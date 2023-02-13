from flask import Flask, request, redirect, render_template, session, flash, json, url_for
from flask_session import Session
from helpers import login_required, eur
from cs50 import SQL
from werkzeug.security import check_password_hash, generate_password_hash

# Configure application
app = Flask(__name__)

# Custom filter
app.jinja_env.filters["eur"] = eur

# Configure session to use filesystem (instead of signed cookies)
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
app.jinja_env.auto_reload = True
app.config["TEMPLATE_AUTO_RELOAD"] = True
app.config["FLASK_DEBUG"] = True

Session(app)

# Configure CS50 Library to use SQLite database
db = SQL("sqlite:///expenseTraker.db")

# Expense categories
CATEGORIES = [
    "Activities",
    "Bills",
    "Car",
    "Clothes",
    "Eating Out",
    "Education",
    "Gifts",
    "Groceries",
    "Health",
    "Hobbies",
    "Holidays",
    "Pets",
    "Pharmacy",
    "Phone",
    "Public Transportation",
    "Rent",
    "Taxi/Uber",
    "Other",
]

# Income Categories
INCOME = [
    "Gift",
    "Investement",
    "Salary",
    "Other",
]


@app.after_request
def after_request(response):
    """Ensure responses aren't cached"""
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response.headers["Expires"] = 0
    response.headers["Pragma"] = "no-cache"
    return response


@app.route("/login", methods=["GET", "POST"])
def login():
    
    # Forget any user_id
    session.clear

    if request.method == "POST":

        # Get data submitted
        username = request.form.get("username")
        password = request.form.get("password")

        # Ensure username was submited
        if not username:
            flash("Must provide username", category="error")
        
        # Ensure password was submitted
        elif not password:
            flash("Must provide password", category="error")

        # Query db data
        data = db.execute("SELECT * FROM users WHERE username = ?", username)

        # Confirm that username exists and password id correct
        if len(data) != 1 or not check_password_hash(data[0]["hash"], password):
            flash("Invalid username and/or password", category="error")
            return redirect("/login")

        # Remember which user has logged in
        session["user_id"] = data[0]["id"]

        # Redirect user to homepage
        flash("Logged in successfully!", category="success")
        return redirect("/")
    
    # User reached route via GET
    else:
        return render_template("login.html")


@app.route("/register", methods=["GET", "POST"])
def register():

    # User reached via POST
    if request.method == "POST":

        # Get data submited
        username = request.form.get("username")
        password = request.form.get("password")
        confirmation = request.form.get("confirmation")

        # Query db for username
        dbusers = db.execute("SELECT username FROM users WHERE username = ?", username)

        # Ensure username is unique
        if len(dbusers) != 0:
            flash("Username already taken", category="error")

        # Ensure that username is at least 2 characteres long
        elif len(username) < 2:
            flash("Username must be at least 2 characters", category="error")

        # Ensure that password is at least 8 characters long    
        elif len(password) < 8:
            flash("Password must be at least 8 characters", category="error")

        # Confirm that passwords match    
        elif password != confirmation:
            flash("Passwords do not match", category="error")
        
        else:
            # Generate password hash
            hash = generate_password_hash(password)
            
            # Insert new user in the db
            db.execute("INSERT INTO users (username, hash) VALUES (?, ?)", username, hash)
            flash("Acount created!", category="success")
            return redirect("/login")
        
        return redirect("/register")
    
    # User reached route via GET
    else:
        return render_template("register.html")

@app.route("/logout")
@login_required
def logout():

    # Foerget any user_id
    session.clear()

    # Redirect user to login form
    return redirect("/")
    
@app.route("/", methods=["GET", "POST"])
@login_required
def index():

    if request.method == "POST":
        
        date = request.form.get("date")        

        # Get all the expenses grouped by categories fiterd by month
        expenses = db.execute("SELECT category, SUM (amount), date FROM movements WHERE user_id = ? AND action = 'expense' AND STRFTIME('%Y-%m', date) = ? GROUP BY category;", session["user_id"], date)

        # Get all movements from user
        movements = db.execute("SELECT * FROM movements WHERE user_id = ? AND STRFTIME('%Y-%m', date) = ? ORDER BY date DESC, movement_id DESC", session["user_id"], date)

        # Get overall expenses and income fiterd by month
        tot_exp = db.execute("SELECT SUM(amount) AS total_expenses FROM movements WHERE action = 'expense' AND user_id = ? AND STRFTIME('%Y-%m', date) = ?", session["user_id"], date)[0]["total_expenses"]

        tot_inc = db.execute("SELECT SUM(amount) AS total_income FROM movements WHERE action = 'income' AND user_id = ? AND STRFTIME('%Y-%m', date) = ?", session["user_id"], date)[0]["total_income"]

        # Get balance from user fiterd by month
        if tot_inc == None:
            tot_inc = 0.00
        if tot_exp == None:
            tot_exp = 0.00
        
        balance = tot_inc + tot_exp
        
        labels = []
        data = []

        for i in range(len(expenses)):
            labels.append(expenses[i]["category"])
            data.append(-expenses[i]["SUM (amount)"])



        return render_template("index.html", categories=CATEGORIES, income=INCOME, labels=labels, data=data, expenses=expenses, date=date, movements=movements, balance=balance, tot_exp=tot_exp, tot_inc=tot_inc)

    else:
        # Get all the expenses grouped by categories
        expenses = db.execute("SELECT category, SUM (amount) FROM movements WHERE user_id = ? AND action = 'expense' GROUP BY category;", session["user_id"])

        # Get all movements from user
        movements = db.execute("SELECT * FROM movements WHERE user_id = ? ORDER BY date DESC, movement_id DESC", session["user_id"])

        # Get balance from user 
        balance = db.execute("SELECT balance FROM users WHERE id = ?", session["user_id"])[0]["balance"]

        # Get overall expenses and income
        tot_exp = db.execute("SELECT SUM(amount) AS total_expenses FROM movements WHERE action = 'expense' AND user_id = ?", session["user_id"])[0]["total_expenses"]

        tot_inc = db.execute("SELECT SUM(amount) AS total_income FROM movements WHERE action = 'income' AND user_id = ?", session["user_id"])[0]["total_income"]

        if tot_inc == None:
            tot_inc = 0.00
        if tot_exp == None:
            tot_exp = 0.00

        labels = []
        data = []

        for i in range(len(expenses)):
            labels.append(expenses[i]["category"])
            data.append(-expenses[i]["SUM (amount)"])



        return render_template("index.html", categories=CATEGORIES, income=INCOME, labels=labels, data=data, expenses=expenses, movements=movements, balance=balance, tot_exp=tot_exp, tot_inc=tot_inc)


@app.route("/delete/<id>/<amount>")
@login_required
def delete(id, amount):

    # Delete expense/income from DB
    db.execute("DELETE FROM movements WHERE movement_id = ?", id)

    # Update balace 
    db.execute("UPDATE users SET balance = balance - ? WHERE id = ?", amount, session["user_id"])
    
    return redirect("/")

@app.route("/edit-expense", methods=["POST"])
@login_required
def edit_expense():
    
    # Get the data
    id = request.form.get("m_id")
    category = request.form.get("category")
    description = request.form.get("description")
    amount = request.form.get("amount")
    date = request.form.get("date")

    # Ensure that form provides ID
    if not id:
        flash("No id was submited", category="error")

    # Ensure that user provides category
    elif not category:
        flash("Must specify category!", category="error")
    
    # Ensure that user provides amount
    elif not amount:
        flash("Must specify amount!", category="error")

    # Ensure that amount is grater than 0
    elif float(amount) < 0:
        flash("Amount must be greater that 0", category="error")
    
    # Ensure that user provides date
    elif not date:
        flash("Must specify date", category="error")

    else:
        amount = float(amount)
        init_amount = db.execute("SELECT amount FROM movements WHERE movement_id = ? AND user_id = ?", id, session["user_id"])[0]["amount"]
        delta_amount = (-init_amount) - amount
        db.execute("UPDATE movements SET category = ?, description = ?, amount = ?, date = ? WHERE movement_id = ? AND user_id = ?", category, description, -amount, date, id,session["user_id"])
        db.execute("UPDATE users SET balance = balance + ? WHERE id = ?", delta_amount, session["user_id"])
        flash("Expense edited successfully!", category="success")
        return redirect("/")

    return redirect("/")
        
@app.route("/edit-income", methods=["POST"])
@login_required
def edit_income():
    
    # Get the data
    id = request.form.get("m_id")

    category = request.form.get("category")
    description = request.form.get("description")
    amount = request.form.get("amount")
    date = request.form.get("date")

    # Ensure that form provides ID
    if not id:
        flash("No id was submited", category="error")

    # Ensure that user provides category
    elif not category:
        flash("Must specify category!", category="error")
    
    # Ensure that user provides amount
    elif not amount:
        flash("Must specify amount!", category="error")

    # Ensure that amount is grater than 0
    elif float(amount) < 0:
        flash("Amount must be greater that 0", category="error")
    
    # Ensure that user provides date
    elif not date:
        flash("Must specify date", category="error")

    else:
        amount = float(amount)
        init_amount = db.execute("SELECT amount FROM movements WHERE movement_id = ? AND user_id = ?", id, session["user_id"])[0]["amount"]
        delta_amount = amount - init_amount
        db.execute("UPDATE movements SET category = ?, description = ?, amount = ?, date = ? WHERE movement_id = ? AND user_id = ?", category, description, amount, date, id,session["user_id"])
        db.execute("UPDATE users SET balance = balance + ? WHERE id = ?", delta_amount, session["user_id"])
        flash("Expense edited successfully!", category="success")
        return redirect("/")
    
    return redirect("/")


@app.route("/add-expense", methods=["POST"])
@login_required
def add_expense():

    if request.method == "POST":

        # Get the data
        category = request.form.get("category")
        description = request.form.get("description")
        amount = request.form.get("amount")
        date = request.form.get("date")

        # Ensure that user provides category
        if not category:
            flash("Must specify category!", category="error")
        
        # Ensure that user provides amount
        elif not amount:
            flash("Must specify amount!", category="error")

        # Ensure that amount is grater than 0
        elif float(amount) < 0:
            flash("Amount must be greater that 0", category="error")
        
        # Ensure that user provides date
        elif not date:
            flash("Must specify date", category="error")

        else:
            amount = float(amount)
            # Insert expense in db
            db.execute("INSERT INTO movements (user_id, category, description, amount, action, date) VALUES (?, ?, ?, ?, ?, ?)", session["user_id"], category, description, -amount, "expense", date)
            db.execute("UPDATE users SET balance = (balance - ?) WHERE id = ?", amount, session["user_id"])
            return redirect("/")
        
        return redirect("/")

@app.route("/add-income", methods=["POST"])
@login_required
def add_income():

    if request.method == "POST":

        # Get the data
        category = request.form.get("category")
        description = request.form.get("description")
        amount = request.form.get("amount")
        date = request.form.get("date")

        # Ensure that user provides category
        if not category:
            flash("Must specify category!", category="error")
        
        # Ensure that user provides amount
        elif not amount:
            flash("Must specify amount!", category="error")


        # Ensure that amout is grater than 0
        elif float(amount) < 0:
            flash("Amount must be greater that 0", category="error")

        # Ensure that user provides date
        elif not date:
            flash("Must specify date", category="error")
        
        else:
            amount = float(amount)
            # Insert income in db
            db.execute("INSERT INTO movements (user_id, category, description, amount, action, date) VALUES (?, ?, ?, ?, ?, ?)", session["user_id"], category, description, amount, "income", date)
            db.execute("UPDATE users SET balance = (balance + ?) WHERE id = ?", amount, session["user_id"])
            return redirect("/")
        
        return redirect("/")



if __name__ == '__main__':
    app.run(debugger=True)