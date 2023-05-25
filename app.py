from flask import Flask, render_template, request, redirect, url_for, session
import sqlite3

app = Flask(__name__)
app.secret_key = 'sua_chave_secreta'

@app.route('/')
def start():
    return redirect(url_for('login'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    if 'username' in session:
        return redirect(url_for('home'))

    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        if len(username) and len(password) != 0:
            conn = sqlite3.connect('database.db')
            cur = conn.cursor()
            cur.execute("SELECT * FROM users WHERE (name = ? OR email = ?) AND pass = ?;", (username, username, password))
            match = cur.fetchone()
            conn.close()

            if match:
                session['username'] = username
                return redirect(url_for('home'))

        return render_template('login.html', error='Invalid username or password')

    return render_template('login.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        email = request.form['email']

        if len(username) and len(password) and len(email) != 0:
            conn = sqlite3.connect('database.db')
            cur = conn.cursor()
            cur.execute('INSERT INTO users (name, email, pass) VALUES (?,?,?)', (username, email, password))
            conn.commit()
            conn.close()
            return render_template('login.html', error='Registered successfully')

        return render_template('register.html', error='Some fields are empty or invalid')

    return render_template('register.html')

@app.route('/home')
def home():
    if 'username' not in session:
        return redirect(url_for('login'))

    conn = sqlite3.connect('database.db')
    cur = conn.cursor()
    cur.execute('SELECT * FROM data')
    data = cur.fetchall()
    conn.close()
    return render_template('home.html', data=data)

@app.route('/add', methods=['POST'])
def add():
    if request.method == 'POST':
        dia = request.form['dia']
        valor = request.form['valor']
        desc = request.form['desc']

        if dia and valor and desc:
            conn = sqlite3.connect('database.db')
            cur = conn.cursor()
            cur.execute('INSERT INTO data (dia, val, desc) VALUES (?,?,?)', (dia, valor, desc))
            conn.commit()
            conn.close()
            return redirect(url_for('home'))

    return render_template('home.html')

@app.route('/edit/<int:id>', methods=['POST', 'GET'])
def edit(id):
    conn = sqlite3.connect('database.db')
    cur = conn.cursor()
    cur.execute('SELECT * FROM data WHERE id = ?', (id,))
    row = cur.fetchone()
    conn.close()

    if request.method == 'POST':
        dia = request.form['dia']
        val = request.form['val']
        desc = request.form['desc']

        if dia and val and desc:
            conn = sqlite3.connect('database.db')
            cur = conn.cursor()
            cur.execute('UPDATE data SET dia = ?, val = ?, desc = ? WHERE id = ?', (dia, val, desc, id))
            conn.commit()
            conn.close()
            return redirect(url_for('home'))

    return render_template('edit.html', row=row)

@app.route('/delete/<int:id>', methods=['POST'])
def delete(id):
    conn = sqlite3.connect('database.db')
    cur = conn.cursor()
    cur.execute('DELETE FROM data WHERE id = ?', (id,))
    conn.commit()
    conn.close()
    return redirect(url_for('home'))

if __name__ == '__main__':
    conn = sqlite3.connect('database.db')
    cur = conn.cursor()
    cur.execute('''CREATE TABLE IF NOT EXISTS users
    (id INTEGER PRIMARY KEY AUTOINCREMENT, name TEXT, email TEXT, pass TEXT)''')
    cur.execute('''CREATE TABLE IF NOT EXISTS data
    (id INTEGER PRIMARY KEY AUTOINCREMENT, id_user INT,dia TEXT, val TEXT, desc TEXT)''')
    conn.close()
    app.run(debug=True)
