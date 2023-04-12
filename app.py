from flask import Flask, render_template, request, redirect
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__, static_url_path='/static')
app.debug = True

app.config['SQLALCHEMY_DATABASE_URI']='sqlite://site.db'
db= SQLAlchemy(app)


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
