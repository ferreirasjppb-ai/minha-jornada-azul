from flask import Flask, render_template, request, redirect, url_for, session
import psycopg2
import psycopg2.extras
from datetime import datetime

app = Flask(__name__)
app.secret_key = 'jornada_azul_secreta_2024'

USUARIOS = {
    'Aurora': '08012021tsa',
    'Sirius': '08012021tsa'
}

DATABASE_URL = "postgresql://postgres:Jornada%402024Azul@db.elmssbcalftgfhkelac.supabase.co:5432/postgres"

def get_db():
    conn = psycopg2.connect(DATABASE_URL)
    return conn

def init_db():
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS posts (
            id SERIAL PRIMARY KEY,
            titulo TEXT NOT NULL,
            conteudo TEXT NOT NULL,
            categoria TEXT NOT NULL,
            autor TEXT NOT NULL,
            data_criacao TEXT NOT NULL
        )
    ''')
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS comentarios (
            id SERIAL PRIMARY KEY,
            post_id INTEGER NOT NULL,
            pseudonimo TEXT NOT NULL,
            texto TEXT NOT NULL,
            data_criacao TEXT NOT NULL
        )
    ''')
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS topicos (
            id SERIAL PRIMARY KEY,
            titulo TEXT NOT NULL,
            conteudo TEXT NOT NULL,
            pseudonimo TEXT NOT NULL,
            data_criacao TEXT NOT NULL
        )
    ''')
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS respostas_forum (
            id SERIAL PRIMARY KEY,
            topico_id INTEGER NOT NULL,
            pseudonimo TEXT NOT NULL,
            texto TEXT NOT NULL,
            data_criacao TEXT NOT NULL
        )
    ''')
    conn.commit()
    cursor.close()
    conn.close()

init_db()

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
    cursor = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
    cursor.execute('SELECT * FROM posts ORDER BY id DESC LIMIT 6')
    posts = cursor.fetchall()
    cursor.close()
    conn.close()
    return render_template('index.html', posts=posts, admin=admin_logado(), usuario=session.get('usuario'))

@app.route('/sobre')
def sobre():
    return render_template('sobre.html', admin=admin_logado(), usuario=session.get('usuario'))

@app.route('/post/<int:post_id>')
def ver_post(post_id):
    conn = get_db()
    cursor = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
    cursor.execute('SELECT * FROM posts WHERE id = %s', (post_id,))
    post = cursor.fetchone()
    cursor.execute('SELECT * FROM comentarios WHERE post_id = %s ORDER BY id DESC', (post_id,))
    comentarios = cursor.fetchall()
    cursor.close()
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
    cursor = conn.cursor()
    cursor.execute(
        'INSERT INTO comentarios (post_id, pseudonimo, texto, data_criacao) VALUES (%s, %s, %s, %s)',
        (post_id, pseudonimo, texto, data)
    )
    conn.commit()
    cursor.close()
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
        cursor = conn.cursor()
        cursor.execute(
            'INSERT INTO posts (titulo, conteudo, categoria, autor, data_criacao) VALUES (%s, %s, %s, %s, %s)',
            (titulo, conteudo, categoria, autor, data)
        )
        conn.commit()
        cursor.close()
        conn.close()
        return redirect(url_for('index'))
    return render_template('novo_post.html', admin=admin_logado(), usuario=session.get('usuario'))

@app.route('/forum')
def forum():
    conn = get_db()
    cursor = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
    cursor.execute('SELECT * FROM topicos ORDER BY id DESC')
    topicos = cursor.fetchall()
    cursor.close()
    conn.close()
    return render_template('forum.html', topicos=topicos, admin=admin_logado(), usuario=session.get('usuario'))

@app.route('/forum/topico/<int:topico_id>')
def ver_topico(topico_id):
    conn = get_db()
    cursor = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
    cursor.execute('SELECT * FROM topicos WHERE id = %s', (topico_id,))
    topico = cursor.fetchone()
    cursor.execute('SELECT * FROM respostas_forum WHERE topico_id = %s ORDER BY id ASC', (topico_id,))
    respostas = cursor.fetchall()
    cursor.close()
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
        cursor = conn.cursor()
        cursor.execute(
            'INSERT INTO topicos (titulo, conteudo, pseudonimo, data_criacao) VALUES (%s, %s, %s, %s)',
            (titulo, conteudo, pseudonimo, data)
        )
        conn.commit()
        cursor.close()
        conn.close()
        return redirect(url_for('forum'))
    return render_template('novo_topico.html', admin=admin_logado(), usuario=session.get('usuario'))

@app.route('/forum/responder/<int:topico_id>', methods=['POST'])
def responder_topico(topico_id):
    pseudonimo = request.form['pseudonimo']
    texto = request.form['texto']
    data = datetime.now().strftime('%d/%m/%Y às %H:%M')
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute(
        'INSERT INTO respostas_forum (topico_id, pseudonimo, texto, data_criacao) VALUES (%s, %s, %s, %s)',
        (topico_id, pseudonimo, texto, data)
    )
    conn.commit()
    cursor.close()
    conn.close()
    return redirect(url_for('ver_topico', topico_id=topico_id))

@app.route('/categoria/<categoria>')
def por_categoria(categoria):
    conn = get_db()
    cursor = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
    cursor.execute('SELECT * FROM posts WHERE categoria = %s ORDER BY id DESC', (categoria,))
    posts = cursor.fetchall()
    cursor.close()
    conn.close()
    return render_template('index.html', posts=posts, categoria_atual=categoria, admin=admin_logado(), usuario=session.get('usuario'))

if __name__ == '__main__':
    init_db()
    app.run(debug=True)