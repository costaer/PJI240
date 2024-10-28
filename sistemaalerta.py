import streamlit as st
import sqlite3
from datetime import datetime, timedelta

# Conectar ao banco de dados
conn = sqlite3.connect('estoque.db')
c = conn.cursor()

# Criar tabela se não existir
c.execute('''CREATE TABLE IF NOT EXISTS produtos (
                id INTEGER PRIMARY KEY,
                nome TEXT,
                data_compra DATE,
                data_validade DATE,
                quantidade INTEGER
            )''')

# Função para adicionar produto ao estoque ou atualizar quantidade
def adicionar_produto(nome, data_compra, data_validade, quantidade):
    c.execute('''SELECT * FROM produtos WHERE nome = ? AND data_compra = ? AND data_validade = ?''',
              (nome, data_compra, data_validade))
    produto_existente = c.fetchone()
    if produto_existente:
        nova_quantidade = produto_existente[4] + quantidade
        c.execute('''UPDATE produtos SET quantidade = ? WHERE id = ?''', (nova_quantidade, produto_existente[0]))
    else:
        c.execute('''INSERT INTO produtos (nome, data_compra, data_validade, quantidade)
                      VALUES (?, ?, ?, ?)''', (nome, data_compra, data_validade, quantidade))
    conn.commit()

# Função para buscar todos os produtos ordenados por nome
def buscar_produtos():
    c.execute('''SELECT * FROM produtos ORDER BY nome''')
    return c.fetchall()

# Função para identificar produtos próximos da validade
def produtos_proximos_validade(dias_alerta=7):
    hoje = datetime.today()
    data_limite = hoje + timedelta(days=dias_alerta)
    c.execute('''SELECT * FROM produtos WHERE data_validade <= ? AND quantidade > 0''', (data_limite.strftime("%Y-%m-%d"),))
    return c.fetchall()

# Interface do Streamlit
st.title('Controle de Estoque com Alerta de Validade')

# Lista de produtos disponíveis
opcoes_produtos = ['Arroz', 'Feijão', 'Óleo', 'Açúcar', 'Café moído', 'Sal', 'Extrato de tomate',
                   'Vinagre', 'Bolacha recheada', 'Bolacha salgada', 'Macarrão Espaguete',
                   'Macarrão parafuso', 'Macarrão instantâneo', 'Farinha de trigo', 'Farinha temperada',
                   'Achocolatado em pó', 'Leite', 'Goiabada', 'Suco em pó', 'Mistura para bolo', 'Tempero',
                   'Sardinha', 'Creme dental', 'Papel higiênico', 'Sabonete', 'Milharina']

opcoes_produtos.sort()  # Ordenar os produtos em ordem alfabética

# Barra lateral para cadastrar produtos
st.sidebar.header('Cadastrar Produto')
nome_produto = st.sidebar.selectbox('Nome do Produto', opcoes_produtos)
data_compra = st.sidebar.date_input('Data da Compra')
data_validade = st.sidebar.date_input('Data de Validade')
quantidade = st.sidebar.number_input('Quantidade', min_value=1, value=1)
adicionar = st.sidebar.button('Adicionar Produto')

if adicionar:
    adicionar_produto(nome_produto, data_compra, data_validade, quantidade)
    st.sidebar.success('Produto adicionado com sucesso!')

# Alerta de produtos próximos do vencimento
st.header('Alerta de Validade')
produtos_alerta = produtos_proximos_validade()
if produtos_alerta:
    st.warning("Atenção! Os seguintes produtos estão próximos do vencimento:")
    for produto in produtos_alerta:
        st.write(f"{produto[1]} - Validade: {produto[3]} - Quantidade: {produto[4]}")
else:
    st.info("Nenhum produto próximo do vencimento.")

# Exibir estoque
st.header('Estoque Atual')
produtos_estoque = buscar_produtos()
for produto in produtos_estoque:
    st.write(f"{produto[4]} x {produto[1]} - Compra: {produto[2]} - Validade: {produto[3]}")

# Fechar conexão com o banco de dados
conn.close()
