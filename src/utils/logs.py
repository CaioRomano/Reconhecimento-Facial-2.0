from pathlib import Path
import typing
import logging
from src.config import PATH_PROJECT
from datetime import datetime


def configura_logs(
    formato: str = "{asctime} [{levelname}] arquivo: [{filename}] função: [{funcName}():{lineno}] - {message}",
    arquivo: bool = True,
    pasta_logs: typing.Union[str, Path, None] = None,
    file_name_log: str = 'app'
) -> str:
    """
    Inicia os objetos Logger e realiza as configurações de formatação,
    nível e saída do log

    :param formato: formatação dos logs
    :param arquivo: flag se devemos criar um stream para um arquivo
    :param pasta_logs: caminho para a pasta de logs
    :param file_name_log: Nome do arquivo log
    :return: data e horário da execução do programa
    """

    logger_raiz = logging.getLogger()
    logger_raiz.setLevel(logging.INFO)

    chave_de_execucao = datetime.now().strftime("%Y%m%d-%H%M%S")

    if len(logger_raiz.handlers) > 0:
        chandler = logger_raiz.handlers[0]
    else:
        chandler = logging.StreamHandler()
        logger_raiz.addHandler(chandler)
    chandler.setLevel(logging.INFO)

    formatter = logging.Formatter(formato, style="{", datefmt="%d/%m/%Y %H:%M:%S")
    chandler.setFormatter(formatter)

    if arquivo:
        if pasta_logs is None:
            log_dir = PATH_PROJECT / 'logs'
        else:
            log_dir = Path(pasta_logs)
        log_dir.mkdir(parents=True, exist_ok=True)

        today_date = datetime.now().strftime("%d-%m-%Y")
        fhandler = logging.FileHandler(
            filename=log_dir / f"{today_date}_{file_name_log}.log", mode="a"
        )
        fhandler.setLevel(logging.INFO)

        fhandler.setFormatter(formatter)
        logger_raiz.addHandler(fhandler)

    logger = logging.getLogger(__name__)
    logger.info(f"INICIALIZANDO EXECUÇÃO {chave_de_execucao}")

    return chave_de_execucao
