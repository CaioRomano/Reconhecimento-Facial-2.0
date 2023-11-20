import logging
import os
from datetime import datetime
from typing import List, Tuple
from tqdm import tqdm
import cv2
import face_recognition as fr
import numpy as np

from src.Database.execute import execute_read_table, execute_insert
from src.Database.options import EnumTables
from src.config import DIR_IMG, TOLERANCE


class VerifyFace:
    """
    Classe responsável pela eliminação de rostos já conhecidos.
    """

    _list_encodings: List[np.ndarray]
    _logger = logging.Logger

    def __init__(self) -> None:
        """
        Método Construtor da classe.
        """

        self._list_encodings = self._load_encodings()
        self._logger = logging.getLogger(__name__)

    def _order_images(self, name_image: str) -> tuple:
        """
        Ordena nome das imagens, dando preferência as imagens que não começam com "face_".

        :param name_image: Nome da imagem.
        :return: Retorna uma tupla, mostrando a ordem de precedência e o nome da imagem.
        Quanto menor o número, maior é a ordem de precedência.
        """

        if name_image.startswith("face_"):
            return 1, name_image
        else:
            return 0, name_image

    def _load_encodings(self) -> List[np.ndarray]:
        """
        Carrega os encodings dos rostos já conhecidos do Banco de Dados.

        :return: Retorna uma lista de arrays numpy, que correspondem aos encodings que cada rosto armazenado.
        """

        list_faces_encodings = execute_read_table(EnumTables.peoplefaces.value, columns=['Face_encoding'])
        list_encodings = []
        for i in range(0, len(list_faces_encodings)):
            encoding = list_faces_encodings[i][0].strip('[]').split()
            encoding = [float(elemento) for elemento in encoding]
            encoding = np.array(encoding)
            list_encodings.append(encoding)
        return list_encodings

    def _check_matching_faces(self, image: str) -> Tuple[int, np.ndarray]:
        """
        Checa se o rosto é conhecido ou não.

        :param image: Nome da imagem.
        :return: Retorna um inteiro indicando se o rosto é conhecido ou não e o encoding do rosto usado para comparação.
        """

        self._logger.info(f'CHECANDO CORRESPONDÊNCIA DE {image}...')
        image = fr.load_image_file(f'{DIR_IMG}/{image}')
        image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
        face_encoding = fr.face_encodings(image, num_jitters=10)[0]
        result = fr.compare_faces(self._list_encodings, face_encoding)
        face_dis = fr.face_distance(self._list_encodings, face_encoding)
        status = 0

        if True in result:
            best_match_index = result.index(True)
            if face_dis[best_match_index] < TOLERANCE:
                status = 1
        return status, face_encoding

    def _delete_image_from_directory(self, name_image: str) -> None:
        """
        Deleta imagens que foram reconhecias do diretório.

        :param name_image: Nome da imagem.
        """

        self._logger.info(f'DELETANDO {name_image} DO DIRETÓRIO...')
        os.remove(f'{DIR_IMG}/{name_image}')

    def _add_to_table(self, image: str, face_encoding: np.ndarray) -> None:
        """
        Adiciona as informações na tabela do Banco de Dados.

        :param image: Nome da imagem.
        :param face_encoding: Encoding do rosto usado para a comparação.
        """

        name = image.split('.')[0]
        date_creation = datetime.now().strftime('%d/%m/%Y %H:%m:%S')
        type_face = 'UNKNOWN'

        if 'face_' not in name:
            type_face = 'KNOWN'

        self._logger.info('ADICIONANDO DADOS NA TABELA...')
        execute_insert(table=EnumTables.peoplefaces.value, name=name, type_face=type_face, face_encoding=face_encoding,
                       date_creation=date_creation)

    def run(self) -> None:
        """
        Método que executa o processo de verificação dos rostos.
        """

        self._logger.info('INICIANDO RECUPERAÇÃO...')

        list_images = sorted([f for f in os.listdir(DIR_IMG)], key=self._order_images)

        for image in tqdm(list_images):
            status, face_encoding = self._check_matching_faces(image=image)
            if status:
                self._logger.info(f'FOTO {image} RECONHECIDA')
                self._delete_image_from_directory(name_image=image)
                continue
            self._logger.info(f'FOTO {image} NÃO RECONHECIDA')
            self._add_to_table(image=image, face_encoding=face_encoding)
            self._list_encodings = self._load_encodings()


if __name__ == '__main__':
    v = VerifyFace()
    v.run()
