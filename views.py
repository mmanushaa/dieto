from flask import Flask, jsonify, Blueprint, render_template, redirect, url_for, request, flash, session,g
from flask_mysqldb import MySQL
from flask_login import login_required, current_user
from . import db
from Glowsite.models import Users
from datetime import datetime, date
import sqlite3

views = Blueprint('views', __name__)
app = Flask(__name__)
mysql = MySQL(app)

@views.route('/', methods=['GET', 'POST'])
def index():
    if 'username' in session:
        return render_template("index.html", username=session['username'])
    else:
        return render_template("index.html")

@views.route('/new_page', methods=['POST'])
def new_page():
    # Handle form submission and redirect to new page
    return render_template("signin.html")

@views.route('/process_signup', methods=['POST'])
def process_signup():
    if request.method == 'POST':
        try :
            name = request.form['name']
            email = request.form['email']
            usertype = request.form['usertype']
            password = request.form['password']
            with sqlite3.connect('nutri.db') as con:
                cur = con.cursor()
                cur.execute("INSERT INTO users (name, email, user_type, password) VALUES (?, ?, ?, ?)", (name, email, usertype, password))
                cur.execute("SELECT * FROM users")
                user = cur.fetchone()
                print(user)
                con.commit()
        except:
            con.rollback()

        finally:
            con.close()
            # Send the transaction message to result.html
            return redirect(url_for('views.signup_success', name=name, email=email))
    
        # cur = mysql.connection.cursor()
        # try:
        #     # Insert into Login table without specifying id if it's auto-incremented
        #     cur.execute("INSERT INTO Login (name, email, password) VALUES (%s, %s, %s)", (name, email, password))
        #     mysql.connection.commit()
        #     flash('Signup successful! Welcome, {}'.format(name), 'success')
        # except Exception as e:
        #     mysql.connection.rollback()  # Rollback in case of error
        #     flash('Signup failed: {}'.format(str(e)), 'error')
        # finally:
        #     cur.close()

@views.route('/signup_success')
def signup_success():
    name = request.args.get('name')
    email = request.args.get('email')
    
    return render_template('signin.html', name=name, email=email)

@views.route('/receptive')
def receptive():
    return render_template('recemain2.html')

@views.route('/receptive2')
def receptive2():
    return render_template('receptive.html')

@views.route('/dietsetgo')
def dietsetgo():
    return render_template('dietsetgo.html')

@views.route('/consultatio')
def consultatio():
    return render_template('dietitian.html')

def get_db_connection():
    conn = sqlite3.connect('nutri.db')  # Assuming your SQLite database is 'users.db'
    conn.row_factory = sqlite3.Row  # This allows us to use dictionary-style access to rows
    return conn

# Route for serving the frontend HTML
@app.route('/')
def index():
    return render_template('index.html')  # Make sure this file exists in the 'templates' directory

# Fetch all users from the database
@views.route('/get_all_users', methods=['GET'])
def get_all_users():
    conn = get_db_connection()
    users = conn.execute('SELECT * FROM user_goals').fetchall()
    conn.close()

    if not users:
        return jsonify({'error': 'No users found'}), 404

    users_list = []
    for user in users:
        users_list.append({
            'user_id': user['user_id'],
            'goal_description': user['goal_description']
        })
    
    return jsonify(users_list)

@views.route('/add_goal', methods=['POST'])
def add_goal():
    if 'user_id' not in session:
        flash('You need to log in to set goals.', category='error')
        return redirect(url_for('signin'))

    user_id = session['user_id']
    goal_description = request.form.get('goal_description')
    current_weight = request.form.get('current_weight')
    target_weight = request.form.get('target_weight')
    food_preference = request.form.get('food_preference')
    sleep_hours = request.form.get('sleep')

    # Insert goal data into user_goals table
    with sqlite3.connect('nutri.db') as con:
        cur = con.cursor()
        cur.execute('''INSERT INTO user_goals (user_id, goal_description, current_weight, target_weight, target_date)
                       VALUES (?, ?, ?, ?, ?)''',
                    (user_id, goal_description, current_weight, target_weight, datetime.now()))
        con.commit()

    flash('Goal added successfully!', category='success')
    return redirect(url_for('views.receptive'))

@views.route('/set_diet', methods=['POST'])
def set_diet():
    data = request.get_json()
    user_id = data['user_id']
    diet_description = data['diet_description']

    # Assume dietitian is the currently logged-in user
    dietitian_id = session.get('user_id')  # Assuming the dietitian's user_id is stored in the session

    if not dietitian_id:
        return jsonify({"message": "User not logged in"}), 401

    if not user_id or not diet_description:
        return jsonify({"message": "User ID and diet description are required"}), 400

    # Insert into the database
    conn = get_db_connection()
    conn.execute('''
        INSERT INTO diet_plans (dietitian_id, user_id, diet_description) 
        VALUES (?, ?, ?)
    ''', (dietitian_id, user_id, diet_description))
    conn.commit()
    conn.close()

    return jsonify({"message": "Diet plan successfully set!"})

