import os
from fastapi import APIRouter
from fastapi import Depends
from fastapi import Response
from fastapi.security import HTTPBearer
from fastapi.responses import FileResponse
from app.database.repository import NotFoundError
from app.http.services.helpers import default_error
from dependency_injector.wiring import inject

route = APIRouter(
    prefix="/audio",
    tags=['audio'],
    responses={404: {"description": "Not found"}}
)

security = HTTPBearer()

@route.get("/call_audio/{filename}")
@inject
def get_file(
    filename: str,
    response: Response,
    HTTPBearerSecurity: HTTPBearer = Depends(security)):
    """
    Exceptions:
        NotFoundError
    """
    local_path_file = os.getenv('LOCAL_PATH_FILECALL')
    path = f"{local_path_file}/{filename}"
    try:
        if os.path.exists(path) and os.path.isfile(path):
            result = FileResponse(path)
        else:
            description = f"Не найдено аудио файла с именем '{filename}'"
            raise NotFoundError(item=filename, entity_description=description)
    except Exception as e:
        err = default_error(e, source='Audio')
        response.status_code = err[0]
        result = err[1]
    return result
