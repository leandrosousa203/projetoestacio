import tkinter as tk
from tkinter import messagebox, simpledialog, ttk
import sqlite3
from datetime import datetime

# Função para conectar ao banco de dados SQLite
def conectar():
    return sqlite3.connect('estoque.db')

# Função para criar as tabelas no banco de dados se não existirem
def criar_tabelas():
    conn = conectar()
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS produtos (
            id INTEGER PRIMARY KEY,
            nome TEXT NOT NULL,
            quantidade INTEGER NOT NULL,
            preco REAL NOT NULL,
            data_registro DATETIME NOT NULL
        )
    ''')
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS vendas (
            id INTEGER PRIMARY KEY,
            id_produto INTEGER NOT NULL,
            quantidade INTEGER NOT NULL,
            data_venda DATE NOT NULL,
            FOREIGN KEY (id_produto) REFERENCES produtos (id)
        )
    ''')
    conn.commit()
    conn.close()

# Função para adicionar um produto ao banco de dados
def adicionar_produto(nome, quantidade, preco):
    conn = conectar()
    cursor = conn.cursor()
    agora = datetime.now()  # Obtém data e hora atuais
    cursor.execute('INSERT INTO produtos (nome, quantidade, preco, data_registro) VALUES (?, ?, ?, ?)', 
                   (nome, quantidade, preco, agora))
    conn.commit()
    conn.close()

# Função para formatar a data e hora de acordo com o formato da string
def formatar_data_hora(data_hora_str):
    formatos = [
        "%Y-%m-%d %H:%M:%S.%f",  # Formato com fração de segundos
        "%Y-%m-%d %H:%M:%S",     # Formato com hora e minuto
        "%Y-%m-%d"               # Apenas a data
    ]
    for formato in formatos:
        try:
            return datetime.strptime(data_hora_str, formato).strftime("%d/%m/%Y %H:%M:%S")
        except ValueError:
            continue
    return data_hora_str  # Retorna a string original se nenhum formato corresponder

# Função para atualizar a lista de produtos exibida na interface
def atualizar_lista_produtos():
    lista_produtos.delete(0, tk.END)
    produtos = listar_produtos()
    for produto in produtos:
        data_hora = formatar_data_hora(produto[4])
        lista_produtos.insert(tk.END, f"{produto[0]} - {produto[1]} | Quantidade: {produto[2]} | Preço: R${produto[3]:.2f} | Registrado em: {data_hora}")

# Função para adicionar um produto usando a interface gráfica
def adicionar_produto_interface():
    nome = entry_nome.get()
    quantidade = entry_quantidade.get()
    preco = entry_preco.get()

    if not nome or not quantidade or not preco:
        messagebox.showerror("Erro", "Por favor, preencha todos os campos.")
        return

    try:
        quantidade = int(quantidade)
        preco = float(preco)
    except ValueError:
        messagebox.showerror("Erro", "Quantidade e preço devem ser números.")
        return

    adicionar_produto(nome, quantidade, preco)
    messagebox.showinfo("Sucesso", "Produto adicionado com sucesso.")
    atualizar_lista_produtos()

# Função para realizar uma venda de um produto
def vender_produto(id_produto, quantidade_venda):
    conn = conectar()
    cursor = conn.cursor()

    cursor.execute('SELECT quantidade FROM produtos WHERE id = ?', (id_produto,))
    resultado = cursor.fetchone()

    if not resultado:
        conn.close()
        return False

    quantidade_atual = resultado[0]

    if quantidade_atual < quantidade_venda:
        conn.close()
        return False

    nova_quantidade = quantidade_atual - quantidade_venda
    cursor.execute('UPDATE produtos SET quantidade = ? WHERE id = ?', (nova_quantidade, id_produto))
    cursor.execute('INSERT INTO vendas (id_produto, quantidade, data_venda) VALUES (?, ?, ?)', (id_produto, quantidade_venda, datetime.now().date()))
    
    conn.commit()
    conn.close()
    return True

# Função para realizar uma venda usando a interface gráfica
def vender_produto_interface():
    id_produto = entry_id.get()
    quantidade_venda = entry_quantidade_venda.get()

    if not id_produto or not quantidade_venda:
        messagebox.showerror("Erro", "Por favor, preencha todos os campos.")
        return

    try:
        id_produto = int(id_produto)
        quantidade_venda = int(quantidade_venda)
    except ValueError:
        messagebox.showerror("Erro", "ID do produto e quantidade devem ser números.")
        return

    if quantidade_venda <= 0:
        messagebox.showerror("Erro", "A quantidade para venda deve ser maior que zero.")
        return

    if vender_produto(id_produto, quantidade_venda):
        messagebox.showinfo("Sucesso", "Venda realizada com sucesso.")
    else:
        messagebox.showerror("Erro", "Não foi possível realizar a venda. Verifique o estoque disponível.")

    atualizar_lista_produtos()

