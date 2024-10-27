import streamlit as st
import sqlite3
from datetime import datetime, timedelta

# Criar conexão com o banco de dados
conn = sqlite3.connect('estoque.db')
c = conn.cursor()

# Criar tabela se não existir
c.execute('''CREATE TABLE IF NOT EXISTS produtos (
                id INTEGER PRIMARY KEY,
                nome TEXT,
                data_compra DATE,
                data_validade DATE,
                quantidade INTEGER,
                codigo_controle TEXT
            )''')

# Criar tabela para histórico de cestas
c.execute('''CREATE TABLE IF NOT EXISTS historico_cestas (
                id INTEGER PRIMARY KEY,
                tipo_cesta TEXT,
                data DATE,
                itens TEXT
            )''')

# Lista de produtos disponíveis
opcoes_produtos = ['Arroz', 'Feijão', 'Óleo', 'Açúcar', 'Café moído', 'Sal', 'Extrato de tomate',
                   'Vinagre', 'Bolacha recheada', 'Bolacha salgada', 'Macarrão Espaguete',
                   'Macarrão parafuso', 'Macarrão instantâneo', 'Farinha de trigo', 'Farinha temperada',
                   'Achocolatado em pó', 'Leite', 'Goiabada', 'Suco em pó', 'Mistura para bolo', 'Tempero',
                   'Sardinha', 'Creme dental', 'Papel higiênico', 'Sabonete', 'Milharina']

opcoes_produtos.sort()  # Ordenar os produtos em ordem alfabética

# Função para adicionar produto ao estoque ou atualizar quantidade
def adicionar_produto(nome, data_compra, data_validade, quantidade, codigo_controle):
    # Verificar se o produto já existe
    c.execute('''SELECT * FROM produtos WHERE nome = ? AND data_compra = ? AND data_validade = ?''',
              (nome, data_compra, data_validade))
    produto_existente = c.fetchone()
    if produto_existente:
        nova_quantidade = produto_existente[4] + quantidade
        c.execute('''UPDATE produtos SET quantidade = ?, codigo_controle = ? WHERE id = ?''',
                  (nova_quantidade, codigo_controle, produto_existente[0]))
    else:
        c.execute('''INSERT INTO produtos (nome, data_compra, data_validade, quantidade, codigo_controle)
                      VALUES (?, ?, ?, ?, ?)''', (nome, data_compra, data_validade, quantidade, codigo_controle))
    conn.commit()

# Função para buscar todos os produtos ordenados por validade
def buscar_produtos():
    c.execute('''SELECT * FROM produtos ORDER BY CASE WHEN data_validade <= ? THEN 0 ELSE 1 END, data_validade''',
              (datetime.now() + timedelta(days=10),))
    return c.fetchall()

# Função para atualizar quantidade de produto no estoque
def atualizar_quantidade_produto(produto_id, nova_quantidade):
    c.execute('''UPDATE produtos SET quantidade = ? WHERE id = ?''', (nova_quantidade, produto_id))
    if nova_quantidade <= 0:
        c.execute('''DELETE FROM produtos WHERE id = ?''', (produto_id,))
    conn.commit()

# Função para montar a cesta e encontrar itens faltantes
def montar_cesta(cesta):
    itens_cesta = []
    itens_faltantes = []
    for item in cesta:
        produtos = buscar_produto_por_nome(item)
        if not produtos:
            itens_faltantes.append(item)
        else:
            produto = produtos[0]
            itens_cesta.append((1, *produto[1:]))  # Fixar a quantidade em 1
    return itens_cesta, itens_faltantes

# Função para buscar produtos por nome
def buscar_produto_por_nome(nome):
    c.execute('''SELECT * FROM produtos WHERE nome = ?''', (nome,))
    return c.fetchall()

# Função para calcular a diferença de dias entre duas datas
def diferenca_dias(data1, data2):
    data1 = datetime.strptime(data1, "%Y-%m-%d")
    data2 = datetime.strptime(data2, "%Y-%m-%d")
    return abs((data2 - data1).days)