@views.route('/goals')
def goals():
    # Assuming user_id is stored in session during login
    user_id = session.get('user_id')

    if not user_id:
        return "User not logged in", 401

    # Query the diet plan for the logged-in user
    db = get_db_connection()
    cur = db.execute('SELECT diet_description FROM diet_plans WHERE user_id = ?', (user_id,))
    diet_plan = cur.fetchone()

    if diet_plan:
        diet_description = diet_plan['diet_description']
    else:
        diet_description = "No diet plan available"

    return render_template('getdiet.html', diet_description=diet_description)

@views.route('/profile')
def profile():
    user_id = session.get('user_id')  # Assuming user_id is stored in session
    
    conn = sqlite3.connect('nutri.db')
    conn.row_factory = sqlite3.Row  # For easier row-to-dict conversion
    c = conn.cursor()
    
    # Fetch user details
    c.execute("SELECT * FROM users WHERE user_id = ?", (user_id,))
    user = c.fetchone()
    
    # Fetch user goals
    c.execute("SELECT * FROM user_goals WHERE user_id = ?", (user_id,))
    goals = c.fetchall()
    
    # Fetch diet plans
    c.execute("SELECT * FROM diet_plans WHERE user_id = ?", (user_id,))
    diet_plans = c.fetchall()
    
    # Fetch progress
    c.execute("SELECT * FROM user_progress WHERE user_id = ?", (user_id,))
    progress = c.fetchall()
    
    conn.close()

    return render_template('profile.html', user=user, goals=goals, diet_plans=diet_plans, progress=progress)

@views.route('/progress', methods=['GET','POST'])
def progress():
    return render_template('progress.html')

# @views.route('/update_weight', methods=['GET','POST'])
# def update_weight():
#     if 'user_id' not in session:
#         return redirect(url_for('login'))
#     user_id = session['user_id']
#     db = get_db_connection()
#     cursor = db.cursor()

#     if request.method == 'POST':
#         new_weight = request.form['current_weight']
#         cursor.execute('UPDATE user_goals SET current_weight = ? WHERE user_id = ?', (new_weight, user_id))
#         db.commit()
#         return redirect(url_for('views.update_weight'))

#     cursor.execute('SELECT current_weight, target_weight FROM user_goals WHERE user_id = ?', (user_id,))
#     result = cursor.fetchone()
#     current_weight, target_weight = result if result else (None, None)
#     progress = round((1 - current_weight / target_weight) * 100, 2) if current_weight and target_weight else 0

#     return render_template('progress.html', current_weight=current_weight, target_weight=target_weight, progress=progress)

@views.route('/get_progress_data/<int:user_id>')
def get_progress_data(user_id):
    db = get_db_connection()
    cursor = db.cursor()
    user_id = session['user_id']
    
    cursor.execute("SELECT current_weight, target_weight FROM user_goals WHERE user_id = ?", (user_id,))
    row = cursor.fetchone()
    
    if row:
        current_weight, target_weight = row
        progress = ((current_weight - target_weight) / target_weight) * 100 if target_weight else 0
        return jsonify({"current_weight": current_weight, "target_weight": target_weight, "progress": progress})
    return jsonify({"error": "No data found for this user."}), 404

@views.route('/update_weight', methods=['GET', 'POST'])
def update_weight():
    if 'user_id' not in session:
        return redirect(url_for('login'))

    user_id = session['user_id']
    db = get_db_connection()
    cursor = db.cursor()

    if request.method == 'POST':
        new_weight = request.form['updated_weight']  # Fetching the updated weight from the form
        cursor.execute('UPDATE user_goals SET current_weight = ? WHERE user_id = ?', (new_weight, user_id))
        db.commit()
        return redirect(url_for('views.update_weight'))

    # Fetch current and target weights from the database
    cursor.execute('SELECT current_weight, target_weight FROM user_goals WHERE user_id = ?', (user_id,))
    result = cursor.fetchone()
    
    current_weight, target_weight = result if result else (None, None)

    # Calculate progress if both weights are available
    progress = round((1 - (current_weight / target_weight)) * 100, 2) if current_weight and target_weight else 0

    return render_template('progress.html', current_weight=current_weight, target_weight=target_weight, progress=progress)

@views.route('/submit_feedback', methods=['POST'])
def submit_feedback():
    print("hi")
    if 'user_id' not in session:
        return jsonify({"message": "User not signed in"}), 403

    user_id = session['user_id']
    data = request.get_json()
    feedback = data.get('feedback')
    feedback_date = date.today()

    if not feedback:
        return jsonify({"message": "Feedback cannot be empty"}), 400

    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('''INSERT INTO user_progress (user_id, progress_description, progress_date)
                      VALUES (?, ?, ?)''', (user_id, feedback, feedback_date))
    conn.commit()
    conn.close()

    return jsonify({"message": "Feedback submitted successfully"}), 200