# Função para listar todos os produtos no banco de dados
def listar_produtos():
    conn = conectar()
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM produtos')
    produtos = cursor.fetchall()
    conn.close()
    return produtos

# Função para calcular itens vendidos e adicionados em um dia específico
def calcular_itens_vendidos_e_adicionados(dia, mes, ano):
    conn = conectar()
    cursor = conn.cursor()

    data_inicial = datetime(ano, mes, dia).date()
    data_final = datetime(ano, mes, dia).date()

    cursor.execute('SELECT COALESCE(SUM(quantidade), 0) FROM produtos WHERE data_registro <= ?', (data_inicial,))
    itens_adicionados = cursor.fetchone()[0]

    cursor.execute('SELECT COALESCE(SUM(quantidade), 0) FROM vendas WHERE data_venda = ?', (data_final,))
    itens_vendidos = cursor.fetchone()[0]

    conn.close()
    return itens_vendidos, itens_adicionados

# Função para gerar o relatório com base na data selecionada
def gerar_relatorio():
    dia = combo_dia.get()
    mes = combo_mes.get()
    ano = combo_ano.get()

    if not dia or not mes or not ano:
        messagebox.showerror("Erro", "Por favor, selecione o dia, mês e ano.")
        return

    try:
        dia = int(dia)
        mes = int(mes)
        ano = int(ano)
    except ValueError:
        messagebox.showerror("Erro", "Dia, mês e ano devem ser números.")
        return

    if dia < 1 or dia > 31:
        messagebox.showerror("Erro", "Dia deve estar entre 1 e 31.")
        return

    try:
        itens_vendidos, itens_adicionados = calcular_itens_vendidos_e_adicionados(dia, mes, ano)
        messagebox.showinfo("Relatório Diário", f"No dia {dia}/{mes}/{ano}:\nItens vendidos: {itens_vendidos}\nItens adicionados ao estoque: {itens_adicionados}")
    except Exception as e:
        messagebox.showerror("Erro", f"Erro ao gerar relatório: {str(e)}")

# Função para atualizar as opções de anos no combo box
def atualizar_opcoes_ano(combo_ano):
    ano_atual = datetime.now().year
    anos_futuros = range(ano_atual, ano_atual + 10)  # Ajuste o número de anos futuros conforme necessário
    combo_ano['values'] = [str(ano) for ano in anos_futuros]
    combo_ano.set(str(ano_atual))  # Define o ano atual como padrão

# Função para buscar um produto específico
def buscar_produto():
    nome_produto = entry_busca.get().strip()

    if not nome_produto:
        atualizar_lista_produtos()  # Mostra todos os produtos
        return

    conn = conectar()
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM produtos WHERE nome LIKE ?', (f'%{nome_produto}%',))
    produtos = cursor.fetchall()
    conn.close()

    lista_produtos.delete(0, tk.END)
    for produto in produtos:
        data_hora = formatar_data_hora(produto[4])
        lista_produtos.insert(tk.END, f"{produto[0]} - {produto[1]} | Quantidade: {produto[2]} | Preço: R${produto[3]:.2f} | Registrado em: {data_hora}")

# Função para limpar o filtro de busca
def limpar_filtro():
    entry_busca.delete(0, tk.END)
    atualizar_lista_produtos()

# Função de autenticação
def autenticar_usuario():
    usuario = simpledialog.askstring("Autenticação", "Nome de usuário:")
    senha = simpledialog.askstring("Autenticação", "Senha:", show='*')

    # Dados de autenticação (para fins de exemplo)
    usuario_correto = "admin"
    senha_correta = "senha123"

    if usuario == usuario_correto and senha == senha_correta:
        return True
    else:
        messagebox.showerror("Autenticação Falhou", "Nome de usuário ou senha incorretos.")
        return False

# Função para limpar todos os dados das tabelas
def limpar_dados():
    if autenticar_usuario():
        conn = conectar()
        cursor = conn.cursor()
        cursor.execute('DELETE FROM produtos')
        cursor.execute('DELETE FROM vendas')
        conn.commit()
        conn.close()
        messagebox.showinfo("Sucesso", "Dados limpos com sucesso.")
        criar_tabelas()
        atualizar_lista_produtos()

