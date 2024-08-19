import tkinter as tk
from tkinter import messagebox, ttk
import sqlite3
from datetime import datetime

# Funções para interagir com o banco de dados SQLite

def conectar():
    return sqlite3.connect('estoque.db')

def criar_tabela():
    conn = conectar()
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS produtos (
            id INTEGER PRIMARY KEY,
            nome TEXT NOT NULL,
            quantidade INTEGER NOT NULL,
            preco REAL NOT NULL,
            data_registro DATE NOT NULL
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

def adicionar_produto(nome, quantidade, preco):
    conn = conectar()
    cursor = conn.cursor()
    cursor.execute('INSERT INTO produtos (nome, quantidade, preco, data_registro) VALUES (?, ?, ?, ?)', (nome, quantidade, preco, datetime.now().date()))
    conn.commit()
    conn.close()

def vender_produto(id_produto, quantidade_venda):
    conn = conectar()
    cursor = conn.cursor()

    # Verificar se há quantidade suficiente em estoque
    cursor.execute('SELECT quantidade FROM produtos WHERE id = ?', (id_produto,))
    resultado = cursor.fetchone()

    if resultado:
        quantidade_atual = resultado[0]
        if quantidade_atual >= quantidade_venda:
            nova_quantidade = quantidade_atual - quantidade_venda
            cursor.execute('UPDATE produtos SET quantidade = ? WHERE id = ?', (nova_quantidade, id_produto))
            
            # Registrar a venda na tabela de vendas
            cursor.execute('INSERT INTO vendas (id_produto, quantidade, data_venda) VALUES (?, ?, ?)', (id_produto, quantidade_venda, datetime.now().date()))
            
            conn.commit()
            conn.close()
            return True
        else:
            conn.close()
            return False
    else:
        conn.close()
        return False

def listar_produtos():
    conn = conectar()
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM produtos')
    produtos = cursor.fetchall()
    conn.close()
    return produtos

def calcular_itens_vendidos_e_adicionados(dia, mes, ano):
    conn = conectar()
    cursor = conn.cursor()

    data_inicial = datetime(ano, mes, dia).date()
    data_final = datetime(ano, mes, dia).date()

    cursor.execute('SELECT COALESCE(SUM(quantidade), 0) FROM produtos WHERE data_registro = ?', (data_inicial,))
    itens_adicionados = cursor.fetchone()[0]

    cursor.execute('SELECT COALESCE(SUM(quantidade), 0) FROM vendas WHERE data_venda = ?', (data_final,))
    itens_vendidos = cursor.fetchone()[0]

    conn.close()
    return itens_vendidos, itens_adicionados

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

# Configuração da interface gráfica
root = tk.Tk()
root.title("Controle de Estoque")

# Frame para adicionar produtos
frame_adicionar = tk.Frame(root, padx=10, pady=10)
frame_adicionar.pack()

label_nome = tk.Label(frame_adicionar, text="Nome do Produto:")
label_nome.grid(row=0, column=0, padx=5, pady=5)
entry_nome = tk.Entry(frame_adicionar, width=30)
entry_nome.grid(row=0, column=1, padx=5, pady=5)

label_quantidade = tk.Label(frame_adicionar, text="Quantidade:")
label_quantidade.grid(row=1, column=0, padx=5, pady=5)
entry_quantidade = tk.Entry(frame_adicionar, width=10)
entry_quantidade.grid(row=1, column=1, padx=5, pady=5)

label_preco = tk.Label(frame_adicionar, text="Preço:")
label_preco.grid(row=2, column=0, padx=5, pady=5)
entry_preco = tk.Entry(frame_adicionar, width=10)
entry_preco.grid(row=2, column=1, padx=5, pady=5)

btn_adicionar = tk.Button(frame_adicionar, text="Adicionar Produto", command=adicionar_produto)
btn_adicionar.grid(row=3, columnspan=2, padx=5, pady=10)

# Frame para relatórios
frame_relatorio = tk.Frame(root, padx=10, pady=10)
frame_relatorio.pack()

label_dia = tk.Label(frame_relatorio, text="Dia:")
label_dia.grid(row=0, column=0, padx=5, pady=5)
combo_dia = ttk.Combobox(frame_relatorio, values=[str(i) for i in range(1, 32)], width=5)
combo_dia.grid(row=0, column=1, padx=5, pady=5)

label_mes = tk.Label(frame_relatorio, text="Mês:")
label_mes.grid(row=0, column=2, padx=5, pady=5)
combo_mes = ttk.Combobox(frame_relatorio, values=[str(i) for i in range(1, 13)], width=5)
combo_mes.grid(row=0, column=3, padx=5, pady=5)

label_ano = tk.Label(frame_relatorio, text="Ano:")
label_ano.grid(row=0, column=4, padx=5, pady=5)
combo_ano = ttk.Combobox(frame_relatorio, values=[str(i) for i in range(2000, 2051)], width=8)
combo_ano.grid(row=0, column=5, padx=5, pady=5)

btn_gerar_relatorio = tk.Button(frame_relatorio, text="Gerar Relatório", command=gerar_relatorio)
btn_gerar_relatorio.grid(row=0, column=6, padx=5, pady=5)

# Criar tabela se não existir
criar_tabela()

# Iniciar a aplicação
root.mainloop()
