import os
from fastapi import APIRouter
from fastapi import Depends
from fastapi import Response
from fastapi import status
from fastapi import UploadFile
from fastapi import File
from fastapi.security import HTTPBearer
from fastapi.responses import FileResponse
from app.http.services.images_service import ImagesServices
from app.http.services.images_service import BadFileException
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
    path = f"images/user_image/{filename}"
    if os.path.exists(path) and os.path.isfile(path):
        return FileResponse(path)
    response.status_code = status.HTTP_404_NOT_FOUND
    return {
        "message" : "Image not found"
    }

@route.post("/")
@inject
def save_file(
    # response: Response(),
    file: UploadFile = File(),
    image_services: ImagesServices = Depends(Provide[Container.image_services]),
    HTTPBearerSecurity: HTTPBearer = Depends(security)):
    try:
        return image_services.add(file)
    except BadFileException as e:
        # response.status_code = status.HTTP_400_BAD_REQUEST
        return ResponseUploadFile(
            message=str(e),
            id=0
        ) 