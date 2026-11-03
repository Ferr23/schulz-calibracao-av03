"""
AV03 - Projeto Aplicado I
Empresa: Schulz S.A.

Classes POO e conexao com SQLite.
"""

import sqlite3


# Classe que representa o tecnico ou solicitante.
class Tecnico:
    def __init__(self, nome, tipo="TECNICO"):
        if not nome.strip():
            raise ValueError("O nome nao pode ficar vazio.")

        if tipo not in ("TECNICO", "SOLICITANTE"):
            raise ValueError("Tipo de profissional invalido.")

        self.nome = nome
        self.tipo = tipo


# Classe que representa um equipamento.
class Equipamento:
    def __init__(self, codigo, denominacao, fabricante=""):
        if not codigo.strip() or not denominacao.strip():
            raise ValueError("Codigo e denominacao sao obrigatorios.")

        self.codigo = codigo
        self.denominacao = denominacao
        self.fabricante = fabricante


# Classe responsavel pelos dados da medicao.
class Medicao:
    def __init__(self, id_equipamento, id_tecnico,
                 data_medicao, parametro, valor_nominal,
                 tolerancia_positiva, tolerancia_negativa,
                 valor_obtido):

        if tolerancia_positiva < 0 or tolerancia_negativa < 0:
            raise ValueError("As tolerancias nao podem ser negativas.")

        self.id_equipamento = id_equipamento
        self.id_tecnico = id_tecnico
        self.data_medicao = data_medicao
        self.parametro = parametro
        self.valor_nominal = valor_nominal
        self.tolerancia_positiva = tolerancia_positiva
        self.tolerancia_negativa = tolerancia_negativa
        self.valor_obtido = valor_obtido

    # Calcula o erro da medicao.
    def calcular_erro(self):
        return self.valor_obtido - self.valor_nominal

    # Verifica se a medicao esta dentro das tolerancias.
    def validar_status(self):
        minimo = self.valor_nominal - self.tolerancia_negativa
        maximo = self.valor_nominal + self.tolerancia_positiva

        if minimo <= self.valor_obtido <= maximo:
            return "CONFORME"

        return "NAO CONFORME"


# Classe responsavel pela comunicacao com o banco SQLite.
class BancoDados:
    def __init__(self, caminho="schulz_calibracao.db"):
        self.caminho = caminho

    # Abre uma conexao com o banco de dados.
    def conectar(self):
        conexao = sqlite3.connect(self.caminho)
        conexao.execute("PRAGMA foreign_keys = ON")
        return conexao

    # INSERT: cadastra um tecnico.
    def cadastrar_tecnico(self, tecnico):
        conexao = self.conectar()

        try:
            cursor = conexao.execute(
                "INSERT INTO tecnicos (nome, tipo) VALUES (?, ?)",
                (tecnico.nome, tecnico.tipo)
            )
            conexao.commit()
            return cursor.lastrowid

        finally:
            conexao.close()

    # INSERT: cadastra um equipamento.
    def cadastrar_equipamento(self, equipamento):
        conexao = self.conectar()

        try:
            cursor = conexao.execute(
                """INSERT INTO equipamentos
                   (codigo, denominacao, fabricante)
                   VALUES (?, ?, ?)""",
                (equipamento.codigo,
                 equipamento.denominacao,
                 equipamento.fabricante)
            )
            conexao.commit()
            return cursor.lastrowid

        finally:
            conexao.close()

    # INSERT: registra uma medicao e calcula seu status.
    def cadastrar_medicao(self, medicao):
        conexao = self.conectar()

        try:
            cursor = conexao.execute(
                """INSERT INTO medicoes
                   (id_equipamento, id_tecnico, data_medicao,
                    parametro, valor_nominal,
                    tolerancia_positiva, tolerancia_negativa,
                    valor_obtido, erro, status)
                   VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
                (
                    medicao.id_equipamento,
                    medicao.id_tecnico,
                    medicao.data_medicao,
                    medicao.parametro,
                    medicao.valor_nominal,
                    medicao.tolerancia_positiva,
                    medicao.tolerancia_negativa,
                    medicao.valor_obtido,
                    medicao.calcular_erro(),
                    medicao.validar_status()
                )
            )

            conexao.commit()
            return cursor.lastrowid

        finally:
            conexao.close()

    # SELECT com JOIN: consulta o relatorio de calibracao.
    def listar_medicoes(self):
        conexao = self.conectar()

        try:
            cursor = conexao.execute(
                """SELECT
                       m.id_medicao,
                       e.codigo,
                       e.denominacao,
                       t.nome,
                       m.parametro,
                       m.valor_nominal,
                       m.valor_obtido,
                       m.erro,
                       m.status
                   FROM medicoes AS m
                   JOIN equipamentos AS e
                       ON m.id_equipamento = e.id_equipamento
                   JOIN tecnicos AS t
                       ON m.id_tecnico = t.id_tecnico
                   ORDER BY m.id_medicao"""
            )
            return cursor.fetchall()

        finally:
            conexao.close()

    # UPDATE: atualiza o resultado de uma medicao.
    def atualizar_medicao(self, id_medicao, medicao):
        conexao = self.conectar()

        try:
            cursor = conexao.execute(
                """UPDATE medicoes
                   SET valor_obtido = ?,
                       erro = ?,
                       status = ?
                   WHERE id_medicao = ?""",
                (
                    medicao.valor_obtido,
                    medicao.calcular_erro(),
                    medicao.validar_status(),
                    id_medicao
                )
            )

            conexao.commit()
            return cursor.rowcount

        finally:
            conexao.close()
