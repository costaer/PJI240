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
                codigo TEXT
            )''')
c.execute('''CREATE TABLE IF NOT EXISTS cestas (
                id INTEGER PRIMARY KEY,
                data DATE,
                itens TEXT,
                codigo TEXT
            )''')

# Função para adicionar produto ao estoque
def adicionar_produto(nome, data_compra, data_validade, quantidade):
    codigo_produto = f"{nome[:3].upper()}_{datetime.now().strftime('%Y%m%d%H%M%S')}"
    c.execute('''SELECT * FROM produtos WHERE nome = ? AND data_compra = ? AND data_validade = ?''',
              (nome, data_compra, data_validade))
    produto_existente = c.fetchone()
    if produto_existente:
        nova_quantidade = produto_existente[4] + quantidade
        c.execute('''UPDATE produtos SET quantidade = ? WHERE id = ?''', (nova_quantidade, produto_existente[0]))
    else:
        c.execute('''INSERT INTO produtos (nome, data_compra, data_validade, quantidade, codigo)
                      VALUES (?, ?, ?, ?, ?)''', (nome, data_compra, data_validade, quantidade, codigo_produto))
    conn.commit()

# Função para buscar produtos com alerta de validade
def buscar_produtos_alerta():
    hoje = datetime.now().date()
    prazo = hoje + timedelta(days=7)
    c.execute('''SELECT * FROM produtos WHERE data_validade <= ? ORDER BY data_validade''', (prazo,))
    return c.fetchall()

# Função para exibir estoque com alerta de validade
def exibir_estoque():
    st.header('Estoque Atual:')
    # Buscar produtos com alerta
    produtos_alerta = buscar_produtos_alerta()
    if produtos_alerta:
        st.subheader('Produtos Perto da Validade (<= 7 dias)')
        for produto in produtos_alerta:
            st.markdown(f"<span style='color:red'>{produto[4]} x {produto[1]} - Validade: {produto[3]}</span>", unsafe_allow_html=True)
    # Buscar todos os produtos restantes
    c.execute('''SELECT * FROM produtos ORDER BY nome''')
    produtos_restantes = c.fetchall()
    
    st.subheader('Outros Produtos:')
    for produto in produtos_restantes:
        if produto not in produtos_alerta:
            st.write(f'{produto[4]} x {produto[1]} - Compra: {produto[2]} - Validade: {produto[3]}')

# Função para exportar estoque em arquivo de texto
def exportar_estoque():
    c.execute("SELECT * FROM produtos ORDER BY nome")
    produtos = c.fetchall()
    with open('estoque.txt', 'w') as file:
        file.write("Estoque Atual:\n")
        for produto in produtos:
            data_validade = datetime.strptime(produto[3], "%Y-%m-%d").date()
            if data_validade <= (datetime.now().date() + timedelta(days=7)):
                file.write(f"[ALERTA] {produto[4]} x {produto[1]} - Validade: {produto[3]}\n")
            else:
                file.write(f"{produto[4]} x {produto[1]} - Compra: {produto[2]} - Validade: {produto[3]}\n")

# Função para montar a cesta e salvar no histórico
def montar_cesta(cesta):
    codigo_cesta = datetime.now().strftime('%Y%m%d%H%M%S')
    itens_cesta = []
    itens_faltantes = []
    for item in cesta:
        produtos = buscar_produto_por_nome(item)
        if not produtos:
            itens_faltantes.append(item)
        else:
            produto = selecionar_proximos_validade(produtos, 1)[0]
            nova_quantidade = produto[4] - 1
            atualizar_quantidade_produto(produto[0], nova_quantidade)
            itens_cesta.append((1, *produto[1:]))  # Quantidade fixa em 1
    if not itens_faltantes:
        c.execute("INSERT INTO cestas (data, itens, codigo) VALUES (?, ?, ?)", 
                  (datetime.now().date(), ', '.join(cesta), codigo_cesta))
        conn.commit()
        exportar_cesta(itens_cesta, codigo_cesta)
    return itens_cesta, itens_faltantes, codigo_cesta

# Função para buscar produtos por nome
def buscar_produto_por_nome(nome):
    c.execute('''SELECT * FROM produtos WHERE nome = ?''', (nome,))
    return c.fetchall()

# Função para selecionar produtos mais próximos da validade
def selecionar_proximos_validade(produtos, quantidade):
    produtos_ordenados = sorted(produtos, key=lambda x: x[3])
    return produtos_ordenados[:quantidade]

# Função para atualizar quantidade de produto no estoque
def atualizar_quantidade_produto(produto_id, nova_quantidade):
    c.execute('''UPDATE produtos SET quantidade = ? WHERE id = ?''', (nova_quantidade, produto_id))
    if nova_quantidade <= 0:
        c.execute('''DELETE FROM produtos WHERE id = ?''', (produto_id,))
    conn.commit()

# Interface do Streamlit
st.title('Controle de Estoque de Cesta Básica')

# Exibir estoque sempre visível na tela
exibir_estoque()

# Menu lateral para cadastrar produtos
st.sidebar.header('Cadastrar Produto')
nome_produto = st.sidebar.selectbox('Nome do Produto', opcoes_produtos)
data_compra = st.sidebar.date_input('Data da Compra')
data_validade = st.sidebar.date_input('Data de Validade')
quantidade = st.sidebar.number_input('Quantidade', min_value=1, value=1)
adicionar = st.sidebar.button('Adicionar Produto')

if adicionar:
    adicionar_produto(nome_produto, data_compra, data_validade, quantidade)
    st.sidebar.success('Produto adicionado com sucesso!')

# Botão para exportar estoque
exportar_estoque_btn = st.sidebar.button("Exportar Estoque Completo")
if exportar_estoque_btn:
    exportar_estoque()
    st.sidebar.success("Estoque exportado com sucesso!")

# Exibir cestas montadas
st.sidebar.header("Histórico de Cestas")
c.execute("SELECT * FROM cestas ORDER BY data DESC")
historico_cestas = c.fetchall()
for cesta in historico_cestas:
    with st.sidebar.expander(f"Cesta {cesta[2]} - {cesta[1]}"):
        st.write(cesta[2])

# Montagem de cesta
st.sidebar.header('Montar Cesta')
opcoes_cesta = ['Pequena', 'Grande']
tipo_cesta = st.sidebar.selectbox('Selecione o tipo de cesta:', opcoes_cesta)
montar = st.sidebar.button('Montar Cesta')

if montar:
    # Definir itens da cesta
    cesta = ['Arroz', 'Feijão', 'Óleo', 'Açúcar']  # Exemplo de produtos para a cesta
    itens_cesta, itens_faltantes, codigo_cesta = montar_cesta(cesta)
    if itens_faltantes:
        st.sidebar.error(f'Itens faltando no estoque: {", ".join(itens_faltantes)}')
    else:
        st.subheader('Itens da Cesta:')
        for item in itens_cesta:
            st.write(f'{item[0]} x {item[1]} - Compra: {item[2]} - Validade: {item[3]}')
