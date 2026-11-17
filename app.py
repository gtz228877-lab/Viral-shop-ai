import os
import sqlite3
from functools import wraps
from datetime import datetime, date
from flask import Flask, request, redirect, url_for, render_template_string, flash, session

APP_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(APP_DIR, "viral_shop.db")
app = Flask(__name__)
app.secret_key = os.environ.get("SECRET_KEY", "troque-esta-chave-antes-de-publicar")

def db():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    with db() as con:
        con.executescript("""
        CREATE TABLE IF NOT EXISTS products (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            category TEXT DEFAULT '',
            affiliate_url TEXT DEFAULT '',
            commission REAL DEFAULT 0,
            notes TEXT DEFAULT '',
            created_at TEXT NOT NULL
        );
        CREATE TABLE IF NOT EXISTS videos (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            product_id INTEGER,
            title TEXT NOT NULL,
            format TEXT DEFAULT 'Narração IA',
            caption TEXT DEFAULT '',
            hashtags TEXT DEFAULT '',
            status TEXT DEFAULT 'Ideia',
            scheduled_at TEXT DEFAULT '',
            created_at TEXT NOT NULL,
            FOREIGN KEY(product_id) REFERENCES products(id)
        );
        CREATE TABLE IF NOT EXISTS earnings (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            description TEXT NOT NULL,
            amount REAL NOT NULL,
            status TEXT DEFAULT 'Pendente',
            earned_on TEXT NOT NULL
        );
        """)

LOGIN_PAGE = r\"\"\"
<!doctype html><html lang=\"pt-br\"><meta charset=\"utf-8\"><meta name=\"viewport\" content=\"width=device-width, initial-scale=1\">
<title>Entrar — Viral Shop AI</title><body style=\"background:#101116;color:white;font-family:Arial;padding:24px\">
<div style=\"max-width:380px;margin:12vh auto;background:#1b1e28;padding:22px;border-radius:14px\">
<h2>🛍️ Viral Shop AI</h2><p>Entre com a senha administrativa configurada no servidor.</p>
<form method=\"post\"><input name=\"password\" type=\"password\" required placeholder=\"Senha\" style=\"width:100%;padding:12px;box-sizing:border-box\">
<p><button style=\"padding:11px 16px\">Entrar</button></p></form>{{error}}</div></body></html>
\"\"\"

def login_required(fn):
    @wraps(fn)
    def wrapper(*args, **kwargs):
        if not session.get("authenticated"):
            return redirect(url_for("login"))
        return fn(*args, **kwargs)
    return wrapper

@app.route("/login", methods=["GET", "POST"])
def login():
    expected = os.environ.get("ADMIN_PASSWORD")
    error = ""
    if request.method == "POST":
        if not expected:
            error = "O administrador ainda não configurou ADMIN_PASSWORD no servidor."
        elif request.form.get("password") == expected:
            session["authenticated"] = True
            return redirect(url_for("home"))
        else:
            error = "Senha incorreta."
    return render_template_string(LOGIN_PAGE, error=error)

@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("login"))

