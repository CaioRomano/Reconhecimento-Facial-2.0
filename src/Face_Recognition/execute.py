from src.Face_Recognition.FaceRecognition import FaceRecognition


def execute_face_recognition() -> None:
    """
    Executa o reconhecimento facial.
    """

    obj = FaceRecognition()
    obj.run()
