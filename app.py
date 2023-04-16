"""
from flask import Flask, render_template, request, redirect

app = Flask(__name__, static_url_path='/static')
app.debug = True


users = [
    {"username": "user1", "password": "pass1"},
    {"username": "user2", "password": "pass2"},
    {"username": "user3", "password": "pass3"}
]

@app.route('/', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        print(username)
        password = request.form['password']
        for user in users:
            if user['username'] == username and user['password'] == password:
                return redirect('/home')
        return render_template('login.html', error='Invalid username or password')
    else:
        return render_template('login.html')

@app.route('/home')
def home():
    return render_template('home.html')

if __name__ == '__main__':
    app.run(debug=True)
"""
from flask import Flask, render_template, request, redirect, url_for
import sqlite3

app = Flask(__name__, static_url_path='/static')
app.debug=True

@app.route('/')
def login():
    if request.method=='POST':
        username=request.form['username']
        password=request.form['password']
        conn=sqlite3.connect('database.db')
        match=conn.execute("SELECT * FROM users WHERE (name = '?' OR email = '?') AND pass = '?';",(username,username,password)).fetchall()
        conn.commit()
        conn.close()
        if len(match) == 1:
            return redirect('/home')
        return render_template('login.html', error='Invalid username or password')
    else:
        return render_template('login.html')

@app.route('/home')
def home():
    return render_template('home.html')

if __name__ == '__main__':
    conn = sqlite3.connect('database.db')
    cur = conn.cursor()
    cur.execute('''CREATE TABLE IF NOT EXISTS users 
                   (id INTEGER PRIMARY KEY AUTOINCREMENT, name TEXT, email TEXT, pass TEXT)''')
    conn.close()
    app.run(debug=True)
