from src.images.GetImages import GetImages
from src.images.NameImages import NameImages
from src.images.CropImages import CropImages
from src.images.VerifyFace import VerifyFace


def execute_get_images() -> None:
    """
    Executa recuperação de imagens.
    """

    obj = GetImages()
    obj.run()


def execute_name_images() -> None:
    """
    Executa nomeação de imagens.
    """

    obj = NameImages()
    obj.run()


def execute_crop_images() -> None:
    """
    Executa Recorte das imagens.
    """

    obj = CropImages()
    obj.run()


def execute_verify_images() -> None:
    """
    Executa verificação e armazenamento das informaçãoes das imagens no Banco de Dados.
    """

    obj = VerifyFace()
    obj.run()
