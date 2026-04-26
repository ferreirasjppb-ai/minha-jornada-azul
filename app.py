# ============================================================
# app.py — Arquivo principal do blog
# Flask é o "motor" do site. Ele recebe as visitas e decide
# qual página mostrar para cada endereço (URL).
# ============================================================

from flask import Flask, render_template, request, redirect, url_for
import sqlite3  # Banco de dados simples, já vem com Python
from datetime import datetime

# Cria o aplicativo Flask
app = Flask(__name__)

# ============================================================
# BANCO DE DADOS
# SQLite é um banco de dados simples guardado num arquivo .db
# Não precisa instalar nada separado — já vem com Python!
# ============================================================

def get_db():
    """Abre conexão com o banco de dados."""
    conn = sqlite3.connect('database.db')
    conn.row_factory = sqlite3.Row  # Permite acessar colunas pelo nome
    return conn

def init_db():
    """Cria as tabelas do banco se ainda não existirem."""
    conn = get_db()
    cursor = conn.cursor()

    # Tabela de posts do blog
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS posts (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            titulo TEXT NOT NULL,
            conteudo TEXT NOT NULL,
            categoria TEXT NOT NULL,
            data_criacao TEXT NOT NULL
        )
    ''')

    # Tabela de comentários (ligados a um post pelo post_id)
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

    # Tabela do fórum (tópicos independentes)
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS topicos (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            titulo TEXT NOT NULL,
            conteudo TEXT NOT NULL,
            pseudonimo TEXT NOT NULL,
            data_criacao TEXT NOT NULL
        )
    ''')

    # Tabela de respostas do fórum
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

# ============================================================
# ROTAS — Cada @app.route define uma URL do site
# ============================================================

# --- PÁGINA INICIAL ---
@app.route('/')
def index():
    conn = get_db()
    # Busca os 6 posts mais recentes para mostrar na home
    posts = conn.execute(
        'SELECT * FROM posts ORDER BY id DESC LIMIT 6'
    ).fetchall()
    conn.close()
    return render_template('index.html', posts=posts)


# --- PÁGINA SOBRE ---
@app.route('/sobre')
def sobre():
    return render_template('sobre.html')


# --- VER UM POST COMPLETO ---
@app.route('/post/<int:post_id>')
def ver_post(post_id):
    conn = get_db()
    # Busca o post pelo ID
    post = conn.execute('SELECT * FROM posts WHERE id = ?', (post_id,)).fetchone()
    # Busca os comentários desse post
    comentarios = conn.execute(
        'SELECT * FROM comentarios WHERE post_id = ? ORDER BY id DESC', (post_id,)
    ).fetchall()
    conn.close()

    if post is None:
        return "Post não encontrado", 404

    return render_template('post.html', post=post, comentarios=comentarios)


# --- ADICIONAR COMENTÁRIO ---
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
    # Redireciona de volta ao post após comentar
    return redirect(url_for('ver_post', post_id=post_id))


# --- NOVO POST (página para escrever) ---
@app.route('/novo-post', methods=['GET', 'POST'])
def novo_post():
    if request.method == 'POST':
        # Quando o formulário é enviado, salva no banco
        titulo = request.form['titulo']
        conteudo = request.form['conteudo']
        categoria = request.form['categoria']
        data = datetime.now().strftime('%d/%m/%Y às %H:%M')

        conn = get_db()
        conn.execute(
            'INSERT INTO posts (titulo, conteudo, categoria, data_criacao) VALUES (?, ?, ?, ?)',
            (titulo, conteudo, categoria, data)
        )
        conn.commit()
        conn.close()
        return redirect(url_for('index'))

    # GET: só mostra o formulário
    return render_template('novo_post.html')


# --- FÓRUM ---
@app.route('/forum')
def forum():
    conn = get_db()
    topicos = conn.execute(
        'SELECT * FROM topicos ORDER BY id DESC'
    ).fetchall()
    conn.close()
    return render_template('forum.html', topicos=topicos)


# --- VER TÓPICO DO FÓRUM ---
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

    return render_template('topico.html', topico=topico, respostas=respostas)


# --- CRIAR TÓPICO NO FÓRUM ---
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

    return render_template('novo_topico.html')


# --- RESPONDER TÓPICO ---
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


# --- POSTS POR CATEGORIA ---
@app.route('/categoria/<categoria>')
def por_categoria(categoria):
    conn = get_db()
    posts = conn.execute(
        'SELECT * FROM posts WHERE categoria = ? ORDER BY id DESC', (categoria,)
    ).fetchall()
    conn.close()
    return render_template('index.html', posts=posts, categoria_atual=categoria)


# ============================================================
# INICIALIZAÇÃO
# Quando rodar "python app.py", isso executa tudo abaixo
# ============================================================
if __name__ == '__main__':
    init_db()       # Cria o banco de dados se não existir
    app.run(debug=True)  # debug=True mostra erros detalhados durante desenvolvimento
