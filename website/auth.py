from flask import Blueprint, render_template, request, flash, redirect, url_for
from .models import User, Tutor, Tutee, Administrator
from .views import uniquebooking, id_to_name
from flask_login import login_user, login_required, logout_user, current_user
import sqlite3 as s

auth = Blueprint('auth', __name__, template_folder="templates")  # works like a mold for flask


# all the methods and routes regarding authentication
def find_load(email):  # combining database tables of all account types to find a specific account using email
    conn = s.connect("tutoring.db")
    c = conn.cursor()
    c.execute("""SELECT email, firstname, password FROM Tutors WHERE email = ? 
                      UNION SELECT email, firstname, password FROM Tutees WHERE email = ? 
                      UNION SELECT email, firstname, password FROM Administrators WHERE email = ?""",
              (str(email), str(email), str(email)))
    data = c.fetchone()
    c.close()
    if data is None:
        return None
    else:
        return User(data[0], data[1], data[2]) # returns the data using the User class

def find_user(role, email): # passing in role and email parameters to find a user from a specific account type
    conn = s.connect("tutoring.db")
    c = conn.cursor()
    if role == "Tutor":
        c.execute('SELECT email, firstname, password FROM Tutors WHERE email = ?', (email,))
        data = c.fetchone()
        if data is None:
            return None
        else:
            return Tutor(data[0], data[1], data[2], 0, 0, 0)
    elif role == "Tutee":
        c.execute('SELECT email, firstname, password FROM Tutees WHERE email = ?', (email,))
        data = c.fetchone()
        if data is None:
            return None
        else:
            return Tutee(data[0], data[1], data[2])
    elif role == "Administrator":
        c.execute('SELECT email, firstname, password FROM Administrators WHERE email = ?', (email,))
        data = c.fetchone()
        if data is None:
            return None
        else:
            return Administrator(data[0], data[1], data[2])  # data returned in different OOP classes
    c.close()


# creates a route to the webpage with url '/login' and the template "login.html"
# GET = request data, POST = submit data
@auth.route('/login', methods=['GET', 'POST'])  # they are HTTP methods allowing the webpage to send and receive data
def login():  # method for the login poge
    if request.method == 'POST':
        role = request.form.get('role')  # fetching inputs from the html form
        email = request.form.get('email')
        password = request.form.get('password')

        user = find_user(role, email)  # filter all the user that have this email here, return the first result
        if user:
            if str(user.password) == str(password):  # comparing the password linked to the email in the database to the input
                flash('Logged in successfully!', category='success')
                login_user(user)
                if role == "Administrator":
                    return redirect(url_for('views.administratorhome'))  # redirecting to the homepage corresponding to account type
                elif role == "Tutor":
                    return redirect(url_for('views.tutorhome'))
                elif role == "Tutee":
                    return redirect(url_for('views.tuteehome'))
            else:
                flash('Incorrect password, try again', category='error')
        else:
            flash('Email does not exist', category='error')
    return render_template("login.html", user=current_user)

# creates a route to the webpage with url '/logout' and redirects to the url used for login
@auth.route('/logout')
@login_required  # a login is required for this action
def logout():
    logout_user()  # calls the flask method to log out user and to clean up any cookies from the user session
    return redirect(url_for('auth.login'))  # redirecting to default page when logging out

# creates a route to the webpage with url '/sign-up' and redirects to the template "sign_up.html"
@auth.route('/sign-up', methods=['GET', 'POST'])
def sign_up():
    if request.method == 'POST':
        role = request.form.get('role')  # taking in inputs from the html form
        email = request.form.get('email')
        first_name = request.form.get('firstName')
        password1 = request.form.get('password1')
        password2 = request.form.get('password2')

        user = find_user(role, email)  # calls the find_user function to look for a matching user

        if user:
            flash('Email already exists', category='error')  # error checking for inputs
        elif len(email) < 4:
            flash('Email must be greater than 4 characters.', category='error')
        elif len(first_name) < 2:
            flash('First Name must be greater than 1 character.', category='error')
        elif len(password1) < 7:
            flash('Password must be greater than 7 characters', category='error')
        elif password1 != password2:
            flash('Passwords do not match.', category='error')
        else:
            # add user to database table according to account type
            conn = s.connect("tutoring.db")
            c = conn.cursor()
            if role == "Tutor":
                c.execute("""INSERT INTO Tutors (email, firstname, password)
                VALUES (:email, :firstname, :password)""",
                          {
                              'email': email,
                              'firstname': first_name,
                              'password': password1,
                          })
                conn.commit()
                conn.close()
                flash('Account successfully created!', category='success')
                return redirect(url_for('views.tutorhome'))
            elif role == "Tutee":
                c.execute("INSERT INTO Tutees VALUES (:email, :first_name, :password)",
                          {
                              'email': email,
                              'first_name': first_name,
                              'password': password1
                          })
                conn.commit()
                conn.close()
                flash('Account successfully created!', category='success')
                return redirect(url_for('views.tuteehome'))  # redirects to respective homepages according to account type
            # use url_for with blueprint name and function name for mapping

    return render_template("sign_up.html", user=current_user)

