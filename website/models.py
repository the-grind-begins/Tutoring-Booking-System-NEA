from flask_login import UserMixin  # used to manage user sessions


class User(UserMixin):  # UserMixin implemented in order to work with Flask login
    def __init__(self, email, firstname, password):
        self.email = email
        self.firstname = firstname
        self.password = password

    def is_active(self):  # returns true if the user's account is active
        return True

    def get_id(self):  # returns the user's email for Flask to manage user session
        return self.email


class Tutor(UserMixin):
    def __init__(self, email, firstname, password, subjects, charge, rating):
        self.email = email
        self.firstname = firstname
        self.password = password
        self.subjects = subjects
        self.charge = charge
        self.rating = rating

    def is_active(self):
        return True

    def get_id(self):
        return self.email


class Tutee(UserMixin):
    def __init__(self, email, firstname, password):
        self.email = email
        self.firstname = firstname
        self.password = password

    def is_active(self):
        return True

    def get_id(self):
        return self.email

class Administrator(UserMixin):
    def __init__(self, email, firstname, password):
        self.email = email
        self.firstname = firstname
        self.password = password

    def is_active(self):
        return True

    def get_id(self):
        return self.email

