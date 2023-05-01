import os
from fastapi import APIRouter
from fastapi import Depends
from fastapi import Response
from fastapi import status
from fastapi import UploadFile
from fastapi import File
from fastapi.security import HTTPBearer
from fastapi.responses import FileResponse
from app.database.repository import NotFoundError
from app.http.services.helpers import default_error
from app.http.services.images_service import ImagesServices
from app.http.services.images_service import ResponseUploadFile
from app.kernel import Container
from dependency_injector.wiring import Provide
from dependency_injector.wiring import inject

route = APIRouter(
    prefix="/images",
    tags=['images'],
    responses={404: {"description": "Not found"}}
)

security = HTTPBearer()

@route.get("/user_image/{filename}", include_in_schema=False)
def get_file(
    filename: str,
    response: Response):
    """
    Exceptions:
        NotFoundError
    """
    path = f"images/user_image/{filename}"
    try:
        if os.path.exists(path) and os.path.isfile(path):
            result = FileResponse(path)
        else:
            description = f"Не найдено изображение с именем '{filename}'"
            raise NotFoundError(item=filename, entity_description=description)
    except Exception as e:
        err = default_error(e, source='Image')
        response.status_code = err[0]
        result = err[1]
    return result


@route.post("/")
@inject
def save_file(
    response: Response,
    file: UploadFile = File(),
    image_services: ImagesServices = Depends(Provide[Container.image_services]),
    HTTPBearerSecurity: HTTPBearer = Depends(security)):
    """
    Exceptions:
        BadFileException
    """
    try:
        result = image_services.add(file)
    except Exception as e:
        err = default_error(e, source='Image')
        response.status_code = err[0]
        result = err[1]
    return result
