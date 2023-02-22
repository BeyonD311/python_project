import os
from app.database import ImagesRepository
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
            id=file.id
        )
    
    def __save_file(self, image: UploadFile) -> str:
        chuck_size = 4000
        file_name = image.filename.replace(" ", "_")
        output_file = f"/images/user_image/{file_name}"
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
            raise BadFileException(image.filename + " is not image ")

class BadFileException(Exception):
    def __init__(self, file: str) -> None:
        super().__init__(f"bad file: {file}")

class ResponseUploadFile(BaseModel):
    message: str
    id: int