# creates a route to the webpage with url '/tutor' and redirects to the url used for the tutor homepage
@auth.route('/tutor', methods=['GET', 'POST'])
def unavailable():
    tutoremail = current_user.get_id()  # calls the get_id() function within the OOP class

    if request.method == 'POST':
        date = request.form.get('date')  # taking in inputs from html form
        starttime = request.form.get('starttime')
        endtime = request.form.get('endtime')

        # creating unavailable id by combining string values of the date, start time and end time
        unavailable_id = date.replace("-", "") + starttime.replace(":", "") + endtime.replace(":", "")
        unavailable_id = uniquebooking(unavailable_id)  # recursive algorithm to ensure that the id is unique

        conn = s.connect("tutoring.db")  # adding the unavailable time into the corresponding database table
        c = conn.cursor()
        c.execute('INSERT INTO "Unavailable Times" VALUES (:unavailable_id, :tutor_email, :date, :start_time, :end_time)',
                  {
                      'unavailable_id': unavailable_id,
                      'tutor_email': tutoremail,
                      'date': date,
                      'start_time': starttime,
                      'end_time': endtime,
                  })
        conn.commit()
        conn.close()
        flash('Unavailable time is saved!', category='success')

    return redirect(url_for('views.tutorhome'))

# creates a route to the webpage with url '/tutoraccount' and redirects to the template "tutordetails.html"
@auth.route('/tutoraccount', methods=['GET', 'POST'])  # GET = request data, POST = submit data, they are HTTP methods
def tutoraccount():
    tutor = None
    tutoremail = current_user.get_id()  # calls get_id() method inside an OOP class

    if request.method == 'GET':
        conn = s.connect("tutoring.db")
        c = conn.cursor()
        c.execute('SELECT * FROM Tutors WHERE email= ?', (tutoremail, ))  # finds the tutor that has a matching email
        tutor = list(c.fetchone())

        ids = tutor[3].replace(" ","").split(",")  # stores the subject ids of the tutor in a list
        subjects = [id_to_name(int(value)) for value in ids]  # converts the ids into subject names
        tutor[3] = ", ".join(subjects)

        conn.close()

    if request.method == 'POST':  # this updates the account information for tutors
        password = request.form.get('password')  # taking in inputs from html form
        rate = request.form.get('rate')
        subject = request.form.getlist('subjects')
        subject = ", ".join(subject) if subject else None
        conn = s.connect("tutoring.db")
        c = conn.cursor()

        if len(password) < 7 and password != "":
            flash('Password must be greater than 7 characters', category='error')
        else:
            c.execute("""UPDATE Tutors SET password = COALESCE(?, password), 
                                                charge = COALESCE(?, charge), 
                                                subjects = COALESCE(?, subjects) 
                                                WHERE email = ?""",
                      (password if password else None, rate if rate else None, subject if subject else None, tutoremail)
                      )
            # COALESCE handles null values and returns the first non-null value
            # which allows the user to leave some parameters blank when filling in the html form
            conn.commit()
            flash("Account details successfully updated!", category="success")

        c.execute('SELECT * FROM Tutors WHERE email= ?', (tutoremail, ))  # selecting tutor form database
        tutor = list(c.fetchone())
        ids = tutor[3].replace(" ","").split(",")
        subjects = [id_to_name(int(value)) for value in ids if value.isdigit()]
        tutor[3] = ", ".join(subjects)

        conn.close()
        return render_template("tutordetails.html", user=current_user, tutor=tutor)
    return render_template("tutordetails.html", user=current_user, tutor=tutor)

# creates a route to the webpage with url '/tuteeaccount' and redirects to the template "tuteedetails.html"
@auth.route('/tuteeaccount', methods=['GET', 'POST'])
def tuteeaccount():
    tutee = None
    tuteeemail = current_user.get_id()

    if request.method == 'GET':
        conn = s.connect("tutoring.db")
        c = conn.cursor()
        c.execute('SELECT * FROM Tutees WHERE email= ?', (tuteeemail, ))
        # selecting a tutee from database according to email
        tutee = c.fetchone()

        conn.close()

    if request.method == 'POST':
        password = request.form.get('password')  # taking in password input form html form
        conn = s.connect("tutoring.db")
        c = conn.cursor()

        if len(password) < 7:
            flash('Password must be greater than 7 characters', category='error')
        else:  # updates password to the non-null value between the new input and the original password
            c.execute('UPDATE Tutees SET password = COALESCE(?, password) WHERE email = ?', (password if password else None, tuteeemail))
            conn.commit()
            flash("Account details successfully updated!", category="success")

        c.execute('SELECT * FROM Tutees WHERE email= ?', (tuteeemail, ))
        tutee = c.fetchone()

        conn.close()
        return render_template("tuteedetails.html", user=current_user, tutee=tutee)
    return render_template('tuteedetails.html', user=current_user, tutee=tutee)

# creates a route to the webpage with url '/administratoraccount' and redirects to the template "administratordetails.html"
@auth.route('/administratoraccount', methods=['GET', 'POST'])
def administratoraccount():
    administrator = None
    administratoremail = current_user.get_id()

    if request.method == 'GET':
        conn = s.connect("tutoring.db")
        c = conn.cursor()
        c.execute('SELECT * FROM Administrators WHERE email= ?', (administratoremail,))
        # returns all values according to email parameter
        administrator = c.fetchone()

        conn.close()

    if request.method == 'POST':
        password = request.form.get('password')  # takes in password input from html form

        conn = s.connect("tutoring.db")
        c = conn.cursor()

        if len(password) < 7:
            flash('Password must be greater than 7 characters', category='error')
        else:
            c.execute('UPDATE Administrators SET password = COALESCE(?, password) WHERE email = ?',
                      (password if password else None, administratoremail))
            conn.commit()  # SQL command for updating the Administrator password
            flash("Account details successfully updated!", category="success")

        c.execute('SELECT * FROM Administrators WHERE email= ?', (administratoremail,))
        administrator = c.fetchone()  # returns all values according to email parameter

        conn.close()

        return render_template("administratordetails.html", user=current_user, admin=administrator)
    return render_template('administratordetails.html', user=current_user, admin=administrator)