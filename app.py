from flask import Flask, render_template, request, redirect, url_for, session
import sqlite3
from datetime import datetime

app = Flask(__name__)
app.secret_key = 'jornada_azul_secreta_2024'

USUARIOS = {
    'Aurora': '08012021tsa',
    'Sirius': '08012021tsa'
}

def get_db():
    conn = sqlite3.connect('database.db')
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS posts (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            titulo TEXT NOT NULL,
            conteudo TEXT NOT NULL,
            categoria TEXT NOT NULL,
            autor TEXT NOT NULL,
            data_criacao TEXT NOT NULL
        )
    ''')
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS comentarios (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            post_id INTEGER NOT NULL,
            pseudonimo TEXT NOT NULL,
            texto TEXT NOT NULL,
            data_criacao TEXT NOT NULL,
            FOREIGN KEY (post_id) REFERENCES posts(id)
        )
    ''')
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS topicos (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            titulo TEXT NOT NULL,
            conteudo TEXT NOT NULL,
            pseudonimo TEXT NOT NULL,
            data_criacao TEXT NOT NULL
        )
    ''')
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS respostas_forum (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            topico_id INTEGER NOT NULL,
            pseudonimo TEXT NOT NULL,
            texto TEXT NOT NULL,
            data_criacao TEXT NOT NULL,
            FOREIGN KEY (topico_id) REFERENCES topicos(id)
        )
    ''')
    conn.commit()
    conn.close()

def admin_logado():
    return 'usuario' in session

@app.route('/admin/login', methods=['GET', 'POST'])
def login():
    erro = None
    if request.method == 'POST':
        usuario = request.form['usuario']
        senha = request.form['senha']
        if usuario in USUARIOS and USUARIOS[usuario] == senha:
            session['usuario'] = usuario
            return redirect(url_for('index'))
        else:
            erro = 'Usuário ou senha incorretos.'
    return render_template('login.html', erro=erro)

@app.route('/admin/logout')
def logout():
    session.pop('usuario', None)
    return redirect(url_for('index'))

@app.route('/')
def index():
    conn = get_db()
    posts = conn.execute('SELECT * FROM posts ORDER BY id DESC LIMIT 6').fetchall()
    conn.close()
    return render_template('index.html', posts=posts, admin=admin_logado(), usuario=session.get('usuario'))

@app.route('/sobre')
def sobre():
    return render_template('sobre.html', admin=admin_logado(), usuario=session.get('usuario'))

@app.route('/post/<int:post_id>')
def ver_post(post_id):
    conn = get_db()
    post = conn.execute('SELECT * FROM posts WHERE id = ?', (post_id,)).fetchone()
    comentarios = conn.execute(
        'SELECT * FROM comentarios WHERE post_id = ? ORDER BY id DESC', (post_id,)
    ).fetchall()
    conn.close()
    if post is None:
        return "Post não encontrado", 404
    return render_template('post.html', post=post, comentarios=comentarios, admin=admin_logado(), usuario=session.get('usuario'))

@app.route('/comentar/<int:post_id>', methods=['POST'])
def comentar(post_id):
    pseudonimo = request.form['pseudonimo']
    texto = request.form['texto']
    data = datetime.now().strftime('%d/%m/%Y às %H:%M')
    conn = get_db()
    conn.execute(
        'INSERT INTO comentarios (post_id, pseudonimo, texto, data_criacao) VALUES (?, ?, ?, ?)',
        (post_id, pseudonimo, texto, data)
    )
    conn.commit()
    conn.close()
    return redirect(url_for('ver_post', post_id=post_id))

@app.route('/novo-post', methods=['GET', 'POST'])
def novo_post():
    if request.method == 'POST':
        titulo = request.form['titulo']
        conteudo = request.form['conteudo']
        categoria = request.form['categoria']
        autor = request.form.get('pseudonimo', 'Anônimo')
        data = datetime.now().strftime('%d/%m/%Y às %H:%M')
        conn = get_db()
        conn.execute(
            'INSERT INTO posts (titulo, conteudo, categoria, autor, data_criacao) VALUES (?, ?, ?, ?, ?)',
            (titulo, conteudo, categoria, autor, data)
        )
        conn.commit()
        conn.close()
        return redirect(url_for('index'))
    return render_template('novo_post.html', admin=admin_logado(), usuario=session.get('usuario'))

@app.route('/forum')
def forum():
    conn = get_db()
    topicos = conn.execute('SELECT * FROM topicos ORDER BY id DESC').fetchall()
    conn.close()
    return render_template('forum.html', topicos=topicos, admin=admin_logado(), usuario=session.get('usuario'))

@app.route('/forum/topico/<int:topico_id>')
def ver_topico(topico_id):
    conn = get_db()
    topico = conn.execute('SELECT * FROM topicos WHERE id = ?', (topico_id,)).fetchone()
    respostas = conn.execute(
        'SELECT * FROM respostas_forum WHERE topico_id = ? ORDER BY id ASC', (topico_id,)
    ).fetchall()
    conn.close()
    if topico is None:
        return "Tópico não encontrado", 404
    return render_template('topico.html', topico=topico, respostas=respostas, admin=admin_logado(), usuario=session.get('usuario'))

@app.route('/forum/novo', methods=['GET', 'POST'])
def novo_topico():
    if request.method == 'POST':
        titulo = request.form['titulo']
        conteudo = request.form['conteudo']
        pseudonimo = request.form['pseudonimo']
        data = datetime.now().strftime('%d/%m/%Y às %H:%M')
        conn = get_db()
        conn.execute(
            'INSERT INTO topicos (titulo, conteudo, pseudonimo, data_criacao) VALUES (?, ?, ?, ?)',
            (titulo, conteudo, pseudonimo, data)
        )
        conn.commit()
        conn.close()
        return redirect(url_for('forum'))
    return render_template('novo_topico.html', admin=admin_logado(), usuario=session.get('usuario'))

@app.route('/forum/responder/<int:topico_id>', methods=['POST'])
def responder_topico(topico_id):
    pseudonimo = request.form['pseudonimo']
    texto = request.form['texto']
    data = datetime.now().strftime('%d/%m/%Y às %H:%M')
    conn = get_db()
    conn.execute(
        'INSERT INTO respostas_forum (topico_id, pseudonimo, texto, data_criacao) VALUES (?, ?, ?, ?)',
        (topico_id, pseudonimo, texto, data)
    )
    conn.commit()
    conn.close()
    return redirect(url_for('ver_topico', topico_id=topico_id))

@app.route('/categoria/<categoria>')
def por_categoria(categoria):
    conn = get_db()
    posts = conn.execute(
        'SELECT * FROM posts WHERE categoria = ? ORDER BY id DESC', (categoria,)
    ).fetchall()
    conn.close()
    return render_template('index.html', posts=posts, categoria_atual=categoria, admin=admin_logado(), usuario=session.get('usuario'))

if __name__ == '__main__':
    init_db()
    app.run(debug=True)
