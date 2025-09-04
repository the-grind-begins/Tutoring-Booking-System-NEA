from flask import Flask
from flask_login import LoginManager
from .auth import find_load


def create_app():
    app = Flask(__name__)
    # set up to sign session cookies for protection against cookie data tampering
    # essentially used to protect user data against cyber attackers
    app.config['SECRET_KEY'] = 'ihfeoihdaoihaoihfa hufeffdshufds'

    # blueprints imported from view.py and auth.py files
    from .views import views
    from .auth import auth

    # registering blueprints along with the url prefix
    app.register_blueprint(views, url_prefix='/')
    app.register_blueprint(auth, url_prefix='/')

    # import classes
    from .models import Tutor, Tutee, Administrator

    # the LoginManager is a class from Flask used to handle logins and
    # contains the code that allows for my application and Flask-login to work togethe
    login_manager = LoginManager()
    login_manager.login_view = 'auth.login'
    login_manager.init_app(app)

    # the user loader stores the user's ID when in an active session
    # so the user does not have to login every time they reopen the application
    @login_manager.user_loader

    def load_user(email):
        print(f"Loading user with email: {email}")
        return find_load(email)
        # telling flask how we load a user
        # similar to filter by but by default looks for the primary key and check if equal to passed value
        # recognizes current user
    return app