# Função para selecionar produtos mais próximos da validade
def selecionar_proximos_validade(produtos, quantidade):
    produtos_ordenados = sorted(produtos, key=lambda x: x[3])
    return produtos_ordenados[:quantidade]

# Função para salvar o histórico de cestas
def salvar_historico_cesta(tipo_cesta, itens):
    c.execute('''INSERT INTO historico_cestas (tipo_cesta, data, itens) VALUES (?, ?, ?)''',
              (tipo_cesta, datetime.now().date(), ', '.join(itens)))
    conn.commit()

# Interface do Streamlit
st.title('Controle de Estoque de Cesta Básica')

# Barra lateral para cadastrar produtos
st.sidebar.header('Cadastrar Produto')
nome_produto = st.sidebar.selectbox('Nome do Produto', opcoes_produtos)
data_compra = st.sidebar.date_input('Data da Compra')
data_validade = st.sidebar.date_input('Data de Validade')
quantidade = st.sidebar.number_input('Quantidade', min_value=1, value=1)
codigo_controle = st.sidebar.text_input('Código de Controle', value='', max_chars=10)
adicionar = st.sidebar.button('Adicionar Produto')

if adicionar:
    adicionar_produto(nome_produto, data_compra, data_validade, quantidade, codigo_controle)
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
        
    # Verificar se todos os itens da cesta estão disponíveis no estoque
    todos_disponiveis = True
    itens_faltantes = []
    for item in cesta:
        produtos = buscar_produto_por_nome(item)
        if not produtos:
            todos_disponiveis = False
            itens_faltantes.append(item)
    
    if not todos_disponiveis:
        st.sidebar.error('Os seguintes itens estão faltando no estoque para completar a cesta: {}'.format(', '.join(itens_faltantes)))
    else:
        # Montar a cesta com os itens disponíveis mais próximos da validade
        itens_cesta = []
        for item in cesta:
            produtos = buscar_produto_por_nome(item)
            produto_mais_proximo = selecionar_proximos_validade(produtos, 1)[0]
            nova_quantidade = produto_mais_proximo[4] - 1
            atualizar_quantidade_produto(produto_mais_proximo[0], nova_quantidade)
            itens_cesta.append((1, *produto_mais_proximo[1:]))  # Fixar a quantidade em 1
        
        # Exibir os itens da cesta
        st.subheader('Itens da Cesta:')
        for item in itens_cesta:
            st.write(f'{item[0]} x {item[2]} - Compra: {item[1]} - Validade: {item[3]}')
        
        # Salvar histórico de cestas montadas
        salvar_historico_cesta(tipo_cesta, [item[2] for item in itens_cesta])

# Exibir estoque
st.header('Estoque:')
produtos_estoque = buscar_produtos()
for produto in produtos_estoque:
    st.write(f'{produto[4]} x {produto[2]} - Compra: {produto[1]}  - Validade: {produto[3]} (Código: {produto[5]})')

# Exibir histórico de cestas
st.header('Histórico de Cestas Montadas:')
c.execute('SELECT * FROM historico_cestas ORDER BY data DESC')
historico_cestas = c.fetchall()

if historico_cestas:
    for registro in historico_cestas:
        st.write(f'Tipo: {registro[1]} - Data: {registro[2]} - Itens: {registro[3]}')
else:
    st.write('Nenhuma cesta montada ainda.')

# Exportar histórico para .txt
exportar = st.button('Exportar Histórico de Cestas para .txt')
if exportar:
    with open('historico_cestas.txt', 'w') as f:
        for registro in historico_cestas:
            f.write(f'Tipo: {registro[1]} - Data: {registro[2]} - Itens: {registro[3]}\n')
    st.success('Histórico exportado com sucesso!')

# Fechar conexão com o banco de dados
conn.close()