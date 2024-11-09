from flask import Flask
from flask_mysqldb import MySQL
from flask_sqlalchemy import SQLAlchemy
from os import path
from flask_login import LoginManager

db = SQLAlchemy()

def create_app():
    app = Flask(__name__)
    app.config['MYSQL_HOST'] = 'localhostzz'
    app.config['MYSQL_USER'] = 'root'
    app.config['MYSQL_PASSWORD'] = 'Arathy.bindhu12345'
    app.config['MYSQL_DB'] = 'NUTRI'
    app.config['MYSQL_PORT'] = 3306
    app.config['SECRET_KEY'] = 'dkjfnhe'
    app.config["SQLALCHEMY_DATABASE_URI"] = 'sqlite:///NUTRI.db'

    db.init_app(app)

    from .views import views
    from .auth import auth

    app.register_blueprint(views)
    app.register_blueprint(auth)

    from .models import Users

    with app.app_context():
        db.create_all()

    login_manager = LoginManager()
    login_manager.login_view = 'auth.signup'
    login_manager.init_app(app)

    @login_manager.user_loader
    def load_user(user_id):
        return Users.query.get(str(user_id))

    return app
