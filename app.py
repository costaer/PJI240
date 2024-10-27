from flask import Flask, render_template, request, redirect, url_for, send_file
import sqlite3
import csv
import os
from datetime import datetime

app = Flask(__name__)

# Variável de ambiente para o caminho do banco (Railway-friendly)
DATABASE_URL = os.getenv('DATABASE_URL', 'cesta.db')

# Função para conectar ao banco de dados
def get_db_connection():
    conn = sqlite3.connect'(DATABASE_URL')
    cursor = conn.cursor()
    conn.row_factory = sqlite3.Row
    return conn

# Função para inicializar o banco se não existir
def init_db():
    if not os.path.exists(DATABASE_URL):
        conn = get_db_connection()
        conn.execute('''
            CREATE TABLE produtos (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                nome TEXT,
                data_compra TEXT,
                data_validade TEXT,
                quantidade INTEGER
            )
        ''')
        conn.execute('''
            CREATE TABLE cestas (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                codigo TEXT,
                data_montagem TEXT,
                tipo TEXT,
                itens TEXT
            )
        ''')
        conn.close()

# Inicializa o banco
init_db()

# Lista de produtos fixos em ordem alfabética
PRODUTOS = sorted([
    "Achocolatado em pó", "Arroz", "Açúcar", "Bolacha recheada", "Bolacha salgada",
    "Café moído", "Creme dental", "Extrato de tomate", "Farinha de trigo", 
    "Farinha temperada", "Feijão", "Goiabada", "Leite", "Macarrão Espaguete",
    "Macarrão instantâneo", "Macarrão parafuso", "Milharina", "Mistura para bolo",
    "Óleo", "Papel higiênico", "Sabonete", "Sal", "Sardinha", "Suco em pó",
    "Tempero", "Vinagre"
])

# Página principal
@app.route('/')
def index():
    conn = get_db_connection()
    produtos = conn.execute('SELECT * FROM produtos ORDER BY data_validade').fetchall()
    cestas = conn.execute('SELECT * FROM cestas ORDER BY id DESC').fetchall()
    conn.close()
    return render_template('index.html', produtos=produtos, cestas=cestas, produtos_opcoes=PRODUTOS)

# Rota para cadastrar produto
@app.route('/cadastrar', methods=['POST'])
def cadastrar():
    nome = request.form['nome']
    data_compra = request.form['data_compra']
    data_validade = request.form['data_validade']
    quantidade = int(request.form['quantidade'])

    conn = get_db_connection()
    conn.execute(
        'INSERT INTO produtos (nome, data_compra, data_validade, quantidade) VALUES (?, ?, ?, ?)',
        (nome, data_compra, data_validade, quantidade)
    )
    conn.commit()
    conn.close()
    return redirect(url_for('index'))

# Rota para montar cestas
@app.route('/montar_cesta/<tipo>', methods=['POST'])
def montar_cesta(tipo):
    data_montagem = datetime.now().strftime('%d%m%Y')
    itens_pequena = [
        'Arroz', 'Feijão', 'Óleo', 'Açúcar', 'Café moído', 'Sal', 'Extrato de tomate',
        'Bolacha recheada', 'Macarrão Espaguete', 'Farinha de trigo', 'Farinha temperada',
        'Goiabada', 'Suco em pó', 'Sardinha', 'Creme dental', 'Papel higiênico', 'Sabonete', 'Milharina', 'Tempero'
    ]
    itens_grande = itens_pequena + [
        'Vinagre', 'Bolacha salgada', 'Macarrão parafuso', 'Macarrão instantâneo',
        'Achocolatado em pó', 'Leite', 'Mistura para bolo'
    ]
    itens = itens_pequena if tipo == 'pequena' else itens_grande
    codigo = f"{data_montagem}{str(len(itens)).zfill(3)}"

    conn = get_db_connection()
    conn.execute(
        'INSERT INTO cestas (codigo, data_montagem, tipo, itens) VALUES (?, ?, ?, ?)',
        (codigo, data_montagem, tipo, ', '.join(itens))
    )
    conn.commit()
    conn.close()
    return redirect(url_for('index'))

# Rota para baixar lista de uma cesta
@app.route('/baixar/<int:id>')
def baixar(id):
    conn = get_db_connection()
    cesta = conn.execute('SELECT * FROM cestas WHERE id = ?', (id,)).fetchone()
    conn.close()

    filename = f"cesta_{cesta['codigo']}.csv"
    with open(filename, 'w', newline='') as f:
        writer = csv.writer(f)
        writer.writerow(['Código', 'Data', 'Tipo', 'Itens'])
        writer.writerow([cesta['codigo'], cesta['data_montagem'], cesta['tipo'], cesta['itens']])

    return send_file(filename, as_attachment=True)

if __name__ == '__main__':
    app.run(debug=True)