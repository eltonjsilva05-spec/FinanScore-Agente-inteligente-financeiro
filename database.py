import sqlite3
import hashlib
from datetime import datetime

def conectar_bd():
    """Cria a conexão com o banco de dados SQLite."""
    return sqlite3.connect("finanscore.db")

def inicializar_banco():
    """Cria as tabelas necessárias no banco de dados se não existirem."""
    conn = conectar_bd()
    cursor = conn.cursor()
   
    # Tabela de Usuários
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS usuarios (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            senha TEXT NOT NULL,
            nome_completo TEXT NOT NULL,
            email TEXT,
            telefone TEXT,
            plano TEXT DEFAULT 'Gratuito'
        )
    """)
    
    # Tabela de Transações (Fluxo de Caixa)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS transacoes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT NOT NULL,
            data TEXT NOT NULL,
            descricao TEXT NOT NULL,
            categoria TEXT NOT NULL,
            tipo TEXT NOT NULL,
            valor REAL NOT NULL,
            conta_id INTEGER DEFAULT 0,
            FOREIGN KEY(username) REFERENCES usuarios(username)
        )
    """)
    
    # Tabela de Contas Bancárias (B2B / Clientes)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS contas (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT NOT NULL,
            banco TEXT NOT NULL,
            agencia TEXT NOT NULL,
            conta TEXT NOT NULL,
            tipo_conta TEXT NOT NULL,
            saldo_inicial REAL DEFAULT 0.0,
            FOREIGN KEY(username) REFERENCES usuarios(username)
        )
    """)
    
    # Tabela de Histórico da Reserva Técnica
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS reserva (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT NOT NULL,
            tipo TEXT NOT NULL, -- 'Aporte' ou 'Resgate'
            valor REAL NOT NULL,
            data TEXT NOT NULL,
            FOREIGN KEY(username) REFERENCES usuarios(username)
        )
    """)
    
    # Criar um administrador padrão se não houver nenhum
    cursor.execute("SELECT * FROM usuarios WHERE username = 'admin'")
    if not cursor.fetchone():
        senha_hash = hashlib.sha256("admin123".encode()).hexdigest()
        cursor.execute("""
            INSERT INTO usuarios (username, senha, nome_completo, email, telefone, plano)
            VALUES ('admin', ?, 'Administrador Global', 'admin@finanscore.com', '413384-1560', 'Admin')
        """, (senha_hash,))
        
    conn.commit()
    conn.close()

# ==========================================
# FUNÇÕES DE AUTENTICAÇÃO
# ==========================================

def verificar_login(username, senha):
    """Verifica se o usuário e a senha coincidem."""
    conn = conectar_bd()
    cursor = conn.cursor()
    senha_hash = hashlib.sha256(senha.encode()).hexdigest()
    cursor.execute("SELECT * FROM usuarios WHERE username = ? AND senha = ?", (username, senha_hash))
    usuario = cursor.fetchone()
    conn.close()
    return usuario is not None

def criar_usuario(username, senha, nome, email, telefone):
    """Registra um novo usuário no sistema."""
    conn = conectar_bd()
    cursor = conn.cursor()
    senha_hash = hashlib.sha256(senha.encode()).hexdigest()
    try:
        cursor.execute("""
            INSERT INTO usuarios (username, senha, nome_completo, email, telefone)
            VALUES (?, ?, ?, ?, ?)
        """, (username, senha_hash, nome, email, telefone))
        conn.commit()
        sucesso = True
    except sqlite3.IntegrityError:
        sucesso = False
    conn.close()
    return sucesso

# ==========================================
# FUNÇÕES DE TRANSAÇÕES (DASHBOARD & FLUXO)
# ==========================================

def inserir_transacao(username, data, descricao, categoria, tipo, valor, conta_id=0):
    conn = conectar_bd()
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO transacoes (username, data, descricao, categoria, tipo, valor, conta_id)
        VALUES (?, ?, ?, ?, ?, ?, ?)
    """, (username, data, descricao, categoria, tipo, valor, conta_id))
    conn.commit()
    conn.close()

def listar_transacoes_usuario(username):
    conn = conectar_bd()
    cursor = conn.cursor()
    cursor.execute("SELECT id, data, descricao, categoria, tipo, valor, conta_id FROM transacoes WHERE username = ? ORDER BY data DESC, id DESC", (username,))
    dados = cursor.fetchall()
    conn.close()
    return dados

def excluir_transacao(id_transacao):
    conn = conectar_bd()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM transacoes WHERE id = ?", (id_transacao,))
    conn.commit()
    conn.close()

def atualizar_transacao(id_transacao, data, descricao, categoria, tipo, valor, conta_id):
    conn = conectar_bd()
    cursor = conn.cursor()
    cursor.execute("""
        UPDATE transacoes 
        SET data = ?, descricao = ?, categoria = ?, tipo = ?, valor = ?, conta_id = ? 
        WHERE id = ?
    """, (data, descricao, categoria, tipo, valor, conta_id, id_transacao))
    conn.commit()
    conn.close()

def soma_receitas_usuario(username):
    conn = conectar_bd()
    cursor = conn.cursor()
    cursor.execute("SELECT SUM(valor) FROM transacoes WHERE username = ? AND tipo = 'Receita'", (username,))
    res = cursor.fetchone()[0]
    conn.close()
    return res if res else 0.0

def soma_despesas_usuario(username):
    conn = conectar_bd()
    cursor = conn.cursor()
    cursor.execute("SELECT SUM(valor) FROM transacoes WHERE username = ? AND tipo = 'Despesa'", (username,))
    res = cursor.fetchone()[0]
    conn.close()
    return res if res else 0.0

def dados_grafico_categorias(username):
    conn = conectar_bd()
    cursor = conn.cursor()
    cursor.execute("SELECT categoria, SUM(valor) FROM transacoes WHERE username = ? AND tipo = 'Despesa' GROUP BY categoria", (username,))
    dados = cursor.fetchall()
    conn.close()
    return dados

# ==========================================
# FUNÇÕES DE CONTAS BANCÁRIAS
# ==========================================

def inserir_conta_bancaria(username, banco, agencia, conta, tipo_conta, saldo_inicial):
    conn = conectar_bd()
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO contas (username, banco, agencia, conta, tipo_conta, saldo_inicial)
        VALUES (?, ?, ?, ?, ?, ?)
    """, (username, banco, agencia, conta, tipo_conta, saldo_inicial))
    conn.commit()
    conn.close()

