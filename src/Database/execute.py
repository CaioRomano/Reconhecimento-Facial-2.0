from pathlib import Path
from typing import Tuple, Any, List, Union
import os

import click

from src.config import PATH_PROJECT
from src.Database.options import TABLE_DICT, DB_DICT, EnumDB, EnumTables


def execute_create_database(path_db: Path, db_name: str, check_same_thread: bool = False) -> None:
    """
    Executa a criação do banco de dados.

    :param path_db: Caminho do Banco de Dados.
    :param db_name: Nome do Banco de Dados.
    :param check_same_thread: Checa se a conexão e as demais operações do Banco de Dados devem ser executadas numa mesma Thread.
    """

    obj = DB_DICT[EnumDB(db_name)]()
    obj.create_database(path_db=path_db, db_name=db_name, check_same_thread=check_same_thread)


def execute_create_table(table: str) -> None:
    """
    Executa a criação de uma tabela.

    :param table: Nome da tabela.
    """

    obj = TABLE_DICT[EnumTables(table)](table_name=table)
    obj.create_table()


def execute_delete_table(table: str) -> None:
    """
    Executa a exclusão de uma tabela

    :param table: Nome da tabela.
    """

    obj = TABLE_DICT[EnumTables(table)](table_name=table)
    obj.delete_table()


def execute_delete_data(table: str) -> None:
    """
    Executa a exclusão dos dados de uma tabela.

    :param table: Nome da tabela.
    """

    obj = TABLE_DICT[EnumTables(table)](table_name=table)
    obj.delete_all_data()


def execute_exist_tables(db_name: str) -> Tuple[int, Any]:
    """
    Executa a verificação de existência de tabelas dentro do banco de Dados.

    :param db_name: Nome do Banco de Dados.
    """

    obj = DB_DICT[EnumDB(db_name)]()
    query = 'select name from sqlite_master where type="table";'
    tables = obj.cursor().execute(query).fetchall()
    if ('sqlite_sequence',) in tables:
        tables.remove(('sqlite_sequence',))
    tables = [table[0] for table in tables]
    num_tables = len(tables)
    return num_tables, tables


def execute_check_database_tables() -> None:
    """
     Executa uma verificação do número mínimo de tabelas para a aplicação funcionar.
    """

    if os.path.exists(PATH_PROJECT / EnumDB.database.value):
        num_tables, tables = execute_exist_tables(db_name=EnumDB.database.value)
        if num_tables < 1:
            click.echo('As tabelas necessárias não existem!')
            click.echo('Tabelas existentes: ')
            for table in tables:
                click.echo(f'\t- {table}')
            exit()
        else:
            pass
    else:
        click.echo('A ação não pode ser executada, pois o Banco de dados não existe!')
        exit()


def execute_close_connection() -> None:
    """
     Executa o término da conexão do Banco de Dados.
    """

    obj = DB_DICT[EnumDB.database.value]()
    obj.close_connection()


def execute_insert(table: str, name: str, face_encoding: Any, type_face: str, date_creation: str) -> None:
    """
    Executa a inserção de dados dentro de uma tabela.

    :param table: Nome da tabela.
    :param name: valor da coluna Nome.
    :param face_encoding: valor da coluna Face_encoding
    :param type_face: valor da coluna Type_face
    :param date_creation:  valor da coluna Date_creation
    """

    obj = TABLE_DICT[EnumTables(table)](table_name=table)
    obj.insert(
        name=name,
        type_face=type_face,
        face_encoding=face_encoding,
        date_creation=date_creation
    )


def execute_read_table(table: str, columns: Union[str, List[str]]) -> Any:
    """
    Exxecuta a leitura de uma tabela, após a seleção das colunas que serão lidas.

    :param table: Nome das colunas
    :param columns: Nome das colunas. "*" para retornar registros de todas as colunas
    """

    if table == EnumTables.peoplefaces.value:
        obj = TABLE_DICT[EnumTables(table)](table_name=table)
        result = obj.read_table(columns=columns)
        return result


if __name__ == '__main__':
    print(execute_read_table(EnumTables.peoplefaces.value, columns=['Nome', 'Type_face']))
