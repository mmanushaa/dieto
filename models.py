from . import db

class Users(db.Model):
    __tablename__ = 'users'  # Specify the name of the table in the database

    id = db.Column(db.Integer, primary_key=True)  # Primary key
    name = db.Column(db.String(30), nullable=False)  # User's name
    email = db.Column(db.String(30), nullable=False, unique=True)  # User's email
    user_type = db.Column(db.String(20), nullable=False)  # User type (e.g., 'client', 'dietitian')

    def __repr__(self):
        return f"<Users {self.name}, {self.email}, {self.user_type}>"