def listar_contas_usuario(username):
    conn = conectar_bd()
    cursor = conn.cursor()
    cursor.execute("SELECT id, banco, agencia, conta, tipo_conta, saldo_inicial FROM contas WHERE username = ?", (username,))
    dados = cursor.fetchall()
    conn.close()
    return dados

def excluir_conta_bancaria(id_conta):
    conn = conectar_bd()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM contas WHERE id = ?", (id_conta,))
    cursor.execute("UPDATE transacoes SET conta_id = 0 WHERE conta_id = ?", (id_conta,))
    conn.commit()
    conn.close()

def verificar_saldo_transacoes_conta(conta_id):
    conn = conectar_bd()
    cursor = conn.cursor()
    cursor.execute("SELECT tipo, valor FROM transacoes WHERE conta_id = ?", (conta_id,))
    transacoes = cursor.fetchall()
    conn.close()
    
    saldo = 0.0
    for tipo, valor in transacoes:
        if tipo == "Receita":
            saldo += valor
        else:
            saldo -= valor
    return saldo

def obter_saldo_atual_conta(conta_id, saldo_inicial):
    saldo_movimentacoes = verificar_saldo_transacoes_conta(conta_id)
    return saldo_inicial + saldo_movimentacoes

# ==========================================
# FUNÇÕES DA RESERVA TÉCNICA
# ==========================================

def atualizar_valor_inicial_reserva(username, valor):
    conn = conectar_bd()
    cursor = conn.cursor()
    data_atual = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    cursor.execute("""
        INSERT INTO reserva (username, tipo, valor, data)
        VALUES (?, 'Aporte', ?, ?)
    """, (username, valor, data_atual))
    conn.commit()
    conn.close()

def obter_valor_inicial_reserva(username):
    conn = conectar_bd()
    cursor = conn.cursor()
    cursor.execute("SELECT tipo, valor FROM reserva WHERE username = ?", (username,))
    movimentacoes = cursor.fetchall()
    conn.close()
    
    total = 0.0
    for tipo, valor in movimentacoes:
        if tipo == "Aporte":
            total += valor
        elif tipo == "Resgate":
            total -= valor
    return total

def obter_historico_reserva(username):
    conn = conectar_bd()
    cursor = conn.cursor()
    cursor.execute("SELECT tipo, valor, data FROM reserva WHERE username = ? ORDER BY data DESC", (username,))
    dados = cursor.fetchall()
    conn.close()
    return dados

# ==========================================
# GESTÃO SAAS & ADMINISTRAÇÃO
# ==========================================

def obter_plano_usuario(username):
    conn = conectar_bd()
    cursor = conn.cursor()
    cursor.execute("SELECT plano FROM usuarios WHERE username = ?", (username,))
    res = cursor.fetchone()
    conn.close()
    return res[0] if res else "Gratuito"

def atualizar_plano_usuario(username, novo_plano):
    conn = conectar_bd()
    cursor = conn.cursor()
    cursor.execute("UPDATE usuarios SET plano = ? WHERE username = ?", (novo_plano, username))
    conn.commit()  # Garante commit imediato no SQLite
    conn.close()

def listar_todos_usuarios():
    conn = conectar_bd()
    cursor = conn.cursor()
    cursor.execute("SELECT id, username, nome_completo, email, telefone, plano FROM usuarios")
    dados = cursor.fetchall()
    conn.close()
    return dados

# ==========================================
# AUXILIARES
# ==========================================

def formatar_brl(valor):
    """Formata valores numéricos para a moeda brasileira."""
    return f"R$ {valor:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")

# Links de compatibilidade explícita
obter_total_reserva = obter_valor_inicial_reserva
obter_saldo_reserva_atual = obter_valor_inicial_reserva
registrar_movimentacao_reserva = atualizar_valor_inicial_reserva