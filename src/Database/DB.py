import logging
import os
import sqlite3 as sql
from pathlib import Path
from typing import Union, List
from src.config import PATH_PROJECT


class DB:
    """
    Classe abstrata, responsável por agregar as principais funcionalidades para as classes filhas.
    """

    _connection: sql.Connection
    _cursor: sql.Cursor
    _table_name: str
    _logger: logging.Logger

    def __init__(self) -> None:
        """
        Instancia objeto da classe DB.
        """

        try:
            self._logger = logging.getLogger(__name__)
            db_name = 'Database.db'
            if os.path.exists(PATH_PROJECT / db_name):
                self._connection = sql.connect(os.path.join(PATH_PROJECT, db_name),
                                               check_same_thread=False)
                self._cursor = self._connection.cursor()
        except sql.Error as e:
            print(e)

    def create_database(self, path_db: Path, db_name: str, check_same_thread: bool = False):
        """
        Cria o Banco de Dados

        :param path_db: Caminho do Banco de Dados.
        :param db_name: Nome do Banco de Dados.
        :param check_same_thread: Checa se a conexão e as demais operações do Banco de Dados devem ser executadas numa mesma Thread.
        """

        try:
            self._logger.info('CRIANDO BANCO DE DADOS...')
            self._connection = sql.connect(os.path.join(path_db, db_name), check_same_thread=check_same_thread)
        except sql.Error as e:
            self._logger.error('ERRO NA CRIAÇÃO DO BANCO DE DADOS.')
            self._logger.exception(f'EXCEÇÃO: {e}')
        else:
            self._cursor = self._connection.cursor()
            self._logger.info('BANCO DE DADOS CRIADO')

    def cursor(self) -> sql.Cursor:
        """
        Acessa o cursor do Banco de Dados, responsável por realizar operações dentro do banco de dados.

        :return: retorna um cursor para o Banco de Dados.
        """

        return self._cursor

    def connection(self) -> sql.Connection:
        """
        Acessa a conexão do Banco de Dados, responsável por persistir as operações feitas no cursor.

        :return: retorna uma conexão com o Banco de Dados.
        """

        return self._connection

    def read_table(self, columns: Union[str, List[str]] = '*') -> list:
        """
        Retorna dados de uma tabela ao especificar as colunas.

        :param columns: Colunas de dados que serão retornadas. "*" para retornar dados de todas as colunas.
        :return: Retorna uma lista de registros da tabela.
        """

        if isinstance(columns, str):
            pass
        elif isinstance(columns, list):
            columns = ', '.join(columns)

        if columns == '*':
            query = f"""select * from {self._table_name};"""
        else:
            query = f"""select {columns} from {self._table_name};"""

        self._cursor.execute(query)
        return list(self.cursor().fetchall())

    def delete_all_data(self) -> None:
        """
        Deleta todos os dados de uma tabela.
        """

        try:
            self._cursor.execute(f'delete from {self._table_name};')
        except sql.Error as e:
            self._logger.error('ERRO NA DELEÇÃO DOS DADOS.')
            self._logger.exception(f'EXCEÇÃO: {e}')
        else:
            self._connection.commit()
            self._logger.info('TODOS OS DADOS FORAM DELETADOS')

    def delete_table(self) -> None:
        """
        Deleta uma tabela.
        """

        try:
            query = f'drop table {self._table_name};'
            self._cursor.execute(query)
            self._logger.info('TABELA DELETADA')
        except sql.OperationalError as e:
            self._logger.error('ERRO NA DELEÇÃO DA TABELA.')
            self._logger.warning(f'A TABELA {self._table_name} TALVEZ NÃO EXISTA')
            self._logger.exception(f'EXCEÇÃO: {e}')
        except sql.Error as e:
            self._logger.exception(f'EXCEÇÃO: {e}')

    def close_connection(self) -> None:
        """
        Fecha a conexão com o Banco de Dados.
        """

        self._connection.close()
        self._logger.info('DESCONEXÃO COM BANCO DE DADOS CONCLUÍDA')
