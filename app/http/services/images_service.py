import os
from hashlib import md5
from app.database import ImagesRepository, BadFileException
from fastapi import UploadFile
from pydantic import BaseModel


class ImagesServices():

    def __init__(self, image_repository: ImagesRepository) -> None:
        self._repository: ImagesRepository = image_repository

    def add(self, image: UploadFile):
        self.__check_file(image)
        path = self.__save_file(image)
        file = self._repository.add(path)
        return ResponseUploadFile(
            message=f"file {image.filename} upload",
            id=file.id,
            path=file.path
        )

    def __save_file(self, image: UploadFile) -> str:
        chuck_size = 4000
        file_name = md5(image.filename.encode()).hexdigest()
        expansion = image.filename.split(".").pop()
        output_file = f"/images/user_image/{file_name}.{expansion}"
        if os.path.isfile(output_file):
            os.remove(output_file)
        file = open(f'/app/{output_file}', "wb+")
        data = image.file.read(chuck_size)
        while(data != b''):
            file.write(data)
            data = image.file.read(chuck_size)
        image.close()
        file.close()
        return output_file

    def __check_file(self, image: UploadFile):
        if image.content_type.find("image") == -1:
            raise BadFileException(
                item=image.filename,
                entity_description=f"Неверный формат файла: '{image.filename}'."
            )


class ResponseUploadFile(BaseModel):
    message: str
    id: int
    path: str
