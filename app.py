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

@app.route('/', methods=['GET', 'POST'])
def login():
    if request.method=='POST':
        username=request.form['username']
        password=request.form['password']
        if 'entrar' in request.form:
            if len(username) and len(password)!=0:
                with open('usuario.txt','w') as f:
                    f.write(username+" "+password)
                conn=sqlite3.connect('database.db')
                cur = conn.cursor()
                cur.execute("SELECT * FROM users WHERE (name = ? OR email = ?) AND pass = ?;", (username, username, password))
                match = cur.fetchall()
                conn.close()
                if len(match) == 1:
                    return redirect('/home')
                return render_template('login.html', error='Invalid username or password')
            else:
                return render_template('login.html')
        elif 'register' in request.form:
            email=request.form['email']
            with open('inserts.txt','w') as f:
                f.write(username+" "+password+" "+email)
            if len(username) and len(password) and len(email)!=0:
                conn=sqlite3.connect('database.db')
                cur=conn.cursor()
                cur.execute('INSERT INTO users (name, email, pass) VALUES (?,?,?)',(username,email,password))
                conn.commit()
                with open('insert.txt','w') as f:
                    rows=cur.fetchall()
                    for lines in rows:
                        f.write(lines[0])
                conn.close
                return render_template('login.html',error='Registrado com sucesso')
            else:
                return render_template('Register.html',error='Algum dos campos está vazio ou invalido!!!')
    else:
        return render_template('login.html')
    
@app.route('/register', methods=['GET', 'POST'])
def register():
    return render_template('Register.html')

@app.route('/home')
def home():
    conn=sqlite3.connect('database.db')
    data=conn.execute('select * from data').fetchall()
    conn.close()
    return render_template('home.html',data=data)

@app.route('/add', methods=['POST'])
def add():
    if request.method =='POST':
        dia=request.form['dia']
        valor=request.form['valor']
        desc=request.form['desc']
        conn=sqlite3.connect('database.db')
        cur=conn.cursor()
        cur.execute('INSERT INTO data (dia, val, desc) VALUES (?,?,?)',(dia,valor,desc))
        conn.commit()
        conn.close()
        return redirect('/home')
    else:
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
                   (id INTEGER PRIMARY KEY AUTOINCREMENT, dia TEXT, val TEXT, desc TEXT)''')
    conn.close()
    app.run(debug=True)
