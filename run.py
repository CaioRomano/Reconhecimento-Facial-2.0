import os
from pathlib import Path
from typing import List, Union

import click as cli

from src.Database.execute import execute_exist_tables, execute_create_database, execute_create_table, \
    execute_close_connection, execute_delete_table, \
    execute_delete_data, execute_check_database_tables
from src.Database.options import EnumTables, EnumDB
from src.Face_Recognition.execute import execute_face_recognition
from src.config import PATH_PROJECT
from src.images.execute import execute_get_images, execute_verify_images, execute_crop_images, execute_name_images
from src.utils.logs import configura_logs


@cli.group()
def grupo_principal() -> None:
    """
     Grupo principal de comandos.
    """

    pass


@grupo_principal.group()
def database() -> None:
    """
    Grupo de comandos responsável pelas operações dentro do banco de dados.
    """

    pass


@database.group()
def create() -> None:
    """
    Grupo de comandos responsável pela criação do Banco de Dados e Tabelas.
    """

    pass


@database.group()
def delete() -> None:
    """
    Grupo de comandos responsável por exclusões dentro do Banco de Dados.
    """

    pass


@grupo_principal.group()
def recognition() -> None:
    """
    Grupo responsável pelo reconhecimento facial.
    """

    execute_check_database_tables()


@grupo_principal.group()
def images() -> None:
    """
    Grupo de comandos responsável pela manipulação das imagens
    """

    execute_check_database_tables()


@grupo_principal.group()
def web() -> None:
    """
    Grupo responsável pelo acesso a recursos web.
    """

    execute_check_database_tables()


@create.command()
@cli.option(
    '--name',
    '-n',
    'name',
    type=cli.Choice([s.value for s in EnumDB])
)
@cli.option(
    '--path',
    '-p',
    'path_db',
    type=cli.Choice([PATH_PROJECT]),
    default=PATH_PROJECT
)
def db(name: str, path_db: Path) -> None:
    """
    Cria o Banco de Dados.

    :param name: Nome do Banco de Dados.
    :param path_db: Caminho do Banco de Dados.
    """
    configura_logs()
    if os.path.exists(path_db / name):
        cli.echo(f'Banco de Dados {name} já existe!')
    else:
        execute_create_database(path_db=path_db, db_name=name, check_same_thread=False)
        cli.echo(f'Banco de dados {name} criado com sucesso!')


@create.command()
@cli.argument(
    'tables',
    nargs=-1,
    type=cli.Choice([s.value for s in EnumTables])
)
def table(tables: Union[List[str], str]) -> None:
    """
    Cria uma ou mais tabelas.

    :param tables: Nome ou lista de nome de tabelas.
    """

    _, tables_aux = execute_exist_tables(EnumDB.database.value)
    if set(tables) == set(tables_aux):
        cli.echo('As tabelas já existem!')
        exit()
    else:
        for table in tables:
            if table in tables_aux:
                cli.echo(f'Tabela {table} já existe!')
            else:
                execute_create_table(table=table)
                cli.echo(f'Tabela {table} criada com sucesso!')


@delete.command()
@cli.argument(
    'tables',
    nargs=-1,
    type=cli.Choice([s.value for s in EnumTables])
)
def table(tables: List[str]) -> None:
    """
    Exclui uma ou mais tabelas.

    :param tables: Nome ou lista de tabelas.
    """

    confirmation = cli.confirm('Essa ação não pode ser desfeita!\n\tQuer continuar?')
    if confirmation:
        for table in tables:
            execute_delete_table(table=table)
            cli.echo(f'Tabela {table} removida com sucesso!')


@delete.command()
@cli.argument(
    'tables',
    nargs=-1,
    type=cli.Choice([s.value for s in EnumTables])
)
def data(tables: List[str]) -> None:
    """
    Exclui os dados de uma ou mais tabelas.

    :param tables: Nome ou lista de tabelas.
    """

    confirmation = cli.confirm('Essa ação não pode ser desfeita!\n\tQuer continuar?')
    if confirmation:
        for table in tables:
            execute_delete_data(table=table)
            cli.echo(f'Dados da tabela {table} removidos com sucesso!')


@delete.command()
@cli.option(
    '--name',
    '-n',
    'name',
    type=cli.Choice([s.value for s in EnumDB])
)
@cli.option(
    '--path',
    '-p',
    'path_db',
    default=PATH_PROJECT,
    type=cli.Choice([PATH_PROJECT])
)
def db(name: str, path_db: str) -> None:
    """
    Exclui o Banco de Dados.

    :param name: Nome do Banco de Dados.
    :param path_db: Caminho para o Banco de Dados.
    """

    confirmation = cli.confirm('Essa ação não pode ser desfeita!\n\tQuer continuar?')
    if confirmation:
        path = f'{path_db}/{name}'
        if os.path.exists(path):
            os.remove(path)
            cli.echo(f'Banco de dados {name} apagado com sucesso')
        else:
            cli.echo(f'Banco de dados {name} não existe!')
        pass


@images.command()
@cli.argument(
    'task',
    nargs=1,
    type=cli.Choice(['capturar_imagem', 'nomear_imagem', 'recortar_imagem', 'verificar_imagem', '*'],
                    case_sensitive=False)
)
def execute_task(task: str) -> None:
    """
    Executa uma ou um conjunto de etapas relacionadas a manipulação das imagens.
    "*" é para executar todas as etapas.

    :param task: etapas de manipulação das imagens.
    """

    configura_logs()
    if task == 'capturar_imagem':
        execute_get_images()
    elif task == 'nomear_imagem':
        execute_name_images()
    elif task == 'recortar_imagem':
        execute_crop_images()
    elif task == 'verificar_imagem':
        execute_verify_images()
    elif task == '*':
        execute_get_images()
        execute_name_images()
        execute_verify_images()
        execute_crop_images()
    else:
        pass


@recognition.command()
def init() -> None:
    """
    Inicia o Reconhecimento Facial.
    """
    configura_logs(file_name_log='face_recognition')
    execute_face_recognition()


@web.command()
def enter() -> None:
    """
    Acessa uma página na Web.
    """
    pass
    # configura_logs()
    # cli.echo('Clique no terminal e aperte Ctrl+c para finalizar conexão ou aperte o botão "Cortar Conexão"')
    # sys.argv = ['streamlit', 'run', DIR_WEB_APP]
    # sys.exit(main())


if __name__ == '__main__':
    grupo_principal()
    execute_close_connection()
