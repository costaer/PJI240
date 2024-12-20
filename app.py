import streamlit as st
import sqlite3
from datetime import datetime, timedelta
import uuid

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
# Função feita para o projeto integrador 2
c.execute('''CREATE TABLE IF NOT EXISTS historico_cestas (
                id INTEGER PRIMARY KEY,
                tipo_cesta TEXT,
                data DATE,
                codigo_cesta TEXT,
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
def adicionar_produto(nome, data_compra, data_validade, quantidade):
    codigo_controle = str(uuid.uuid4())[:8]  # Gerar código de controle único
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

# Função para buscar todos os produtos
def buscar_produtos():
    c.execute('''SELECT * FROM produtos''')
    return c.fetchall()

# Função para buscar produtos por nome
def buscar_produto_por_nome(nome):
    c.execute('''SELECT * FROM produtos WHERE nome = ?''', (nome,))
    return c.fetchall()

# Função para atualizar quantidade de produto no estoque
def atualizar_quantidade_produto(produto_id, nova_quantidade):
    c.execute('''UPDATE produtos SET quantidade = ? WHERE id = ?''', (nova_quantidade, produto_id))
    if nova_quantidade <= 0:
        c.execute('''DELETE FROM produtos WHERE id = ?''', (produto_id,))
    conn.commit()

# Função para salvar o histórico de cestas
# Função feita para o projeto integrador 2
def salvar_historico_cesta(tipo_cesta, codigo_cesta, itens):
    c.execute('''INSERT INTO historico_cestas (tipo_cesta, data, codigo_cesta, itens) VALUES (?, ?, ?, ?)''',
              (tipo_cesta, datetime.now().date(), codigo_cesta, ', '.join(itens)))
    conn.commit()

# Função para gerar arquivo da cesta
# Função feita para o projeto integrador 2
def gerar_arquivo_cesta(codigo_cesta, tipo_cesta, itens):
    filename = f'cesta_{codigo_cesta}.txt'
    with open(filename, 'w') as f:
        f.write(f'Tipo da Cesta: {tipo_cesta}\n')
        f.write(f'Código da Cesta: {codigo_cesta}\n')
        f.write(f'Data: {datetime.now().date()}\n')
        f.write('Itens:\n')
        for item in itens:
            f.write(f'- {item}\n')
    return filename

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

codigo_cesta_gerado = None
cesta_itens = []

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
        # Montar a cesta com os itens disponíveis
        for item in cesta:
            produtos = buscar_produto_por_nome(item)
            if produtos:  # Verifica se o produto está disponível
                produto_mais_proximo = produtos[0]  # Considerar apenas o primeiro produto
                if produto_mais_proximo[4] > 0:  # Verifica se há quantidade disponível
                    nova_quantidade = produto_mais_proximo[4] - 1
                    atualizar_quantidade_produto(produto_mais_proximo[0], nova_quantidade)
                    itens_cesta.append(f'1 x {produto_mais_proximo[5]} - Código: {produto_mais_proximo[4]} - Compra: {produto_mais_proximo[1]} - Validade: {produto_mais_proximo[3]}')  # Adicionar descrição do item

        # Exibir os itens da cesta
        st.subheader('Itens da Cesta:')
        for item in itens_cesta:
            st.write(item)

        # Gerar um código de cesta único
        # Função feita para o projeto integrador 2
        codigo_cesta_gerado = str(uuid.uuid4())[:8]

        # Salvar histórico de cestas montadas e obter o código da cesta
        # Função feita para o projeto integrador 2
        salvar_historico_cesta(tipo_cesta, codigo_cesta_gerado, itens_cesta)

        # Gerar arquivo da cesta e disponibilizar para download
        # Função feita para o projeto integrador 2
        arquivo_cesta = gerar_arquivo_cesta(codigo_cesta_gerado, tipo_cesta, itens_cesta)
        with open(arquivo_cesta, 'rb') as f:
            st.download_button(label='Baixar Cesta', data=f, file_name=arquivo_cesta, mime='text/plain')

# Exibir estoque
st.header('Estoque:')
produtos_estoque = buscar_produtos()
produtos_proximos_validade = sorted(
    [produto for produto in produtos_estoque if datetime.strptime(produto[3], "%Y-%m-%d") <= datetime.now() + timedelta(days=7)],
    key=lambda x: x[3]  # Ordenar por data de validade - Função feita para o projeto integrador 2
)

# Exibir produtos que estão prestes a vencer primeiro
# Função feita para o projeto integrador 2
for produto in produtos_proximos_validade:
    st.warning(f'{produto[4]} x {produto[2]} - Compra: {produto[1]} - Validade: {produto[3]} (Código: {produto[5]})')

# Exibir o restante dos produtos em ordem alfabética
produtos_restantes = sorted([produto for produto in produtos_estoque if produto not in produtos_proximos_validade], key=lambda x: x[2])
for produto in produtos_restantes:
    st.write(f'{produto[4]} x {produto[2]} - Compra: {produto[1]} - Validade: {produto[3]} (Código: {produto[5]})')

# Exibir histórico de cestas
# Função feita para o projeto integrador 2
st.header('Histórico de Cestas Montadas:')
c.execute('SELECT * FROM historico_cestas ORDER BY data DESC')
historico_cestas = c.fetchall()

if historico_cestas:
    for registro in historico_cestas:
        col1, col2, col3 = st.columns([3, 1, 1])
        with col1:
            st.write(f'Tipo: {registro[1]} - Código: {registro[3]} - Data: {registro[2]}')
            if st.button('Ver Itens', key=registro[3]):
                st.write(f'Itens: {registro[4]}')
                arquivo_historico = f'historico_cesta_{registro[3]}.txt'
                with open(arquivo_historico, 'w') as f:
                    f.write(f'Tipo da Cesta: {registro[1]}\n')
                    f.write(f'Código da Cesta: {registro[3]}\n')
                    f.write(f'Data: {registro[2]}\n')
                    f.write('Itens:\n')
                    for item in registro[4].split(', '):
                        f.write(f'- {item}\n')
                with open(arquivo_historico, 'rb') as f:
                    st.download_button(label='Baixar Lista de Produtos', data=f, file_name=arquivo_historico, mime='text/plain')

# Fechar conexão com o banco de dados
conn.close()