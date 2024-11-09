import sqlite3

# Connect to SQLite database located in 'instance' folder
conn = sqlite3.connect('nutri.db')
print("connected to database")

# Create a cursor object
c = conn.cursor()

# Enable foreign key constraints (required for SQLite)
c.execute('PRAGMA foreign_keys = ON;')

# Create tables
c.execute('''CREATE TABLE users (
    user_id INTEGER PRIMARY KEY AUTOINCREMENT,
    name VARCHAR(50) NOT NULL UNIQUE,
    email VARCHAR(100) NOT NULL UNIQUE,
    password VARCHAR(255) NOT NULL,
    user_type TEXT NOT NULL,  -- Use TEXT instead of ENUM
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
)''')

c.execute('''CREATE TABLE user_goals (
    goal_id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    goal_description TEXT NOT NULL,
    current_weight DECIMAL(5, 2),  -- Current weight in kg
    target_weight DECIMAL(5, 2),   -- Target weight in kg
    target_date DATE NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(user_id)
)''')

c.execute('''CREATE TABLE dietitian_assignments (
    assignment_id INTEGER PRIMARY KEY AUTOINCREMENT,
    dietitian_id INTEGER NOT NULL,
    user_id INTEGER NOT NULL,
    assigned_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (dietitian_id) REFERENCES users(user_id),
    FOREIGN KEY (user_id) REFERENCES users(user_id) 
)''')

c.execute('''CREATE TABLE diet_plans (
    plan_id INTEGER PRIMARY KEY AUTOINCREMENT,
    dietitian_id INTEGER NOT NULL,
    user_id INTEGER NOT NULL,
    diet_description TEXT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (dietitian_id) REFERENCES users(user_id),
    FOREIGN KEY (user_id) REFERENCES users(user_id) 
)''')

c.execute('''CREATE TABLE user_progress (
    progress_id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    progress_description TEXT NOT NULL,
    progress_date DATE NOT NULL,
    FOREIGN KEY (user_id) REFERENCES users(user_id) 
)''')

c.execute('''CREATE TABLE user_weight (
    weight_id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    current_weight DECIMAL(5, 2) NOT NULL,
    target_weight DECIMAL(5, 2) NOT NULL,
    recorded_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(user_id) 
)''')

print("created tables")

# Commit and close the connection
conn.commit()
conn.close()
