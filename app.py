# app.py

from flask import Flask, render_template, request, redirect, url_for, flash
from datetime import datetime, timedelta

app = Flask(__name__)
app.secret_key = 'supersecretkey'  # Chave de segurança para mensagens flash

# Estoque e histórico mantidos em memória (lista simples)
estoque = []
historico = []

# Lista de produtos disponíveis
produtos_disponiveis = [
    "Arroz", "Feijão", "Óleo", "Açúcar", "Café moído", "Sal", "Extrato de tomate",
    "Vinagre", "Bolacha recheada", "Bolacha salgada", "Macarrão Espaguete",
    "Macarrão parafuso", "Macarrão instantâneo", "Farinha de trigo", 
    "Farinha temperada", "Achocolatado em pó", "Leite", "Goiabada", "Suco em pó", 
    "Mistura para bolo", "Tempero", "Sardinha", "Creme dental", "Papel higiênico", 
    "Sabonete", "Milharina"
]

# Tipos de cestas básicas
cesta_pequena = [
    "Arroz", "Feijão", "Óleo", "Açúcar", "Café moído", "Sal", "Extrato de tomate",
    "Bolacha recheada", "Macarrão Espaguete", "Farinha de trigo", 
    "Farinha temperada", "Goiabada", "Suco em pó", "Sardinha", "Creme dental", 
    "Papel higiênico", "Sabonete", "Milharina", "Tempero"
]

cesta_grande = cesta_pequena + [
    "Vinagre", "Bolacha salgada", "Macarrão parafuso", "Macarrão instantâneo", 
    "Achocolatado em pó", "Leite", "Mistura para bolo"
]

def verificar_alertas():
    """Verifica quais produtos estão próximos de vencer."""
    hoje = datetime.today()
    return [p for p in estoque if p['data_validade'] <= hoje + timedelta(days=7)]

@app.route('/')
def index():
    alertas = verificar_alertas()
    return render_template('index.html', estoque=estoque, alertas=alertas)

@app.route('/adicionar', methods=['POST'])
def adicionar():
    """Adiciona um produto ao estoque."""
    nome = request.form['nome']
    data_compra = datetime.strptime(request.form['data_compra'], '%Y-%m-%d')
    data_validade = datetime.strptime(request.form['data_validade'], '%Y-%m-%d')
    quantidade = int(request.form['quantidade'])
    produto_id = request.form['produto_id']

    estoque.append({
        'id': produto_id,
        'nome': nome,
        'data_compra': data_compra,
        'data_validade': data_validade,
        'quantidade': quantidade
    })
    flash('Produto adicionado com sucesso!')
    return redirect(url_for('index'))

@app.route('/montar_cesta/<tipo>')
def montar_cesta(tipo):
    """Monta uma cesta e atualiza o estoque."""
    cesta = cesta_pequena if tipo == 'pequena' else cesta_grande
    itens_cesta = []

    for nome in cesta:
        produto = next((p for p in estoque if p['nome'] == nome and p['quantidade'] > 0), None)
        if produto:
            produto['quantidade'] -= 1
            itens_cesta.append(produto)

    historico.append({
        'tipo': tipo,
        'itens': itens_cesta,
        'data': datetime.today()
    })

    flash(f'Cesta {tipo} montada com sucesso!')
    return redirect(url_for('historico_view'))

@app.route('/historico')
def historico_view():
    """Exibe o histórico de cestas montadas."""
    return render_template('historico.html', historico=historico)

if __name__ == '__main__':
    app.run(debug=True)