# 💙 Minha Jornada Azul — Blog sobre Autismo

Blog criado em Python com Flask.
Minimalista, azul claro, seguro e anônimo.

---

## Como rodar no seu computador (VS Code)

### 1. Instale o Python
Acesse https://python.org e baixe a versão mais recente.
Durante a instalação, marque a opção "Add Python to PATH".

### 2. Abra a pasta no VS Code
- Abra o VS Code
- Vá em File → Open Folder
- Selecione a pasta `blog_autismo`

### 3. Abra o Terminal no VS Code
- Menu Terminal → New Terminal

### 4. Instale o Flask
No terminal, cole este comando:
```
pip install flask
```

### 5. Rode o site!
```
python app.py
```

### 6. Acesse no navegador
Abra o navegador e acesse:
```
http://localhost:5000
```

Pronto! O site está rodando. 🎉

---

## Estrutura do projeto

```
blog_autismo/
├── app.py              ← Arquivo principal (rotas e banco de dados)
├── requirements.txt    ← Lista de dependências
├── database.db         ← Banco de dados (criado automaticamente)
├── templates/          ← Páginas HTML
│   ├── base.html       ← Template base (menu e rodapé)
│   ├── index.html      ← Página inicial
│   ├── sobre.html      ← Página "Sobre mim"
│   ├── post.html       ← Post individual + comentários
│   ├── novo_post.html  ← Formulário de novo post
│   ├── forum.html      ← Lista de tópicos do fórum
│   ├── topico.html     ← Tópico individual + respostas
│   └── novo_topico.html← Formulário de novo tópico
└── static/
    └── style.css       ← Visual do site
```

---

## Funcionalidades

✅ Blog com posts e categorias
✅ Página "Sobre mim" anônima
✅ Comentários anônimos por pseudônimo
✅ Fórum com tópicos e respostas
✅ Visual azul claro e minimalista
✅ Funciona no celular (responsivo)
✅ Banco de dados simples (SQLite)

---

## Próximos passos (quando quiser evoluir)

- Publicar online grátis no Render.com
- Adicionar sistema de login para a autora
- Adicionar busca por posts
- Adicionar curtidas nos posts
