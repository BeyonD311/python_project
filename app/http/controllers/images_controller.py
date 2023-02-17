import os
from fastapi import APIRouter, Depends, Response, status
from fastapi.security import HTTPBearer
from fastapi.responses import FileResponse

route = APIRouter(
    prefix="/images",
    tags=['images'],
    responses={404: {"description": "Not found"}},
    include_in_schema=False
)

security = HTTPBearer()

@route.get("/user_image/{filename}")
def get_file(
    filename: str,
    response: Response,
    HTTPBearerSecurity: HTTPBearer = Depends(security)):
    path = f"images/user_image/{filename}"
    if os.path.exists(path) and os.path.isfile(path):
        return FileResponse(path)
    response.status_code = status.HTTP_404_NOT_FOUND
    return {
        "message" : "Image not found"
    }