# Função para sair da aplicação
def sair_aplicacao():
    root.destroy()

# Configuração da interface gráfica
root = tk.Tk()
root.title("Controle de Estoque")

# Configurações dos widgets
frame_adicionar = tk.Frame(root)
frame_adicionar.pack(pady=10)

label_nome = tk.Label(frame_adicionar, text="Nome do Produto:")
label_nome.grid(row=0, column=0, padx=5, pady=5)
entry_nome = tk.Entry(frame_adicionar)
entry_nome.grid(row=0, column=1, padx=5, pady=5)

label_quantidade = tk.Label(frame_adicionar, text="Quantidade:")
label_quantidade.grid(row=1, column=0, padx=5, pady=5)
entry_quantidade = tk.Entry(frame_adicionar)
entry_quantidade.grid(row=1, column=1, padx=5, pady=5)

label_preco = tk.Label(frame_adicionar, text="Preço:")
label_preco.grid(row=2, column=0, padx=5, pady=5)
entry_preco = tk.Entry(frame_adicionar)
entry_preco.grid(row=2, column=1, padx=5, pady=5)

button_adicionar = tk.Button(frame_adicionar, text="Adicionar Produto", command=adicionar_produto_interface)
button_adicionar.grid(row=3, columnspan=2, pady=10)

frame_venda = tk.Frame(root)
frame_venda.pack(pady=10)

label_id = tk.Label(frame_venda, text="ID do Produto:")
label_id.grid(row=0, column=0, padx=5, pady=5)
entry_id = tk.Entry(frame_venda)
entry_id.grid(row=0, column=1, padx=5, pady=5)

label_quantidade_venda = tk.Label(frame_venda, text="Quantidade:")
label_quantidade_venda.grid(row=1, column=0, padx=5, pady=5)
entry_quantidade_venda = tk.Entry(frame_venda)
entry_quantidade_venda.grid(row=1, column=1, padx=5, pady=5)

button_vender = tk.Button(frame_venda, text="Realizar Venda", command=vender_produto_interface)
button_vender.grid(row=2, columnspan=2, pady=10)

frame_busca = tk.Frame(root)
frame_busca.pack(pady=10)

label_busca = tk.Label(frame_busca, text="Buscar Produto:")
label_busca.grid(row=0, column=0, padx=5, pady=5)
entry_busca = tk.Entry(frame_busca)
entry_busca.grid(row=0, column=1, padx=5, pady=5)

button_buscar = tk.Button(frame_busca, text="Buscar", command=buscar_produto)
button_buscar.grid(row=1, column=0, padx=5, pady=5)

button_limpar = tk.Button(frame_busca, text="Limpar Filtro", command=limpar_filtro)
button_limpar.grid(row=1, column=1, padx=5, pady=5)

frame_relatorio = tk.Frame(root)
frame_relatorio.pack(pady=10)

label_dia = tk.Label(frame_relatorio, text="Dia:")
label_dia.grid(row=0, column=0, padx=5, pady=5)
combo_dia = ttk.Combobox(frame_relatorio, values=[str(i) for i in range(1, 32)])
combo_dia.grid(row=0, column=1, padx=5, pady=5)

label_mes = tk.Label(frame_relatorio, text="Mês:")
label_mes.grid(row=1, column=0, padx=5, pady=5)
combo_mes = ttk.Combobox(frame_relatorio, values=[str(i) for i in range(1, 13)])
combo_mes.grid(row=1, column=1, padx=5, pady=5)

label_ano = tk.Label(frame_relatorio, text="Ano:")
label_ano.grid(row=2, column=0, padx=5, pady=5)
combo_ano = ttk.Combobox(frame_relatorio)
combo_ano.grid(row=2, column=1, padx=5, pady=5)

button_gerar_relatorio = tk.Button(frame_relatorio, text="Gerar Relatório", command=gerar_relatorio)
button_gerar_relatorio.grid(row=3, columnspan=2, pady=10)

button_limpar_dados = tk.Button(frame_relatorio, text="Limpar Dados", command=limpar_dados)
button_limpar_dados.grid(row=4, columnspan=2, pady=10)

button_sair = tk.Button(root, text="Sair", command=sair_aplicacao)
button_sair.pack(pady=10)

frame_lista = tk.Frame(root)
frame_lista.pack(pady=10)

lista_produtos = tk.Listbox(frame_lista, width=80)
lista_produtos.pack()

atualizar_lista_produtos()  # Atualiza a lista de produtos na inicialização
atualizar_opcoes_ano(combo_ano)

criar_tabelas()

root.mainloop()
