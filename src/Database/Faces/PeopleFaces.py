import sqlite3 as sql
from src.Database.DB import DB


class PeopleFaces(DB):
    """
    Classe responsável por popular o Banco de dados
    """

    _table_name: str

    def __init__(self, table_name: str) -> None:
        """
        Método construtor da classe

        :param table_name: Nome da tabela.
        """
        super().__init__()
        self._table_name = table_name

    def create_table(self) -> None:
        """
        Cria a tabela com as respectivas colunas e suas informações
        """

        try:
            self._cursor.execute(f"""
            create table if not exists {self._table_name}
            (
            ID integer not null primary key autoincrement,
            Nome text not null,
            Type_face text not null check (Type_face in ("KNOWN", "UNKNOWN")),
            Face_encoding text not null,
            Data_criacao text not null,
            UNIQUE(Nome)
            )
            """)
        except sql.Error as e:
            self._logger.error('ERRO NA CRIAÇÃO DA TABELA.')
            self._logger.exception(f'EXCEÇÃO: {e}')
        else:
            self._connection.commit()
            self._logger.info(f'TABELA {self._table_name} CRIADA')

    def insert(self, name: str = None, face_encoding: list = None, type_face: str = None,
               date_creation: str = None) -> bool:
        """
        Método responsável por inserir novos registros na tabela.

        :param name: Nome do indivíduo. Nomes que começam com "face_" indicam alguém que não possui identificação.
        :param face_encoding: Encoding do rosto do indivíduo.
        :param type_face: Indica se o indivíduo é alguém conhecido ou desconhecido, representado pelos valores KNOWN e
        UNKNOWN, respectivamente.
        :param date_creation: Data de criação do registro.
        :return: Retorna um valor booleano que indica se a inserção foi bem sucedida ou não.
        """

        try:
            self._cursor.execute(f"""
            insert into {self._table_name} (Nome, Face_encoding, Type_face, Data_criacao)
            values
            (?, ?, ?, ?)
            """, (str(name), str(face_encoding), str(type_face), str(date_creation)))
        except sql.Error as e:
            self._logger.error('ERRO NA INSERÇÃO DA TABELA.')
            self._logger.exception(f'EXCEÇÃO: {e}')
            return False
        else:
            self._connection.commit()
            return True
