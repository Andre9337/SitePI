from flask import Flask, render_template, request, redirect, url_for
import sqlite3

app = Flask(__name__)

@app.route('/')
def index():
    conn = sqlite3.connect('database.db')
    cur = conn.cursor()
    #cur.execute('SELECT * FROM users')
    users = conn.execute('SELECT * FROM users').fetchall()
    rows = cur.fetchall()
    with open('usuarios.txt', 'w') as f:
        # Escreve o cabeçalho da tabela
        f.write('ID,Nome,E-mail\n')
        # Escreve cada linha da tabela
        for user in rows:
            f.write(f'{user[0]},{user[1]},{user[2]}\n')
    conn.close()
    return render_template('index.html', rows=rows, users=users)

@app.route('/add', methods=['POST'])
def add():
    if request.method == 'POST':
        name = request.form['name']
        email = request.form['email']
        p = request.form['pass']
        conn = sqlite3.connect('database.db')
        cur = conn.cursor()
        cur.execute('INSERT INTO users (name, email, pass) VALUES (?, ?, ?)', (name, email, p))
        conn.commit()
        conn.close()
        return redirect(url_for('index'))

@app.route('/edit/<int:id>', methods=['POST', 'GET'])
def edit(id):
    conn = sqlite3.connect('database.db')
    cur = conn.cursor()
    cur.execute('SELECT * FROM users WHERE id = ?', (id,))
    row = cur.fetchone()
    conn.close()
    if request.method == 'POST':
        name = request.form['name']
        email = request.form['email']
        p = request.form['pass']
        conn = sqlite3.connect('database.db')
        cur = conn.cursor()
        cur.execute('UPDATE users SET name = ?, email = ?, pass = ? WHERE id = ?', (name, email, p, id))
        conn.commit()
        conn.close()
        return redirect(url_for('index'))
    return render_template('edit.html', row=row)

@app.route('/delete/<int:id>', methods=['POST'])
def delete(id):
    conn = sqlite3.connect('database.db')
    cur = conn.cursor()
    cur.execute('DELETE FROM users WHERE id = ?', (id,))
    conn.commit()
    conn.close()
    return redirect(url_for('index'))

if __name__ == '__main__':
    conn = sqlite3.connect('database.db')
    cur = conn.cursor()
    cur.execute('''CREATE TABLE IF NOT EXISTS users 
                   (id INTEGER PRIMARY KEY AUTOINCREMENT, name TEXT, email TEXT, pass TEXT)''')
    conn.close()
    app.run(debug=True)
