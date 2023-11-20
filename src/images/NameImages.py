import logging
import re

import click
import numpy as np
from tqdm import tqdm
from src.config import DIR_IMG
import os
import easyocr as ocr
import cv2
from typing import List, Tuple, Union, Any


class NameImages:
    """
    Classe responsável por nomear as imagens armazenadas pela classe GetImages
    """

    _logger: logging.Logger
    _reader = ocr.Reader
    _RE_PATTERN: re.Pattern

    def __init__(self, gpu: bool = False) -> None:
        """
        Método Construtor da classe

        :param gpu: Flag indicando uso da GPU
        """

        self._logger = logging.getLogger(__name__)
        self._reader = ocr.Reader(['pt'], gpu=gpu)
        self._RE_PATTERN = re.compile(r'[!@#$%^&*()_+{}\[\]:;<>,.?/\\|`~-]+$')

    def _remove_special_character(self, text: str) -> str:
        """
        Remove caracteres especiais na string.

        :param text: Texto identificado pelo OCR.
        :return: Nova string sem caracteres especiais.
        """

        text = re.sub(self._RE_PATTERN, '', text)
        return text

    def _read_text_from_images(self, image: np.ndarray) -> Union[Any, bool]:
        """
        Identifica o texto presente na imagem.

        :param image: Imagem usada para identificar o texto.
        :return: Retorna o texto que foi identificado pelo OCR,
        se nada for encontrado, então o método retornará uma flag indicando inexistência de texto.
        """
        self._logger.info('IDENTIFICANDO TEXTO...')
        result = self._reader.readtext(image, batch_size=2)
        return result if len(result) else False

    def _write_text_on_image(self, bbox, text: str) -> Tuple[int, int]:
        """
        Delimita a caixa delimitadora e a posição do texto na imagem.

        :param bbox: Caixa delimitadora dos textos.
        :param text: Texto identificado pelo OCR.
        :return: posições do texto e da caixa delimitadora.
        """

        (left, top), (_, _), (right, bottom), (_, _) = bbox
        center_x = (left + right) // 2
        top_text = top - 10
        (width, height), _ = cv2.getTextSize(text, cv2.FONT_HERSHEY_DUPLEX, 0.8, 2)
        x = center_x - height // 2

        return x, top_text

    def _display_image(self, image: np.ndarray, result: Any) -> List[str]:
        """
        Mostra a imagem no monitor.

        :param image: Imagem usada para identificar o texto.
        :param result: Tupla mostrando a caixa delimitadora, texto e probabilidade.
        :return: Retorna o texto encontrado.
        """

        list_text_result = []
        for (bbox, text, probabilidade) in result:
            cv2.rectangle(image, (int(bbox[0][0]), int(bbox[0][1])), (int(bbox[2][0]), int(bbox[2][1])), (0, 255, 0),
                          2)

            x, y = self._write_text_on_image(bbox, text)
            text = self._remove_special_character(text)

            cv2.putText(image, f'{text} - {round(probabilidade, 2)}%', (x, y), cv2.FONT_HERSHEY_SIMPLEX, 0.8,
                        (0, 255, 0), 2, cv2.LINE_AA)
            list_text_result.append(text)

        cv2.imshow("Texto Detectado", image)
        k = cv2.waitKey(0)
        if k == ord('q') or k == 27:
            cv2.destroyAllWindows()
            return list_text_result

    def _rename_images(self, name_image: str, new_name_image: str) -> None:
        """
        Renomeia a imagem

        :param name_image: Nome da imagem
        :param new_name_image: Novo nome da imagem
        """

        try:
            self._logger.info(f'RENOMENANDO {name_image} para {new_name_image}')
            name_image, extension = name_image.split('.')
            os.rename(f'{DIR_IMG}/{name_image}.{extension}', f'{DIR_IMG}/{new_name_image}.{extension}')
        except OSError as e:
            self._logger.error('ERRO DURANTE A RENOMEAÇÃO DAS IMAGENS')
            self._logger.exception(f'EXCEÇÃO: {e}')

    def _is_name_correct(self, list_result_text: List[str]) -> str:
        """
        Permite alteração do exto encontrado

        :param list_result_text: Lista dos textos encontrados
        :return: Retorna o texto modificado
        """

        list_text = []
        self._logger.info('ALTERANDO TEXTO ENCONTRADO...')

        for text in list_result_text:
            click.echo('Caso esteja satisfeito com o texto detectado, aperte a tecla "enter"!')
            response = click.prompt(f'Deseja alterar texto detectado?\n\t{text}', default='', show_default=False)
            list_text.append(response if len(response) else text)
        text = self._format_new_name(list_text)
        return text

    def _format_new_name(self, list_text: List[str]) -> str:
        """
        Realiza a formatação da string, ou strings, encontradas pelo OCR.

        :param list_text: Lista de textos encontrados pelo OCR.
        :return: Junta todos os textos encontrados numa única string.
        """

        click.echo('Caso esteja satisfeito com o texto, aperte a tecla "enter"!')
        text = ' '.join(list_text)
        response = click.prompt(f'Deseja alterar texto detectado?\n\t{text}', default='', show_default=False)
        return response.title() if len(response) else text.title()

    def run(self) -> None:
        """
        Executa  o processo de nomeação das imagens.
        """
        self._logger.info('RECUPERANDO IMAGENS...')
        list_images = [f for f in os.listdir(DIR_IMG) if f.lower().startswith('face_')]
        num = 1
        for name_image in tqdm(list_images, desc='PROCESSANDO IMAGENS...'):
            image = cv2.imread(f'{DIR_IMG}/{name_image}')
            result = self._read_text_from_images(image=image)
            if isinstance(result, bool):
                continue
            list_result_text = self._display_image(image=image, result=result)
            text = self._is_name_correct(list_result_text)
            self._rename_images(name_image=name_image, new_name_image=text)
            num += 1


if __name__ == '__main__':
    m = NameImages()
    m.run()
