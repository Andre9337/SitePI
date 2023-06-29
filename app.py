from flask import Flask, render_template, request, redirect, url_for, session
import datetime
import requests
import csv
import sqlite3

app = Flask(__name__)
app.secret_key = 'sua_chave_secreta_aqui'
app.config['data']=[]


@app.route('/',methods=['GET', 'POST'])
def start():
    if request.method =='POST':
        with open('log.txt', 'a') as file:
            file.write("Step: POST request\n")
            file.write("Route / \n")
            file.write("\n")
        return redirect(url_for('login'))

    return redirect(url_for('login'))

@app.route('/login',methods=['GET','POST'])
def login():
    if 'username' in session:
        pass
    if request.method =='POST':
        email = request.form['email']
        password = request.form['password']
        conn=sqlite3.connect('data.db')
        cur=conn.cursor()
        cur.execute('Select * from users where user=? and pass=?;',(email,password))
        match= cur.fetchone()
        conn.close()
        with open('log.txt', 'a') as file:
            file.write("Step: Match\n")
            file.write("Route /login \n")
            file.write("User = "+str(email)+"\n")
            file.write("Pass = "+str(password)+"\n")
            file.write("Match = "+str(match)+" \n")
            file.write("\n")
        if match:
            session['username']=match[0]
            conn = sqlite3.connect('data.db')
            cur = conn.cursor()
            user = session.get('username')
            cur.execute('SELECT * FROM data WHERE id_user = ?', (user,))
            app.config['data'] = cur.fetchall()
            conn.close()
            return redirect(url_for('home'))
    
    return render_template('login.html')
    
@app.route('/home',methods=['GET','POST'])
def home():
    data=app.config['data']
    if 'username' not in session:
        return redirect(url_for('login'))
    if request.method=="GET":
        mes_atual = datetime.date.today().month
        meses = []
        for i in range(1, 6):
            mes_anterior = mes_atual - i
            if mes_anterior <= 0:
                mes_anterior += 12
            meses.append(mes_anterior)
        max=0
        soma=0
        ent=0
        fis=0
        onl=0
        for i in app.config['data']:
            soma+=i[5]
            if i[3] == "Entreterimento":
                ent+=i[5]
            if i[3] == "Fisico":
                fis+=i[5]
            if i[3] == "Online":
                onl+=i[5]
            if int(i[5]) >max:
                max=i[5]
        s=ent+fis+onl
        if ent!=0:ent1=(ent/s)*100
        else:ent1=0
        if fis!=0:fis1=(fis/s)*100
        else:fis1=0
        if onl!=0:onl1=(onl/s)*100
        else:onl1=0
        response_usd = requests.get('https://api.exchangerate-api.com/v4/latest/USD')
        data_usd = response_usd.json()
        usd = data_usd['rates']['BRL']
        response_gbp = requests.get('https://api.exchangerate-api.com/v4/latest/GBP')
        data_gbp = response_gbp.json()
        gbp = data_gbp['rates']['BRL']
        response_eur = requests.get('https://api.exchangerate-api.com/v4/latest/EUR')
        data_eur = response_eur.json()
        eur = data_eur['rates']['BRL']
        return render_template('home.html', data=data, contagem=str(len(data)), meses=meses, mes_atual=mes_atual, max=max, soma=soma, ent=ent, fis=fis, onl=onl, s=s, ent1=ent1, fis1=fis1, onl1=onl1, dolar=usd, libra=gbp, euro=eur)
    
@app.route('/d',methods=['POST'])
def d():
    export_to_csv()
    return redirect(url_for('home'))
    
    
@app.route('/add',methods=['GET','POST'])
def add():
    descricao = request.form['descr']
    valor = request.form['valo']
    categoria = request.form['cate']
    data = request.form['datas']
    with open('log.txt', 'a') as file:
        file.write("Step: ADD\n")
        file.write("Route /add \n")
        file.write("desc = "+str(descricao)+" \n")
        file.write("val = "+str(valor)+" \n")
        file.write("cat = "+str(categoria)+" \n")
        file.write("data = "+str(data)+" \n")
        file.write("\n")
    conn = sqlite3.connect('data.db')
    cur = conn.cursor()
    user=session.get('username')
    cur.execute('''INSERT INTO data(id_user, descricao, categoria, data, valor) values (?,?,?,?,?)''',(user,descricao,categoria,data,valor))
    conn.commit()
    conn.close()
    return redirect(url_for('home'))

@app.route('/delete/<int:id>',methods=['POST'])
def delete(id):
    conn = sqlite3.connect('data.db')
    cur = conn.cursor()
    cur.execute('''DELETE FROM data WHERE id=?''',(id,))
    conn.commit()
    conn.close()
    return redirect(url_for('home'))

@app.route('/filter', methods=['POST', 'GET'])
def filter():
    app.config['data']=filtro()
    return redirect(url_for('home'))

def filtro():
    diamin = request.form.get('diamin')
    diamax = request.form.get('diamax')
    valmin = request.form.get('valmin')
    valmax = request.form.get('valmax')
    conn=sqlite3.connect('data.db')
    cur=conn.cursor()
    user=session.get('username')
    cur.execute("SELECT * FROM data WHERE id_user = ? AND data > ? AND valor > ? AND data < ? AND valor < ? ORDER BY data", (user,diamin,valmin,diamax,valmax))
    data=cur.fetchall()
    conn.close
    return data
    
def export_to_csv():
    data=app.config['data']
    if not data:
        return  # Não há dados para exportar

    # Nome do arquivo CSV de saída
    filename = 'data.csv'

    # Abrir o arquivo CSV em modo de escrita
    with open(filename, 'w', newline='') as file:
        writer = csv.writer(file)

        # Escrever o cabeçalho
        header = ['ID', 'Descrição', 'Categoria', 'Data', 'Valor']
        writer.writerow(header)

        # Escrever os dados
        for row in data:
            writer.writerow(row[0:5])  # Supondo que os dados estejam nas colunas de índice 0 a 4

    return filename

if __name__ == '__main__':
    conn = sqlite3.connect('data.db')
    cur = conn.cursor()
    cur.execute('''CREATE TABLE IF NOT EXISTS users
    (id INTEGER PRIMARY KEY AUTOINCREMENT,
    user TEXT,
    pass TEXT)''')
    cur.execute('''CREATE TABLE IF NOT EXISTS data (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    id_user REAL NOT NULL,
    descricao TEXT NOT NULL,
    categoria TEXT,
    data TEXT,
    valor REAL
    )''')
    conn.close()
    app.run(debug=True)
