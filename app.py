import sqlite3
import os
from flask import Flask, render_template, request, redirect, url_for, session, flash
from werkzeug.utils import secure_filename

app = Flask(__name__)
app.secret_key = "dev_secret_key"

UPLOAD_FOLDER = 'static/uploads'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER


# ----------------------
# DATABASE CONNECTION
# ----------------------
def get_db():
    conn = sqlite3.connect("flask_auth.db")
    conn.row_factory = sqlite3.Row
    return conn


# ----------------------
# CREATE DATABASE TABLES
# ----------------------
def create_tables():
    conn = get_db()
    cursor = conn.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT NOT NULL,
            email TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS tasks (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            task TEXT NOT NULL
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS posts (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            content TEXT NOT NULL
        )
    """)

    conn.commit()
    conn.close()


create_tables()


# ----------------------
# LOADING PAGE
# ----------------------
@app.route('/')
def home():
    return redirect(url_for('login'))


# ----------------------
# LOGIN ROUTING
# ----------------------
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']

        conn = get_db()
        cursor = conn.cursor()

        cursor.execute(
            "SELECT * FROM users WHERE email = ? AND password = ?",
            (email, password)
        )
        user = cursor.fetchone()
        conn.close()

        if user:
            session['username'] = user['username']
            return redirect(url_for('dashboard'))
        else:
            flash("Invalid email or password")

    return render_template("login.html")


# ----------------------
# DASHBOARD ROUTING
# ----------------------
@app.route('/dashboard')
def dashboard():
    if 'username' in session:
        return render_template('dashboard.html', username=session['username'])
    return redirect(url_for('login'))


# ----------------------
# SIGNUP ROUTING
# ----------------------
@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        username = request.form['username']
        email = request.form['email']
        password = request.form['password']

        conn = get_db()
        cursor = conn.cursor()

        try:
            cursor.execute(
                "INSERT INTO users (username, email, password) VALUES (?, ?, ?)",
                (username, email, password)
            )
            conn.commit()
            flash("Account created successfully! Please log in.")
            return redirect(url_for('login'))
        except:
            flash("Email already exists.")
        finally:
            conn.close()

    return render_template("signup.html")


# ----------------------
# LOGOUT ROUTING
# ----------------------
@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))


# ----------------------
# TO-DO ROUTING
# ----------------------
@app.route('/tasks')
def tasks():
    conn = get_db()
    cur = conn.cursor()
    cur.execute("SELECT * FROM tasks")
    tasks = cur.fetchall()
    conn.close()

    return render_template('tasks.html', tasks=tasks)


# ----------------------
# TO-DO ADD TASK ROUTING
# ----------------------
@app.route('/add_task', methods=['POST'])
def add_task():
    task = request.form['task']

    conn = get_db()
    cur = conn.cursor()
    cur.execute("INSERT INTO tasks (task) VALUES (?)", (task,))
    conn.commit()
    conn.close()

    return redirect(url_for('tasks'))


# ----------------------
# TO-DO DELETE TASK ROUTING
# ----------------------
@app.route('/delete_task/<int:id>')
def delete_task(id):
    conn = get_db()
    cur = conn.cursor()
    cur.execute("DELETE FROM tasks WHERE id = ?", (id,))
    conn.commit()
    conn.close()

    return redirect(url_for('tasks'))


# ----------------------
# BLOG PAGE ROUTING
# ----------------------
@app.route('/blog')
def blog():
    conn = get_db()
    cur = conn.cursor()
    cur.execute("SELECT * FROM posts")
    posts = cur.fetchall()
    conn.close()

    return render_template('blog.html', posts=posts)


# ----------------------
# CREATE BLOG POST ROUTING
# ----------------------
@app.route('/create_post', methods=['GET', 'POST'])
def create_post():
    if request.method == 'POST':
        title = request.form['title']
        content = request.form['content']

        conn = get_db()
        cur = conn.cursor()
        cur.execute(
            "INSERT INTO posts (title, content) VALUES (?, ?)",
            (title, content)
        )
        conn.commit()
        conn.close()

        return redirect(url_for('blog'))

    return render_template('create_post.html')


# ----------------------
# IMAGE UPLOAD ROUTING
# ----------------------
@app.route('/upload', methods=['GET', 'POST'])
def upload():
    if request.method == 'POST':
        file = request.files['image']

        if file:
            filename = secure_filename(file.filename)
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))

            return redirect(url_for('upload'))

    return render_template('upload.html')


# ----------------------
# RUN APP
# ----------------------
if __name__ == "__main__":
    app.run(debug=True)