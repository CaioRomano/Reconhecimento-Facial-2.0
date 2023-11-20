import logging
import os
import time
from typing import Tuple, Any, List, Union

import cv2
import face_recognition as fr
from cv2 import VideoCapture

from src.config import TIMER, DIR_IMG


class GetImages:
    """
    Classe responsável por capturar imagens da Webcam e armazená-las numa pasta.
    """

    _logger: logging.Logger
    _image_counter: int = 0

    def __init__(self) -> None:
        """
        Método Construtor da classe.
        """

        self.img = None
        self._image_counter = self._find_img_counter()
        self._logger = logging.getLogger(__name__)

    def _find_faces(self) -> Union[bool, None]:
        """
        Verifica a existência de rostos na foto encontrada.

        :return: Retorna uma flag indicando existência de rostos na foto.
        """

        self._logger.info('PROCURANDO ROSTOS...')
        if self.img is None:
            return False
        face_locations = fr.face_locations(self.img, number_of_times_to_upsample=2)
        if not face_locations:
            self._logger.warning("NENHUM ROSTO DETECTADO")
            return False
        return True

    def _find_img_counter(self) -> int:
        """
        Cria um número identificador de imagem para armazená-la na pasta.

        :return: Número identificador de imagem .
        """

        image_counter = 0
        while os.path.exists(f"{DIR_IMG}/face_{image_counter}.jpg"):
            image_counter += 1
        return image_counter

    def _draw_circle(self, face_locations: List[Tuple], frame: Any, color: Tuple[int, int, int]) -> None:
        """
        Desenha um círculo ao redor do rosto encontrado.

        :param face_locations: Localização do rosto.
        :param frame: Frame atual na Webcam.
        :param color: Cor do círculo.
        """

        for (top, right, bottom, left) in face_locations:
            top *= 4
            right *= 4
            bottom *= 4
            left *= 4
            center_x = (left + right) // 2
            center_y = (top + bottom) // 2
            radius = (right - left) // 2

            cv2.circle(frame, (center_x, center_y), radius, color, 2)

    def _save_images(self) -> None:
        """
        Salva imagens no diretório.
        """

        num = self._image_counter
        cv2.imwrite(f"{DIR_IMG}/face_{num}.jpg", self.img)
        self._logger.info(f"ROSTO DETECTADO E SALVO EM face_{num}.jpg")

    def _process_frame(self, frame: Any) -> List[Tuple]:
        """
        Processa o frame atual na Webcam.

        :param frame: Frame atual da Webcam.
        :return: Localização dos rostos.
        """

        small_frame = cv2.resize(frame, (0, 0), fx=0.25, fy=0.25)
        rgb_small_frame = small_frame[:, :, ::-1]
        face_locations = fr.face_locations(rgb_small_frame, number_of_times_to_upsample=2)
        return face_locations

    def _recognition(self, cap: VideoCapture) -> None:
        """
        Método que realiza o reconhecimento facial.

        :param cap: Câmera da Webcam.
        """

        color = (255, 255, 255)
        start_time = time.time()
        while True:
            ret, frame = cap.read()
            if not ret:
                self._logger.error('ERRO AO CAPTURAR QUADRO DA WEBCAM')
            if time.time() - start_time > TIMER:
                self.img = frame
                break

            self.img = frame
            face_locations = self._process_frame(frame=frame)
            self._draw_circle(face_locations=face_locations, frame=frame, color=color)
            cv2.imshow('Captura', frame)
            if cv2.waitKey(1) & 0xff == 27:
                break

    def run(self) -> None:
        """
        Executa todo o processo de captura e armazenamento da imagem.
        """

        self._logger.info('INICIANDO WEBCAM...')
        cap = cv2.VideoCapture(0)
        if not cap.isOpened():
            self._logger.error('ERRO AO ABRIR WEBCAM')
            exit()

        self._recognition(cap=cap)
        cap.release()
        cv2.destroyAllWindows()
        if not self._find_faces():
            exit()
        self._save_images()


if __name__ == '__main__':
    g = GetImages()
    g.run()
