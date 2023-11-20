from src.Database.Faces.PeopleFaces import PeopleFaces
from src.Database.DB import DB
from enum import Enum


class EnumTables(Enum):
    """
    Classe Enum que aponta para as tabelas do Banco de Dados.
    """

    peoplefaces = 'PeopleFaces'


class EnumDB(Enum):
    """
    Classe Enum que aponta para o Banco de Dados.
    """

    database = 'Database.db'


# Dicionário que permite acesso aos objetos do tipo tabela que fazem parte do banco de Dados.
TABLE_DICT = {
    EnumTables.peoplefaces: PeopleFaces
}

# Dicionário que permite o acesso aos objeto do tipo BD.
DB_DICT = {
    EnumDB.database: DB,
}
