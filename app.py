import streamlit as st
import sqlite3
from datetime import datetime
import random

# Conexão com o banco de dados
conn = sqlite3.connect('estoque.db')
c = conn.cursor()

# Criar tabela de produtos, incluindo o campo de código
c.execute('''CREATE TABLE IF NOT EXISTS produtos (
                id INTEGER PRIMARY KEY,
                codigo TEXT UNIQUE,
                nome TEXT,
                data_compra DATE,
                data_validade DATE,
                quantidade INTEGER
            )''')

# Criar tabela para armazenar cestas montadas
c.execute('''CREATE TABLE IF NOT EXISTS cestas (
                id INTEGER PRIMARY KEY,
                codigo TEXT UNIQUE,
                tipo TEXT,
                data_montagem DATE
            )''')

# Criar tabela para armazenar itens de cada cesta
c.execute('''CREATE TABLE IF NOT EXISTS itens_cesta (
                id INTEGER PRIMARY KEY,
                cesta_id INTEGER,
                produto_codigo TEXT,
                quantidade INTEGER,
                FOREIGN KEY (cesta_id) REFERENCES cestas(id),
                FOREIGN KEY (produto_codigo) REFERENCES produtos(codigo)
            )''')

# Lista de produtos disponíveis
opcoes_produtos = ['Arroz', 'Feijão', 'Óleo', 'Açúcar', 'Café moído', 'Sal', 'Extrato de tomate',
                   'Vinagre', 'Bolacha recheada', 'Bolacha salgada', 'Macarrão Espaguete',
                   'Macarrão parafuso', 'Macarrão instantâneo', 'Farinha de trigo', 'Farinha temperada',
                   'Achocolatado em pó', 'Leite', 'Goiabada', 'Suco em pó', 'Mistura para bolo', 'Tempero',
                   'Sardinha', 'Creme dental', 'Papel higiênico', 'Sabonete', 'Milharina']

opcoes_produtos.sort()

# Função para gerar código único
def gerar_codigo(prefixo):
    return f"{prefixo}-{random.randint(1000, 9999)}"

# Função para adicionar produto ao estoque
def adicionar_produto(nome, data_compra, data_validade, quantidade):
    codigo = gerar_codigo("PROD")
    c.execute('''INSERT INTO produtos (codigo, nome, data_compra, data_validade, quantidade)
                 VALUES (?, ?, ?, ?, ?)''', (codigo, nome, data_compra, data_validade, quantidade))
    conn.commit()

# Função para buscar todos os produtos ordenados por nome
def buscar_produtos():
    c.execute('''SELECT * FROM produtos ORDER BY nome''')
    return c.fetchall()

# Função para montar uma cesta e adicionar ao banco
def montar_cesta(cesta, tipo):
    codigo_cesta = gerar_codigo("CESTA")
    data_montagem = datetime.now().strftime("%Y-%m-%d")
    c.execute('''INSERT INTO cestas (codigo, tipo, data_montagem) VALUES (?, ?, ?)''', (codigo_cesta, tipo, data_montagem))
    cesta_id = c.lastrowid
    
    for item in cesta:
        produtos = buscar_produto_por_nome(item)
        if produtos:
            produto = produtos[0]
            c.execute('''INSERT INTO itens_cesta (cesta_id, produto_codigo, quantidade)
                         VALUES (?, ?, ?)''', (cesta_id, produto[1], 1))  # quantidade fixa 1 para cada item
    
    conn.commit()
    return codigo_cesta

# Função para buscar produtos por nome
def buscar_produto_por_nome(nome):
    c.execute('''SELECT * FROM produtos WHERE nome = ?''', (nome,))
    return c.fetchall()

# Interface do Streamlit
st.title('Controle de Estoque de Cesta Básica')

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

# Barra lateral para selecionar cesta
st.sidebar.header('Montar Cesta')
opcoes_cesta = ['Pequena', 'Grande']
tipo_cesta = st.sidebar.selectbox('Selecione o tipo de cesta:', opcoes_cesta)
montar = st.sidebar.button('Montar Cesta')

if montar:
    if tipo_cesta == 'Pequena':
        cesta = ['Arroz', 'Feijão', 'Óleo', 'Açúcar', 'Café moído', 'Sal', 'Extrato de tomate', 'Bolacha recheada',
                 'Macarrão Espaguete', 'Farinha de trigo', 'Farinha temperada', 'Goiabada', 'Suco em pó', 'Sardinha',
                 'Creme dental', 'Papel higiênico', 'Sabonete', 'Milharina', 'Tempero']
    else:
        cesta = ['Arroz', 'Feijão', 'Óleo', 'Açúcar', 'Café moído', 'Sal', 'Extrato de tomate', 'Vinagre',
                 'Bolacha recheada', 'Bolacha salgada', 'Macarrão Espaguete', 'Macarrão parafuso',
                 'Macarrão instantâneo', 'Farinha de trigo', 'Farinha temperada', 'Achocolatado em pó', 'Leite',
                 'Goiabada', 'Suco em pó', 'Mistura para bolo', 'Tempero', 'Sardinha', 'Creme dental',
                 'Papel higiênico', 'Sabonete']
        
    codigo_cesta = montar_cesta(cesta, tipo_cesta)
    st.sidebar.success(f'Cesta montada com sucesso! Código da Cesta: {codigo_cesta}')

# Exibir estoque com códigos
st.header('Estoque:')
produtos_estoque = buscar_produtos()
for produto in produtos_estoque:
    st.write(f'{produto[1]} - {produto[4]} x {produto[2]} - Compra: {produto[3]} - Validade: {produto[4]}')

# Exibir cestas montadas
st.sidebar.header('Cestas Montadas')
c.execute('''SELECT * FROM cestas''')
cestas_montadas = c.fetchall()
for cesta in cestas_montadas:
    st.sidebar.write(f'Cesta {cesta[1]} ({cesta[2]}) - {cesta[3]}')

# Fechar conexão com o banco de dados
conn.close()