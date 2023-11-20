import logging
import os
from typing import List, Tuple, Any
import cv2
import face_recognition as fr
import numpy as np
from PIL import Image
from tqdm import tqdm

from src.config import DIR_IMG


class CropImages:
    """
    Classe responsável por recortar as imagens remanescentes no diretório após a execução da classe VerifyFace.
    """

    _logger: logging.Logger

    def __init__(self):
        """
        Método Construtor da classe
        """

        self._logger = logging.getLogger(__name__)

    def _get_face_location(self, name_image: str) -> Tuple[List[Tuple], np.ndarray]:
        """
        Recuperar a localização do rosto do indivíduo presente na foto.

        :param name_image: Nome de imagem.
        :return: Retorna a localizção dos rostos existentes na foto e a imagem em si.
        """

        image = fr.load_image_file(f'{DIR_IMG}/{name_image}')
        image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
        face_location = fr.face_locations(image)
        return face_location, image

    def _crop_image(self, face_location: List[Tuple], image: np.ndarray) -> Any:
        """
        Recorta a imagem.

        :param face_location: Lista de tuplas com a localização do rosto do indivíduo presente na foto
        :param image: A imagem do indivíduo.
        :return: Retorna a imagem recortada.
        """
        top, right, bottom, left = face_location[0]
        image_cropped = image[top:bottom, left:right]
        image_cropped = image_cropped[:, :, ::-1]
        return image_cropped

    def _save_change_cropped_image_in_directory(self, name_image: str, image_cropped: Any) -> None:
        """
        Salva a imagem recortada no diretório, substituindo a foto com o mesmo nome.

        :param name_image: Nome da imagem.
        :param image_cropped: Imagem recortada.
        """

        self._logger.info(f'SALVANDO {name_image} NO DIRETÓRIO...')
        image_cropped = Image.fromarray(image_cropped)
        image_cropped.save(f'{DIR_IMG}/{name_image}')

    def run(self):
        """
        Método que executa o processo de recorte da imagem.
        """
        self._logger.info('RECUPERANDO IMAGENS...')
        list_images = [f for f in os.listdir(DIR_IMG)]
        for name_image in tqdm(list_images):
            face_location, image = self._get_face_location(name_image=name_image)
            image_cropped = self._crop_image(face_location=face_location, image=image)
            self._save_change_cropped_image_in_directory(name_image=name_image, image_cropped=image_cropped)  #


if __name__ == '__main__':
    c = CropImages()
    c.run()
