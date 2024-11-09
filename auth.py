# from flask import Blueprint,render_template,request,flash,redirect,url_for
# from .models import Users 
# from werkzeug.security import generate_password_hash, check_password_hash
# from . import db
# from flask_login import login_user, login_required, logout_user, current_user
# import sqlite3

# auth = Blueprint('auth' , __name__)

# @auth.route('/signin', methods=['GET', 'POST'])
# def signin():
#     if request.method == 'POST':
#         email = request.form.get('email')
#         password = request.form.get('password')

#         # Fetch user from the Users table
        

#         user = Users.query.filter_by(email=email).first()
#         print(f"User found: {user.email}, User Type: {user.user_type}")
#         if user:
#             # Check if the entered password matches the stored hash
#             if check_password_hash(user.password, password):
#                 flash('Logged in successfully!', category='success')
#                 login_user(user, remember=True)

#                 # Directly retrieve user_type from the user object
#                 user_type = user.user_type  # Assuming user_type is an attribute in Users model
#                 print(f"User found: {user.email}, User Type: {user_type}")

#                 # Redirect based on user type
#                 if user_type == 'client':
#                     return redirect(url_for('views.receptive'))  # Adjust with your actual view name
#                 elif user_type == 'dietitian':
#                     return redirect(url_for('views.consultatio'))  # Adjust with your actual view name
                
#             else:
#                 flash('Incorrect password, try again.', category='error')
#         else:
#             flash('Email does not exist.', category='error')
#     return render_template('signin.html')

from flask import Blueprint, render_template, request, flash, redirect, url_for, session
from werkzeug.security import generate_password_hash, check_password_hash
import sqlite3

auth = Blueprint('auth', __name__)

# Utility function to get user type
def get_user_type(email):
    with sqlite3.connect('nutri.db') as con:
        cur = con.cursor()
        cur.execute("SELECT user_type FROM users WHERE email=?", (email,))
        return cur.fetchone()
    
@auth.route('/signin', methods=['GET', 'POST'])
def signin():
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')

        # Fetch user from the database
        with sqlite3.connect('nutri.db') as con:
            cur = con.cursor()
            cur.execute("SELECT * FROM users WHERE email=?", (email,))
            user = cur.fetchone()

        if user:
            user_id = user[0]  # Assuming user_id is the first column in the users table
            session['user_id'] = user_id  # Store user_id in session

            # Redirect based on user type (client or dietitian)
            user_type_row = get_user_type(email)
            if user_type_row:
                user_type = user_type_row[0]
                if user_type == 'client':
                    return redirect(url_for('views.receptive'))
                else :
                    return redirect(url_for('views.consultatio'))
            else:
                flash('User type not found.', category='error')
        else:
            flash('Email does not exist.', category='error')

    return render_template('signin.html')


# @auth.route('/signin', methods=['GET', 'POST'])
# def signin():
#     if request.method == 'POST':
#         email = request.form.get('email')
#         password = request.form.get('password')
#         print(email)

#         # Fetch user from the database
#         with sqlite3.connect('nutri.db') as con:
#             cur = con.cursor()
#             cur.execute("SELECT * FROM users WHERE email=?", (email,))
#             user = cur.fetchall()

#         print(user)

#         if user:
#             print(user)
#             #stored_password = user[3]  # Assuming password is the 4th column
#             # if check_password_hash(stored_password, password):
#             #     flash('Logged in successfully!', category='success')

#                 # Get user type
#             user_type_row = get_user_type(email)
#             print(user_type_row[0])
#             if user_type_row:
#                 user_type = user_type_row[0]
                
#                 if user_type == 'client':
#                     print(user_type)
#                     return redirect(url_for('views.receptive'))                    
#                 elif user_type == 'dietitian':
#                         return redirect(url_for('views.consultatio'))
#                 else:
#                     flash('User type not found.', category='error')
#             # else:
#             #     flash('Incorrect password, try again.', category='error')
#         else:
#             flash('Email does not exist.', category='error')

#     return render_template('signin.html')


@auth.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        email = request.form.get('email')
        name = request.form.get('name')
        password = request.form.get('password')

        # Check if the email already exists
        with sqlite3.connect('nutri.db') as con:
            cur = con.cursor()
            cur.execute("SELECT * FROM users WHERE email=?", (email,))
            existing_user = cur.fetchone()

        if existing_user:
            flash('Email already exists.', category='error')
        elif len(email) < 4:
            flash('Email must be greater than 3 characters', category='error')
        elif len(name) < 2:
            flash('Name must be greater than 1 character', category='error')
        elif len(password) < 7:
            flash('Password must be at least 7 characters', category='error')
        else:
            hashed_password = generate_password_hash(password, method='pbkdf2:sha512')
            with sqlite3.connect('nutri.db') as con:
                cur = con.cursor()
                cur.execute("INSERT INTO users (email, name, password, user_type) VALUES (?, ?, ?, ?)", 
                            (email, name, hashed_password, 'client'))  # Default user_type or adjust as needed
                con.commit()
            flash('Account created', category='success')
            return redirect(url_for('auth.signin'))

    return render_template('signin.html')