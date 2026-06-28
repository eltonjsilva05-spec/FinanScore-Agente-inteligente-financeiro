import sqlite3
import hashlib

def conectar():
    return sqlite3.connect("finanscore.db")

def formatar_brl(valor):
    return f"R$ {valor:,.2f}".replace(",", "v").replace(".", ",").replace("v", ".")

def inicializar_banco():
    conn = conectar()
    cursor = conn.cursor()
    
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS usuarios (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE,
            senha TEXT,
            nome TEXT,
            email TEXT,
            telefone TEXT,
            plano TEXT DEFAULT 'Gratuito'
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS transacoes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            usuario TEXT,
            data TEXT,
            descricao TEXT,
            categoria TEXT,
            tipo TEXT,
            valor REAL,
            conta_id INTEGER DEFAULT 0
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS reserva_inicial (
            usuario TEXT PRIMARY KEY,
            valor_fixo REAL DEFAULT 0.0
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS contas_bancarias (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            usuario TEXT,
            banco TEXT,
            agencia TEXT,
            conta TEXT,
            tipo_conta TEXT,
            saldo_inicial REAL DEFAULT 0.0
        )
    """)

    conn.commit()
    conn.close()

def criptografar_senha(senha):
    return hashlib.sha256(senha.encode()).hexdigest()

# --- FUNÇÃO CORRIGIDA AQUI ---
def criar_usuario(username, senha, nome, email, telefone):
    conn = conectar()
    cursor = conn.cursor()
    senha_hash = criptografar_senha(senha)
    try:
        # Corrigido: 6 colunas mapeadas perfeitamente para 6 valores (?,?,?,?,?,?)
        cursor.execute("""
            INSERT INTO usuarios (username, senha, nome, email, telefone, plano) 
            VALUES (?, ?, ?, ?, ?, 'Gratuito')
        """, (username, senha_hash, nome, email, telefone))
        conn.commit()
        return True
    except sqlite3.IntegrityError:
        return False
    finally:
        conn.close()

def verificar_login(username, senha):
    conn = conectar()
    cursor = conn.cursor()
    senha_hash = criptografar_senha(senha)
    cursor.execute("SELECT * FROM usuarios WHERE username = ? AND senha = ?", (username, senha_hash))
    usuario = cursor.fetchone()
    conn.close()
    return usuario is not None

def obter_plano_usuario(username):
    conn = conectar()
    cursor = conn.cursor()
    cursor.execute("SELECT plano FROM usuarios WHERE username = ?", (username,))
    resultado = cursor.fetchone()
    conn.close()
    if resultado:
        return resultado[0]
    return "Gratuito"

def atualizar_plano_usuario(username, novo_plano):
    conn = conectar()
    cursor = conn.cursor()
    cursor.execute("UPDATE usuarios SET plano = ? WHERE username = ?", (novo_plano, username))
    conn.commit()
    conn.close()

def inserir_transacao(usuario_nome, data, descricao, categoria, tipo, valor, conta_id=0):
    conn = conectar()
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO transacoes (usuario, data, descricao, categoria, tipo, valor, conta_id)
        VALUES (?, ?, ?, ?, ?, ?, ?)
    """, (usuario_nome, data, descricao, categoria, tipo, valor, conta_id))
    conn.commit()
    conn.close()

def listar_transacoes_usuario(usuario_nome):
    conn = conectar()
    cursor = conn.cursor()
    cursor.execute("SELECT id, data, descricao, categoria, tipo, valor, conta_id FROM transacoes WHERE usuario = ? ORDER BY data DESC", (usuario_nome,))
    dados = cursor.fetchall()
    conn.close()
    return dados

def excluir_transacao(id_transacao):
    conn = conectar()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM transacoes WHERE id = ?", (id_transacao,))
    conn.commit()
    conn.close()

def atualizar_transacao(id_transacao, data, descricao, categoria, tipo, valor, conta_id):
    conn = conectar()
    cursor = conn.cursor()
    cursor.execute("""
        UPDATE transacoes 
        SET data = ?, descricao = ?, categoria = ?, tipo = ?, valor = ?, conta_id = ?
        WHERE id = ?
    """, (data, descricao, categoria, tipo, valor, conta_id, id_transacao))
    conn.commit()
    conn.close()

def soma_receitas_usuario(usuario_nome):
    nome = usuario_nome["nome"] if isinstance(usuario_nome, dict) else usuario_nome
    conn = conectar()
    cursor = conn.cursor()
    cursor.execute("SELECT SUM(valor) FROM transacoes WHERE usuario = ? AND tipo = 'Receita'", (nome,))
    total = cursor.fetchone()[0]
    conn.close()
    return total if total else 0.0

def soma_despesas_usuario(usuario_nome):
    nome = usuario_nome["nome"] if isinstance(usuario_nome, dict) else usuario_nome
    conn = conectar()
    cursor = conn.cursor()
    cursor.execute("SELECT SUM(valor) FROM transacoes WHERE usuario = ? AND tipo = 'Despesa'", (nome,))
    total = cursor.fetchone()[0]
    conn.close()
    return total if total else 0.0

def dados_grafico_categorias(usuario_nome):
    conn = conectar()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT categoria, SUM(valor) 
        FROM transacoes 
        WHERE usuario = ? AND tipo = 'Despesa' 
        GROUP BY categoria
    """, (usuario_nome,))
    dados = cursor.fetchall()
    conn.close()
    return dados

def obter_valor_inicial_reserva(usuario_nome):
    conn = conectar()
    cursor = conn.cursor()
    cursor.execute("SELECT valor_fixo FROM reserva_inicial WHERE usuario = ?", (usuario_nome,))
    resultado = cursor.fetchone()
    conn.close()
    return resultado[0] if resultado else 0.0

def atualizar_valor_inicial_reserva(usuario_nome, novo_valor):
    conn = conectar()
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO reserva_inicial (usuario, valor_fixo)
        VALUES (?, ?)
        ON CONFLICT(usuario) DO UPDATE SET valor_fixo = excluded.valor_fixo
    """, (usuario_nome, novo_valor))
    conn.commit()
    conn.close()

