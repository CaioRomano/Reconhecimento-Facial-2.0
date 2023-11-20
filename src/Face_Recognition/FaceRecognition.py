import logging
from typing import Tuple, Any, List, Union

import cv2
import face_recognition as fr
import numpy as np

from src.Database.execute import execute_read_table
from src.Database.options import EnumTables
from src.config import TOLERANCE


class FaceRecognition:
    """
    Classe responsável pelo Reconhecimento Facial.
    """

    _logger: logging.Logger
    _list_known_encodes: list
    _list_class_names: list
    _model: str

    def __init__(self, gpu: bool = False) -> None:
        """
        Método Construtor da classe.

        :param gpu: Flag indicando necessidade de uso da GPU.
        """

        self._list_known_encodes, self._list_class_names = [], []
        self._model = 'cnn' if gpu else 'hog'
        self._logger = logging.getLogger(__name__)

    def _load_ClassNames_FaceEncodings(self) -> None:
        """
        Carrega os class_names e face_encodings de cada rosto armazenado no Banco de Dados.
        """

        result = execute_read_table(
            table=EnumTables.peoplefaces.value,
            columns=['Nome', 'Face_encoding']
        )
        for i in range(0, len(result)):
            self._list_class_names.append(result[i][0])
            encoding = result[i][1].strip('[]').split()
            encoding = [float(elemento) for elemento in encoding]
            encoding = np.array(encoding)
            self._list_known_encodes.append(encoding)

    def _recognition(self, frame: Any, faces_locations: list, faces_encodings: list, faces_names: list) -> tuple[
        list[Union[str, Any]], Any, list[tuple[int, int, int]]]:
        """
        Realiza o reconhecimento do rosto em tempo real na Webcam.

        :param frame: Frame atual na Câmera da Webcam.
        :param faces_locations: Lista com a localização dos rostos das pessoas.
        :param faces_encodings: Lista com o encoding dos rostos das pessoas.
        :param faces_names: Listas com o nome das pessoas.
        :return: Uma tupla com a lista do nome das pessoas, localização do rosto das pessoas e a cor da caixa e texto.
        """

        small_frame = cv2.resize(frame, (0, 0), fx=0.25, fy=0.25)
        rgb_small_frame = small_frame[:, :, ::-1]
        faces_locations = fr.face_locations(rgb_small_frame, number_of_times_to_upsample=2, model=self._model)
        faces_encodings = fr.face_encodings(rgb_small_frame, faces_locations, num_jitters=2)
        face_colors = [(0, 0, 255)] * len(faces_locations)

        faces_names = []
        for i, face_encoding in enumerate(faces_encodings):
            matches = fr.compare_faces(self._list_known_encodes, face_encoding, tolerance=TOLERANCE)
            name = 'UNKNOWN'

            face_distance = fr.face_distance(self._list_known_encodes, face_encoding)
            best_match_index = np.argmin(face_distance)
            if matches[best_match_index]:
                name = self._list_class_names[best_match_index]
                face_colors[i] = (0, 255, 0)
                self._logger.info(f'ROSTO DE {name} DETECTADO')
            faces_names.append(name)
        return faces_names, faces_locations, face_colors

    def _display_result(self, frame: Any, faces_locations: Any, faces_names: Union[str, Any],
                        faces_colors: List[Tuple[int, int, int]]) -> None:
        """
        Mostra os resultados no monitor.

        :param frame: Frame atual da Câmera da Webcam.
        :param faces_locations: Lista com a localização do rosto das pessoas.
        :param faces_names: Lista com o nome das pessoas.
        :param faces_colors: Cor indicando se a pessoa é conhecida ou desconhecida.
        """

        for (top, right, bottom, left), name, color in zip(faces_locations, faces_names, faces_colors):
            top *= 4
            right *= 4
            bottom *= 4
            left *= 4
            center_x = (left + right) // 2
            center_y = (top + bottom) // 2
            radius = (right - left) // 2

            cv2.circle(frame, (center_x, center_y), radius, color, 2)

            font = cv2.FONT_HERSHEY_DUPLEX
            (text_width, text_height), _ = cv2.getTextSize(name, font, 1.0, 1)
            text_x = center_x - text_width // 2
            text_y = center_y - (radius + 5)

            cv2.putText(frame, f'{name}', (text_x, text_y), font, 1.0, (255, 255, 255), 2)

    def run(self) -> None:
        """
        Método principal que realiza os procedimentos para o reconhecimento facial.
        """

        self._logger.info('ABRINDO WEBCAM...')
        video_capture = cv2.VideoCapture(0)
        if not video_capture.isOpened():
            self._logger.warning('ERRO AO ABRIR A WEBCAM')
            exit()

        self._load_ClassNames_FaceEncodings()

        faces_locations, faces_encodings, faces_names, faces_colors = [], [], [], []
        process_this_frame = True
        self._logger.info('INICIANDO RECONHECIMENTO FACIAL...')
        while 1:
            ret, frame = video_capture.read()
            if process_this_frame:
                faces_names, faces_locations, faces_colors = self._recognition(frame=frame,
                                                                               faces_locations=faces_locations,
                                                                               faces_encodings=faces_encodings,
                                                                               faces_names=faces_names)
            process_this_frame = not process_this_frame

            self._display_result(frame=frame, faces_locations=faces_locations, faces_names=faces_names,
                                 faces_colors=faces_colors)
            cv2.imshow('Video', frame)
            if cv2.waitKey(1) & 0xff == 27:
                break

        video_capture.release()
        cv2.destroyAllWindows()


if __name__ == '__main__':
    f = FaceRecognition()
    f.run()
