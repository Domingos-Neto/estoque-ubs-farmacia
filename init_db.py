import os
import psycopg2
from psycopg2 import sql
import hashlib
# Importe a Path e o sqlite3.connect NÃO são usados aqui.

# --- Funções Auxiliares ---

def generate_password_hash(password: str) -> str:
    """Gera o hash SHA256 para a senha."""
    return hashlib.sha256(password.encode('utf-8')).hexdigest()

def get_db_conn():
    """Obtém a conexão PostgreSQL usando a variavel de ambiente."""
    DATABASE_URL = os.environ.get('DATABASE_URL')
    if not DATABASE_URL:
        raise Exception("DATABASE_URL não configurada. O script init_db.py precisa dela para rodar.")
    # Adiciona a configuracao SSLmode 'require' para conexoes Render/Remotas
    return psycopg2.connect(DATABASE_URL + "?sslmode=require")

# --- Lógica Principal ---

if __name__ == '__main__':
    try:
        # 1. Obter a Conexão PostgreSQL
        conn = get_db_conn() 
        c = conn.cursor()

        # 2. Comandos SQL para Criar/Recriar Tabelas (Sintaxe PostgreSQL)

        # Usando DROP TABLE ... CASCADE para garantir a limpeza em caso de chaves estrangeiras
        c.execute("DROP TABLE IF EXISTS public.users CASCADE")
        c.execute("DROP TABLE IF EXISTS public.itens CASCADE")
        c.execute("DROP TABLE IF EXISTS public.estoque CASCADE")
        c.execute("DROP TABLE IF EXISTS public.entradas CASCADE")
        c.execute("DROP TABLE IF EXISTS public.saidas CASCADE")

        # 1. Usuários
        c.execute("""
        CREATE TABLE public.users (
            id SERIAL PRIMARY KEY, -- PostgreSQL usa SERIAL para auto-incremento
            username TEXT UNIQUE NOT NULL,
            password_hash TEXT NOT NULL,
            is_admin INTEGER DEFAULT 0
        )
        """)

        # 2. Itens
        c.execute("""
        CREATE TABLE public.itens (
            cod TEXT PRIMARY KEY,
            descricao TEXT,
            unid TEXT,
            estoque_minimo INTEGER DEFAULT 10
        )
        """)

        # 3. Estoque (Saldo)
        c.execute("""
        CREATE TABLE public.estoque (
            cod TEXT PRIMARY KEY,
            descricao TEXT,
            unid TEXT,
            entradas INTEGER DEFAULT 0,
            saidas INTEGER DEFAULT 0,
            estoque_minimo INTEGER DEFAULT 10
        )
        """)

        # 4. Entradas (Sem Nota Fiscal)
        c.execute("""
        CREATE TABLE public.entradas (
            id SERIAL PRIMARY KEY, -- PostgreSQL usa SERIAL para auto-incremento
            cod TEXT,
            descricao TEXT,
            unid TEXT,
            quantidade INTEGER,
            data TEXT
        )
        """)

        # 5. Saídas
        c.execute("""
        CREATE TABLE public.saidas (
            id SERIAL PRIMARY KEY, -- PostgreSQL usa SERIAL para auto-incremento
            cod TEXT,
            descricao TEXT,
            unid TEXT,
            quantidade INTEGER,
            data TEXT
        )
        """)

        # 3. Inserção de Dados (Usando %s como placeholder)

        # Criar Admin
        admin_user = "admin"
        admin_pass = "admin123"
        hashed = generate_password_hash(admin_pass)
        # Atenção ao public.users e %s
        c.execute("INSERT INTO public.users (username, password_hash, is_admin) VALUES (%s, %s, %s)", (admin_user, hashed, 1))

        # Dados de Exemplo
        base_itens = [
            ("MD01", "ACICLOVIR 200MG", "CAIXA", 10),
            ("MD02", "ACIDO ACETILSALICILICO AAS", "CAIXA", 50),
            ("MD03", "ALBENDAZOL SUS. 4%", "FRASCO", 5),
            ("MMH09", "ALCOOL 70%", "LITRO", 20)
        ]

        for cod, desc, unid, min_s in base_itens:
            # Atenção ao public.itens e %s
            c.execute("INSERT INTO public.itens (cod, descricao, unid, estoque_minimo) VALUES (%s, %s, %s, %s)", (cod, desc, unid, min_s))
            # Atenção ao public.estoque e %s
            c.execute("INSERT INTO public.estoque (cod, descricao, unid, entradas, saidas, estoque_minimo) VALUES (%s, %s, %s, %s, %s, %s)", (cod, desc, unid, 0, 0, min_s))

        # 4. Finalizar
        conn.commit()
        conn.close()
        print("Banco recriado: Nota Fiscal removida e Admin restaurado.")

    except Exception as e:
        print(f"Ocorreu um erro fatal na inicialização do DB: {e}")
        if 'conn' in locals() and conn is not None:
            conn.close() # Garante que a conexao é fechada
        raise # Levanta o erro para ver o traceback completo