def obter_total_reserva(usuario_nome):
    conn = conectar()
    cursor = conn.cursor()
    cursor.execute("SELECT SUM(valor) FROM transacoes WHERE usuario = ? AND categoria = 'Reserva' AND tipo = 'Despesa'", (usuario_nome,))
    total = cursor.fetchone()[0]
    conn.close()
    return total if total else 0.0

def inserir_conta_bancaria(usuario_nome, banco, agencia, conta, tipo_conta, saldo_inicial):
    conn = conectar()
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO contas_bancarias (usuario, banco, agencia, conta, tipo_conta, saldo_inicial)
        VALUES (?, ?, ?, ?, ?, ?)
    """, (usuario_nome, banco, agencia, conta, tipo_conta, saldo_inicial))
    conn.commit()
    conn.close()

def listar_contas_usuario(usuario_nome):
    conn = conectar()
    cursor = conn.cursor()
    cursor.execute("SELECT id, banco, agencia, conta, tipo_conta, saldo_inicial FROM contas_bancarias WHERE usuario = ?", (usuario_nome,))
    dados = cursor.fetchall()
    conn.close()
    return dados

def excluir_conta_bancaria(id_conta):
    conn = conectar()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM contas_bancarias WHERE id = ?", (id_conta,))
    conn.commit()
    conn.close()

def obter_saldo_atual_conta(id_conta, saldo_inicial_conta):
    conn = conectar()
    cursor = conn.cursor()
    
    cursor.execute("SELECT SUM(valor) FROM transacoes WHERE conta_id = ? AND tipo = 'Receita'", (id_conta,))
    receitas = cursor.fetchone()[0] or 0.0
    
    cursor.execute("SELECT SUM(valor) FROM transacoes WHERE conta_id = ? AND tipo = 'Despesa'", (id_conta,))
    despesas = cursor.fetchone()[0] or 0.0
    
    conn.close()
    return saldo_inicial_conta + receitas - despesas

def listar_todos_usuarios():
    """ Retorna a lista de todos os usuários cadastrados para o Painel Admin """
    conn = conectar()
    cursor = conn.cursor()
    # Busca ID, Username, Nome, Email, Telefone e Plano (esconde a senha por segurança)
    cursor.execute("SELECT id, username, nome, email, telefone, plano FROM usuarios ORDER BY id DESC")
    dados = cursor.fetchall()
    conn.close()
    return dados