PAGE = r\"\"\"
<!doctype html>
<html lang="pt-br">
<head>
<meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1">
<title>Viral Shop AI</title>
<style>
:root{font-family:Arial,sans-serif;color:#f5f5f7;background:#101116}
*{box-sizing:border-box}body{margin:0}header{padding:22px 18px;background:#191b24;border-bottom:1px solid #30323d}
h1{margin:0;font-size:25px}header p{margin:6px 0 0;color:#aeb1bf;font-size:13px}
main{max-width:1050px;margin:auto;padding:18px}
.grid{display:grid;grid-template-columns:repeat(auto-fit,minmax(190px,1fr));gap:12px}
.card{background:#1b1e28;border:1px solid #303441;border-radius:14px;padding:16px;margin-bottom:14px}
.metric{font-size:28px;font-weight:bold;margin-top:8px}.muted{color:#aeb1bf;font-size:13px}
h2{font-size:18px;margin:0 0 14px}.tabs{display:flex;gap:8px;flex-wrap:wrap;margin:16px 0}
.tabs a,.btn{background:#333849;color:white;text-decoration:none;padding:10px 13px;border:0;border-radius:9px;display:inline-block}
.btn.primary{background:#d52d73}.btn.small{padding:7px 10px;font-size:12px}
label{display:block;font-size:13px;color:#c9cbd4;margin:10px 0 5px}
input,select,textarea{width:100%;padding:11px;border-radius:8px;border:1px solid #414656;background:#11141b;color:white}
textarea{min-height:75px}button{cursor:pointer}.row{display:grid;grid-template-columns:repeat(auto-fit,minmax(180px,1fr));gap:10px}
table{width:100%;border-collapse:collapse;font-size:13px}td,th{text-align:left;padding:10px 7px;border-bottom:1px solid #343744;vertical-align:top}
th{color:#aeb1bf}.pill{background:#343849;border-radius:20px;padding:4px 8px;font-size:11px}
.notice{border-left:3px solid #e5a23b;padding:10px 12px;background:#29251d;color:#f2d8a8;font-size:13px;border-radius:5px;margin-bottom:14px}
.flash{background:#233d31;padding:10px;border-radius:8px;margin-bottom:12px}
@media(max-width:560px){main{padding:12px}td,th{padding:8px 4px;font-size:12px}}
</style></head>
<body>
<header><h1>🛍️ Viral Shop AI</h1><p>Painel de organização para afiliados TikTok Shop</p></header>
<main>
{% with messages = get_flashed_messages() %}{% for msg in messages %}<div class="flash">{{msg}}</div>{% endfor %}{% endwith %}
<div class="notice">Esta versão organiza produtos, ideias, agenda e comissões. Ela ainda não publica no TikTok nem acessa sua conta. A publicação exige integração oficial aprovada e autorização da conta.</div>
<div class="grid">
<div class="card"><div class="muted">Produtos cadastrados</div><div class="metric">{{product_count}}</div></div>
<div class="card"><div class="muted">Vídeos na fila / ideias</div><div class="metric">{{video_count}}</div></div>
<div class="card"><div class="muted">Comissões registradas</div><div class="metric">R$ {{'%.2f'|format(total)}}</div></div>
<div class="card"><div class="muted">Comissões pendentes</div><div class="metric">R$ {{'%.2f'|format(pending)}}</div></div>
</div>
<div class="tabs">
<a href="#produtos">Produtos</a><a href="#videos">Vídeos</a><a href="#ganhos">Comissões</a>
</div>
<section class="card" id="produtos">
<h2>＋ Cadastrar produto afiliado</h2>
<form method="post" action="/product">
<label>Nome do produto</label><input name="name" required placeholder="Ex.: Fone Bluetooth">
<div class="row"><div><label>Categoria</label><input name="category" placeholder="Eletrônicos, beleza..."></div>
<div><label>Comissão estimada (R$)</label><input name="commission" type="number" step="0.01" min="0" value="0"></div></div>
<label>Seu link de afiliado</label><input name="affiliate_url" type="url" placeholder="https://...">
<label>Observações</label><textarea name="notes" placeholder="Preço, benefícios, público..."></textarea>
<p><button class="btn primary">Salvar produto</button></p></form>
{% if products %}<h2>Seus produtos</h2><table><tr><th>Produto</th><th>Categoria</th><th>Comissão estimada</th><th>Link</th></tr>
{% for p in products %}<tr><td>{{p.name}}</td><td>{{p.category}}</td><td>R$ {{'%.2f'|format(p.commission)}}</td><td>{% if p.affiliate_url %}<a style="color:#f18ab4" href="{{p.affiliate_url}}" target="_blank" rel="noopener">Abrir link</a>{% else %}—{% endif %}</td></tr>{% endfor %}</table>{% endif %}
</section>
<section class="card" id="videos">
<h2>＋ Planejar vídeo</h2>
<form method="post" action="/video">
<label>Título / ideia do vídeo</label><input name="title" required placeholder="Ex.: 3 motivos para testar este produto">
<div class="row"><div><label>Produto</label><select name="product_id"><option value="">Sem produto vinculado</option>{% for p in products %}<option value="{{p.id}}">{{p.name}}</option>{% endfor %}</select></div>
<div><label>Formato</label><select name="format">{% for f in ['Narração IA','Imagens do produto','Avatar IA','Demonstração','Misturado'] %}<option>{{f}}</option>{% endfor %}</select></div>
<div><label>Status</label><select name="status">{% for s in ['Ideia','Em produção','Aguardando revisão','Aprovado para publicar','Publicado manualmente'] %}<option>{{s}}</option>{% endfor %}</select></div></div>
<label>Legenda</label><textarea name="caption" placeholder="Escreva a legenda..."></textarea>
<label>Hashtags</label><input name="hashtags" placeholder="#TikTokShop #achadinhos">
<label>Data/hora planejada (opcional)</label><input name="scheduled_at" type="datetime-local">
<p><button class="btn primary">Salvar vídeo</button></p></form>
{% if videos %}<h2>Fila de conteúdo</h2><table><tr><th>Vídeo</th><th>Formato</th><th>Status</th><th>Planejado</th></tr>
{% for v in videos %}<tr><td>{{v.title}}<div class="muted">{{v.product_name or 'Sem produto'}}</div></td><td>{{v.format}}</td><td><span class="pill">{{v.status}}</span></td><td>{{v.scheduled_at or '—'}}</td></tr>{% endfor %}</table>{% endif %}
</section>
<section class="card" id="ganhos">
<h2>＋ Registrar comissão</h2>
<form method="post" action="/earning">
<label>Descrição da venda / comissão</label><input name="description" required placeholder="Ex.: Comissão do produto X">
<div class="row"><div><label>Valor (R$)</label><input name="amount" type="number" min="0" step="0.01" required></div>
<div><label>Status</label><select name="status"><option>Pendente</option><option>Confirmada</option><option>Recebida</option></select></div>
<div><label>Data</label><input name="earned_on" type="date" value="{{today}}"></div></div>
<p><button class="btn primary">Registrar comissão</button></p></form>
{% if earnings %}<table><tr><th>Descrição</th><th>Valor</th><th>Status</th><th>Data</th></tr>{% for e in earnings %}<tr><td>{{e.description}}</td><td>R$ {{'%.2f'|format(e.amount)}}</td><td>{{e.status}}</td><td>{{e.earned_on}}</td></tr>{% endfor %}</table>{% endif %}
</section>
<p class="muted">Dica: use apenas links de afiliado oficiais e conteúdos autorizados. Não invente avaliações, resultados ou características dos produtos.</p>
</main></body></html>
"""

@app.route("/")
@login_required
def home():
    with db() as con:
        products = con.execute("SELECT * FROM products ORDER BY id DESC").fetchall()
        videos = con.execute("""SELECT videos.*, products.name AS product_name FROM videos
            LEFT JOIN products ON videos.product_id=products.id ORDER BY videos.id DESC""").fetchall()
        earnings = con.execute("SELECT * FROM earnings ORDER BY id DESC").fetchall()
        total = con.execute("SELECT COALESCE(SUM(amount),0) FROM earnings").fetchone()[0]
        pending = con.execute("SELECT COALESCE(SUM(amount),0) FROM earnings WHERE status='Pendente'").fetchone()[0]
    return render_template_string(PAGE, products=products, videos=videos, earnings=earnings,
        product_count=len(products), video_count=len(videos), total=total, pending=pending,
        today=date.today().isoformat())

@app.post("/product")
@login_required
def add_product():
    name = request.form.get("name","").strip()
    if not name:
        flash("Informe o nome do produto.")
        return redirect(url_for("home") + "#produtos")
    try: commission = max(0, float(request.form.get("commission") or 0))
    except ValueError: commission = 0
    with db() as con:
        con.execute("INSERT INTO products(name,category,affiliate_url,commission,notes,created_at) VALUES(?,?,?,?,?,?)",
            (name, request.form.get("category",""), request.form.get("affiliate_url",""),
             commission, request.form.get("notes",""), datetime.now().isoformat(timespec="minutes")))
    flash("Produto salvo!")
    return redirect(url_for("home") + "#produtos")

@app.post("/video")
@login_required
def add_video():
    title = request.form.get("title","").strip()
    if not title:
        flash("Informe o título/ideia do vídeo.")
        return redirect(url_for("home") + "#videos")
    pid = request.form.get("product_id") or None
    scheduled = request.form.get("scheduled_at","")
    with db() as con:
        con.execute("INSERT INTO videos(product_id,title,format,caption,hashtags,status,scheduled_at,created_at) VALUES(?,?,?,?,?,?,?,?)",
            (pid, title, request.form.get("format","Narração IA"), request.form.get("caption",""),
             request.form.get("hashtags",""), request.form.get("status","Ideia"), scheduled,
             datetime.now().isoformat(timespec="minutes")))
    flash("Vídeo adicionado à sua fila!")
    return redirect(url_for("home") + "#videos")

@app.post("/earning")
@login_required
def add_earning():
    description = request.form.get("description","").strip()
    try: amount = float(request.form.get("amount"))
    except (TypeError, ValueError): amount = -1
    if not description or amount < 0:
        flash("Informe uma descrição e um valor válido.")
        return redirect(url_for("home") + "#ganhos")
    with db() as con:
        con.execute("INSERT INTO earnings(description,amount,status,earned_on) VALUES(?,?,?,?)",
            (description, amount, request.form.get("status","Pendente"), request.form.get("earned_on") or date.today().isoformat()))
    flash("Comissão registrada!")
    return redirect(url_for("home") + "#ganhos")

init_db()
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)), debug=False)
