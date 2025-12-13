# init_db.py
import sqlite3
from pathlib import Path
import hashlib

DB_PATH = Path(__file__).parent / "estoque.db"

def generate_password_hash(password: str) -> str:
    return hashlib.sha256(password.encode('utf-8')).hexdigest()

conn = sqlite3.connect(DB_PATH)
c = conn.cursor()

# 1. Usuários
c.execute("DROP TABLE IF EXISTS users")
c.execute("""
CREATE TABLE users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT UNIQUE NOT NULL,
    password_hash TEXT NOT NULL,
    is_admin INTEGER DEFAULT 0
)
""")

# 2. Itens
c.execute("DROP TABLE IF EXISTS itens")
c.execute("""
CREATE TABLE itens (
    cod TEXT PRIMARY KEY,
    descricao TEXT,
    unid TEXT,
    estoque_minimo INTEGER DEFAULT 10
)
""")

# 3. Estoque (Saldo)
c.execute("DROP TABLE IF EXISTS estoque")
c.execute("""
CREATE TABLE estoque (
    cod TEXT PRIMARY KEY,
    descricao TEXT,
    unid TEXT,
    entradas INTEGER DEFAULT 0,
    saidas INTEGER DEFAULT 0,
    estoque_minimo INTEGER DEFAULT 10
)
""")

# 4. Entradas (Sem Nota Fiscal)
c.execute("DROP TABLE IF EXISTS entradas")
c.execute("""
CREATE TABLE entradas (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    cod TEXT,
    descricao TEXT,
    unid TEXT,
    quantidade INTEGER,
    data TEXT
)
""")

# 5. Saídas
c.execute("DROP TABLE IF EXISTS saidas")
c.execute("""
CREATE TABLE saidas (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    cod TEXT,
    descricao TEXT,
    unid TEXT,
    quantidade INTEGER,
    data TEXT
)
""")

# Criar Admin
admin_user = "admin"
admin_pass = "admin123"
hashed = generate_password_hash(admin_pass)
c.execute("INSERT INTO users (username, password_hash, is_admin) VALUES (?,?,?)", (admin_user, hashed, 1))

# Dados de Exemplo
base_itens = [
    ("MD01", "ACICLOVIR 200MG", "CAIXA", 10),
    ("MD02", "ACIDO ACETILSALICILICO AAS", "CAIXA", 50),
    ("MD03", "ALBENDAZOL SUS. 4%", "FRASCO", 5),
    ("MMH09", "ALCOOL 70%", "LITRO", 20)
]

for cod, desc, unid, min_s in base_itens:
    c.execute("INSERT INTO itens (cod, descricao, unid, estoque_minimo) VALUES (?,?,?,?)", (cod, desc, unid, min_s))
    c.execute("INSERT INTO estoque (cod, descricao, unid, entradas, saidas, estoque_minimo) VALUES (?,?,?,?,?,?)", (cod, desc, unid, 0, 0, min_s))

conn.commit()
conn.close()
print("Banco recriado: Nota Fiscal removida e Admin restaurado.")