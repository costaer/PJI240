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
                quantidade INTEGER
            )''')

# Tabela para histórico de cestas
c.execute('''CREATE TABLE IF NOT EXISTS cestas_montadas (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                data DATE,
                tipo TEXT,
                itens TEXT
            )''')

# Lista de produtos disponíveis
opcoes_produtos = ['Arroz', 'Feijão', 'Óleo', 'Açúcar', 'Café moído', 'Sal', 'Extrato de tomate',
                   'Vinagre', 'Bolacha recheada', 'Bolacha salgada', 'Macarrão Espaguete',
                   'Macarrão parafuso', 'Macarrão instantâneo', 'Farinha de trigo', 'Farinha temperada',
                   'Achocolatado em pó', 'Leite', 'Goiabada', 'Suco em pó', 'Mistura para bolo', 'Tempero',
                   'Sardinha', 'Creme dental', 'Papel higiênico', 'Sabonete', 'Milharina']

opcoes_produtos.sort()

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

# Função para buscar todos os produtos
def buscar_produtos():
    c.execute('''SELECT * FROM produtos ORDER BY nome''')
    return c.fetchall()

# Função para exportar cesta para arquivo
def exportar_cesta_para_txt(itens_cesta):
    with open('cesta_montada.txt', 'w') as file:
        for item in itens_cesta:
            file.write(f"{item[0]} x {item[2]} - Compra: {item[1]} - Validade: {item[3]}\n")
    st.sidebar.success("Arquivo 'cesta_montada.txt' exportado com sucesso!")

# Função para exportar estoque para arquivo
def exportar_estoque_para_txt(produtos_estoque):
    with open('estoque.txt', 'w') as file:
        for produto in produtos_estoque:
            file.write(f"{produto[4]} x {produto[1]} - Compra: {produto[2]} - Validade: {produto[3]}\n")
    st.sidebar.success("Arquivo 'estoque.txt' exportado com sucesso!")

# Interface do Streamlit
st.title('Controle de Estoque de Cesta Básica')

# Cadastro de produtos na barra lateral
st.sidebar.header('Cadastrar Produto')
nome_produto = st.sidebar.selectbox('Nome do Produto', opcoes_produtos)
data_compra = st.sidebar.date_input('Data da Compra')
data_validade = st.sidebar.date_input('Data de Validade')
quantidade = st.sidebar.number_input('Quantidade', min_value=1, value=1)
adicionar = st.sidebar.button('Adicionar Produto')

if adicionar:
    adicionar_produto(nome_produto, data_compra, data_validade, quantidade)
    st.sidebar.success('Produto adicionado com sucesso!')

# Mostrar estoque com alerta de validade
st.header('Estoque Atual')
produtos_estoque = buscar_produtos()
hoje = datetime.today()

produtos_proximos_validade = [p for p in produtos_estoque if datetime.strptime(p[3], "%Y-%m-%d") <= hoje + timedelta(days=7)]
produtos_restantes = [p for p in produtos_estoque if p not in produtos_proximos_validade]

st.subheader('Produtos Próximos da Validade (menos de 7 dias)')
for produto in produtos_proximos_validade:
    st.markdown(f"<span style='color:red'>{produto[4]} x {produto[1]} - Compra: {produto[2]} - Validade: {produto[3]}</span>", unsafe_allow_html=True)

st.subheader('Outros Produtos em Estoque')
for produto in produtos_restantes:
    st.write(f"{produto[4]} x {produto[1]} - Compra: {produto[2]} - Validade: {produto[3]}")

# Montar cestas e salvar no histórico
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

    itens_cesta = []
    for item in cesta:
        produtos = buscar_produto_por_nome(item)
        if produtos:
            produto = selecionar_proximos_validade(produtos, 1)[0]
            nova_quantidade = produto[4] - 1
            atualizar_quantidade_produto(produto[0], nova_quantidade)
            itens_cesta.append((1, *produto[1:]))
    
    # Exportar cesta e salvar no histórico
    exportar_cesta_para_txt(itens_cesta)
    st.sidebar.success("Cesta montada e exportada com sucesso!")

# Histórico de cestas montadas
st.sidebar.header("Histórico de Cestas Montadas")
c.execute("SELECT * FROM cestas_montadas ORDER BY data DESC")
historico_cestas = c.fetchall()

for cesta in historico_cestas:
    with st.sidebar.expander(f"Cesta {cesta[2]} - {cesta[1]}"):
        st.sidebar.write(cesta[3])

st.sidebar.button("Exportar Estoque", on_click=lambda: exportar_estoque_para_txt(produtos_estoque))

# Fechar conexão com o banco de dados
conn.close()