from pathlib import Path
"""
AV03 - Projeto Aplicado I
Empresa: Schulz S.A.

Programa principal de demonstracao do MVP.
"""

import importlib.util
import sqlite3
from datetime import date
from uuid import uuid4


# Carrega o arquivo 04_classes.py.
spec = importlib.util.spec_from_file_location(
    "classes", "04_classes.py"
)
classes = importlib.util.module_from_spec(spec)
spec.loader.exec_module(classes)

Tecnico = classes.Tecnico
Equipamento = classes.Equipamento
Medicao = classes.Medicao
BancoDados = classes.BancoDados


def main():
    # Verifica se o banco de dados existe.
    caminho_banco = Path("schulz_calibracao.db")

    if not caminho_banco.exists():
        print("Criando banco de dados SQLite...")

        # Lê o script com a estrutura das tabelas.
        script = Path("03_banco.sql").read_text(
            encoding="utf-8"
        )

        # Cria o banco e executa os comandos SQL.
        with sqlite3.connect(caminho_banco) as conexao:
            conexao.executescript(script)

        print("Banco criado com sucesso!")

    banco = BancoDados()

    try:
        print("=== SISTEMA DE CALIBRACAO SCHULZ ===")

        # Cria um tecnico de demonstracao.
        tecnico = Tecnico("Tecnico Demonstracao", "TECNICO")
        id_tecnico = banco.cadastrar_tecnico(tecnico)

        # Cria um equipamento de demonstracao.
        # O codigo e unico para evitar duplicidade.
        codigo = "AV03-" + uuid4().hex[:12].upper()

        equipamento = Equipamento(
            codigo,
            "Termometro de demonstracao",
            "Fabricante Exemplo"
        )

        id_equipamento = banco.cadastrar_equipamento(equipamento)

        # Primeira medicao: dentro da tolerancia.
        medicao1 = Medicao(
            id_equipamento,
            id_tecnico,
            date.today().isoformat(),
            "Temperatura",
            100,
            5,
            5,
            103
        )

        banco.cadastrar_medicao(medicao1)

        # Segunda medicao: fora da tolerancia.
        medicao2 = Medicao(
            id_equipamento,
            id_tecnico,
            date.today().isoformat(),
            "Temperatura",
            100,
            5,
            5,
            108
        )

        banco.cadastrar_medicao(medicao2)

        # Consulta os registros usando JOIN.
        registros = banco.listar_medicoes()

        print("\n=== RELATORIO DE CALIBRACAO ===")

        for registro in registros:
            print("-" * 45)
            print("Medicao:", registro[0])
            print("Equipamento:", registro[1])
            print("Descricao:", registro[2])
            print("Tecnico:", registro[3])
            print("Parametro:", registro[4])
            print("Valor nominal:", registro[5])
            print("Valor obtido:", registro[6])
            print("Erro:", registro[7])
            print("Status:", registro[8])

        print("\nRelatorio gerado com sucesso!")

    except (sqlite3.Error, ValueError) as erro:
        print("Erro durante a execucao:", erro)


if __name__ == "__main__":
    main()
