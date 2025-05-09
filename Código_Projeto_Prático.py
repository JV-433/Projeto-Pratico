import sqlite3
from sqlite3 import Error
import datetime

class Biblioteca:
    def __init__(self):
        # Inicia a conexão com o banco de dados e criar as tabelas
        try:
            self.connection = sqlite3.connect('biblioteca.db')
            self.cursor = self.connection.cursor()
            
            self._criar_tabelas()
            
        except Error as e:
            print(f"Erro ao conectar ao banco de dados: {e}")
            exit()

    def _criar_tabelas(self):
        # Cria as tabelas necessárias no banco de dados
        scripts = [
            """CREATE TABLE IF NOT EXISTS livros (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                titulo TEXT NOT NULL,
                autor TEXT NOT NULL,
                isbn TEXT UNIQUE NOT NULL,
                disponivel BOOLEAN DEFAULT TRUE
            )""",
            
            """CREATE TABLE IF NOT EXISTS usuarios (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                nome TEXT NOT NULL,
                email TEXT UNIQUE NOT NULL,
                senha TEXT
            )""",
            
            """CREATE TABLE IF NOT EXISTS emprestimos (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                livro_id INTEGER NOT NULL,
                usuario_id INTEGER NOT NULL,
                data_emprestimo TEXT NOT NULL,
                data_devolucao TEXT NOT NULL,
                devolvido BOOLEAN DEFAULT FALSE,
                multa REAL DEFAULT 0.00,
                FOREIGN KEY (livro_id) REFERENCES livros(id),
                FOREIGN KEY (usuario_id) REFERENCES usuarios(id)
            )"""
        ]
        
        for script in scripts:
            try:
                self.cursor.execute(script)
                self.connection.commit()
            except Error as e:
                print(f"Erro ao criar tabelas: {e}")
                exit()
    def _criar_admin_se_necessario(self):
        try:
            self.cursor.execute("SELECT id FROM usuarios WHERE email = ?", ('admin@admin',))
            if not self.cursor.fetchone():
                self.cursor.execute(
                "INSERT INTO usuarios (nome, email, senha) VALUES (?, ?, ?)",
                ('admin', 'admin@admin', '123')
        )
            self.connection.commit()
            print("Usuário admin criado com sucesso!")
        except Error as e:
            print(f"Erro ao verificar/criar usuário admin: {e}")
    
    def resetar_banco_de_dados(self):
        try:
            self.cursor.execute("PRAGMA foreign_keys = OFF")
            self.cursor.execute("DELETE FROM emprestimos")
            self.cursor.execute("DELETE FROM livros")
            self.cursor.execute("DELETE FROM usuarios")
            self.cursor.execute("PRAGMA foreign_keys = ON")
            self._criar_admin_se_necessario()
            self.connection.commit()
            print("Todos os dados foram resetados, mantendo a estrutura do banco.")
        except Error as e:
            print(f"Erro ao resetar o banco de dados: {e}")
            self.connection.rollback()

    # CADASTRO E CONSULTA
    def cadastrar_livro(self):
        """Cadastra um novo livro no sistema"""
        print("\n--- CADASTRO DE LIVRO ---")
        while True:
            titulo = input("Título do livro: ").strip()
            if not titulo:
                print("Erro: Título não pode ser vazio.")
                continue

            autor = input("Autor: ").strip()
            isbn = input("ISBN (13 dígitos): ").strip()
            
            if len(isbn) != 13 or not isbn.isdigit():
                print("Erro: ISBN inválido. Deve ter 13 dígitos.")
                continue

            try:
                self.cursor.execute(
                    "INSERT INTO livros (titulo, autor, isbn) VALUES (?, ?, ?)",
                    (titulo, autor, isbn)
                )
                self.connection.commit()
                print(f"Livro '{titulo}' cadastrado com sucesso! (ID: {self.cursor.lastrowid})")
                break
            except Error as e:
                print(f"Erro ao cadastrar livro: {e}")
                break

    def listar_livros(self):
        # Lista todos os livros cadastrados no sistema
        print("\n--- LIVROS CADASTRADOS ---")
        try:
            self.cursor.execute("SELECT * FROM livros")
            livros = self.cursor.fetchall()

            if not livros:
                print("Nenhum livro cadastrado.")
                return

            for livro in livros:
                status = "Disponível" if livro[4] else "Emprestado"
                print(f"ID: {livro[0]} | {livro[1]} ({livro[2]}) - ISBN: {livro[3]} | {status}")
        except Error as e:
            print(f"Erro ao listar livros: {e}")

    def buscar_livro(self):
        # Busca livros por título, autor ou ISBN
        print("\n--- BUSCAR LIVRO ---")
        termo = input("Digite título, autor ou ISBN: ").lower()
        
        try:
            self.cursor.execute("""
                SELECT * FROM livros 
                WHERE LOWER(titulo) LIKE ? 
                OR LOWER(autor) LIKE ? 
                OR isbn LIKE ?
            """, (f"%{termo}%", f"%{termo}%", f"%{termo}%"))
            
            resultados = self.cursor.fetchall()

            if not resultados:
                print("Nenhum livro encontrado.")
            else:
                for livro in resultados:
                    status = "Disponível" if livro[4] else "Emprestado"
                    print(f"ID: {livro[0]} | {livro[1]} - {status}")
        except Error as e:
            print(f"Erro ao buscar livros: {e}")

    # USUÁRIOS
    def cadastrar_usuario(self):
        # Cadastra um novo usuário no sistema
        print("\n--- CADASTRO DE USUÁRIO ---")
        nome = input("Nome completo: ").strip()
        email = input("E-mail: ").strip()
        senha = input("Senha: ").strip()
        
        try:
            self.cursor.execute(
                "INSERT INTO usuarios (nome, email, senha) VALUES (?, ?, ?)",
                (nome, email, senha)
            )
            self.connection.commit()
            print(f"Usuário '{nome}' cadastrado com sucesso! (ID: {self.cursor.lastrowid})")
        except Error as e:
            print(f"Erro ao cadastrar usuário: {e}")

    def listar_usuarios(self):
        # Lista todos os usuários cadastrados
        print("\n--- USUÁRIOS CADASTRADOS ---")
        try:
            self.cursor.execute("SELECT * FROM usuarios")
            usuarios = self.cursor.fetchall()

            if not usuarios:
                print("Nenhum usuário cadastrado.")
                return

            for usuario in usuarios:
                print(f"ID: {usuario[0]} | {usuario[1]} - {usuario[2]}")
        except Error as e:
            print(f"Erro ao listar usuários: {e}")