from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required, current_user
import sqlite3 as s
import random

views = Blueprint('views', __name__, template_folder="templates")
# __name__ is how to define the blueprint

# all the methods and routes regarding fetching and getting information
# frequently used functions

# converts a subject id to the corresponding subject name
def id_to_name(id):
    conn = s.connect("tutoring.db")
    c = conn.cursor()

    c.execute('SELECT subject FROM Subjects WHERE subject_id = ?', (int(id),))
    data = c.fetchone()
    c.close()
    if data:
        return data[0]  # returns the name of the subject
    else:
        return None

# recursive algorithm that ensures that an id generated is unique
def uniquebooking(booking_id):
    new_booking_id = booking_id + str(random.randint(1, 256))  # APPENDS A RANDOM NUMBER RANGING FROM 1 TO 256
    new_booking_id = int(new_booking_id)

    conn = s.connect("tutoring.db")
    c = conn.cursor()
    c.execute('SELECT booking_id FROM Bookings WHERE booking_id = ?', (new_booking_id,))
    data = c.fetchone()
    c.close()

    if data is None:
        return new_booking_id  # the new booking id is returned if it is confirmed to be unique
    else:
        return uniquebooking(booking_id)  # the function is called again if the id is not unique


# creates a route to the webpage with url '/' and redirects to the url used for login
@views.route('/')
def login():
    return redirect(url_for('auth.login'))  # in template reference user and check if authenticated

# creates a route to the webpage with url '/administrator' and redirects to the template "administratorhome.html"
@views.route('/administrator')
# a login is required to access the web[ages below, hence the decorator @login_required is used
@login_required
def administratorhome():
    def get_timings():
        conn = s.connect("tutoring.db")
        c = conn.cursor()

        c.execute('SELECT subject_id, tutor_email, tutee_email, date, start_time, end_time FROM Bookings')
        data = c.fetchall()  # returning all the bookings made from the database
        for row in range(0, len(data)):
            data[row] = list(data[row])
            data[row][0] = id_to_name(data[row][0])  # converting every subject id to their name
        c.close()
        return data

    records = get_timings()
    return render_template("administratorhome.html", user=current_user, records=records)

# creates a route to the webpage with url '/tutor' and redirects to the template "tutorhome.html"
@views.route('/tutor')
@login_required
def tutorhome():
    tutoremail = current_user.get_id()

    def get_timings(tutor):
        conn = s.connect("tutoring.db")
        c = conn.cursor()

        c.execute('SELECT date, start_time, end_time FROM "Unavailable Times" WHERE tutor_email = ?', (tutor,))
        data = c.fetchall() # returns all unavailable times corresponding to a specific tutor
        c.close()
        return data

    records = get_timings(tutoremail)

    return render_template("tutorhome.html", user=current_user, records=records)

# creates a route to the webpage with url '/tutee' and redirects to the template "tuteehome.html"
@views.route('/tutee', methods=['GET', 'POST'])  # GET = request data, POST = submit data, they are HTTP methods
@login_required
def tuteehome():
    tuteeemail = current_user.get_id()

    def email_to_name(tutoremail):  # queries for a tutor's frirst name using their email
        conn = s.connect("tutoring.db")
        c = conn.cursor()

        c.execute('SELECT firstname FROM Tutors WHERE email = ?', (tutoremail,))
        data = c.fetchone()
        c.close()
        return data[0]  # returning the tutor's name

    def get_bookings(tutee):  # getting all the booking records made by the tutee
        conn = s.connect("tutoring.db")
        c = conn.cursor()

        c.execute('SELECT subject_id, tutor_email, date, start_time, end_time FROM Bookings WHERE tutee_email = ?', (tutee,))
        data = c.fetchall()  # selecting all bookings that correspond to a specific tutee
        for row in range(0, len(data)):
            data[row] = list(data[row])
            data[row][0] = id_to_name(data[row][0])  # converting subject id to name
            data[row][1] = email_to_name(data[row][1])  # returning the tutors' names
        c.close()
        return data

    def get_tutors():
        conn = s.connect("tutoring.db")
        c = conn.cursor()
        data = []
        submit = request.form.get('Submit')

        if request.method == 'POST' and submit == "Filter":  # the following actions will proceed if the filter buttin is clicked
            subject, pricestart, priceend, ratingstart, ratingend = request.form.get('subject'), request.form.get('pricestart'), request.form.get('priceend'), request.form.get('ratingstart'), request.form.get('ratingend')

            # searching for tutors that teach specific subjects and that their charge and rating fall between specified ranges
            c.execute('''SELECT email, firstname, subjects, charge, rating FROM Tutors
                         WHERE subjects LIKE ?   
                         AND charge BETWEEN ? AND ?
                         AND rating BETWEEN ? AND ?''', (f'%{subject}%',pricestart, priceend, ratingstart, ratingend))
            data = c.fetchall()  # returns all results

            for row in range(0, len(data)):
                data[row] = list(data[row])
                ids = data[row][2].replace(" ", "").split(",")
                subjects = [id_to_name(int(value)) for value in ids]  # converting every subject id to their name
                data[row][2] = ", ".join(subjects)

            conn.close()
            flash('Tutors are filtered!', category='success')
            return data

        if request.method == 'POST' and submit == "Submit":  # the following actions will proceed if the button for bookings was clicked
            subject = request.form.get('subject')  # getting values from html form
            date = request.form.get('date')
            starttime = request.form.get('starttime')
            endtime = request.form.get('endtime')
            tutoremail = request.form.get('tutor')

            tuteeemail = current_user.get_id()
            booking_id = date.replace("-", "") + starttime.replace(":", "") + endtime.replace(":", "")  # generating id
            booking_id = uniquebooking(booking_id)  # recursive algorithm for unique id

            conn = s.connect("tutoring.db")
            c = conn.cursor()  # creating a booking record within the database
            c.execute(
                "INSERT INTO Bookings VALUES (:booking_id, :subject_id, :tutor_email, :tutee_email, :date, :start_time, :end_time)",
                {
                    'booking_id': booking_id,
                    'subject_id': int(subject),
                    'tutor_email': tutoremail,
                    'tutee_email': tuteeemail,
                    'date': date,
                    'start_time': starttime,
                    'end_time': endtime,
                })
            conn.commit()
            c.close()
            flash('Booking is successful!', category='success')
            return data

    subject = request.form.get('subject')  # getting subject input from html form
    records = get_bookings(tuteeemail)
    tutors = get_tutors()
    return render_template("tuteehome.html", user=current_user, records=records, tutors=tutors, subject=subject)

# creates a route to the webpage with url '/bookings' and redirects to the template "bookings.html"
@views.route('/bookings', methods=['GET'])
@login_required
def bookings():
    tutoremail = current_user.get_id()

    def get_timings():
        conn = s.connect("tutoring.db")
        c = conn.cursor()

        # selecting records from booking corresponding to a specific tutor
        c.execute('SELECT subject_id, tutee_email, date, start_time, end_time FROM Bookings WHERE tutor_email = ?', (tutoremail,))
        data = c.fetchall()
        for row in range(0, len(data)):
            data[row] = list(data[row])
            data[row][0] = id_to_name(data[row][0])  # convertingn subject id to name
        conn.close()
        return data
    records = get_timings()
    return render_template("bookings.html", user=current_user, records=records)

# creates a route to the webpage with url '/records' and redirects to the template "tuteerecords/html"
@views.route('/records', methods=['GET'])
@login_required
def records():
    tuteeemail = current_user.get_id()

    def get_timings():  # getting bookings in the database corresponding to a specific tutee
        conn = s.connect("tutoring.db")
        c = conn.cursor()

        c.execute('SELECT subject_id, tutor_email, date, start_time, end_time FROM Bookings WHERE tutee_email = ?', (tuteeemail,))
        data = c.fetchall()
        for row in range(0, len(data)):
            data[row] = list(data[row])
            data[row][0] = id_to_name(data[row][0])  # converting subject ids to names
        c.close()
        return data
    records = get_timings()
    return render_template("tuteerecords.html", user=current_user, records=records)
