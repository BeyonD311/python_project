from fastapi import Depends, APIRouter, Response
from fastapi.security import HTTPBearer
from app.http.services.queue import QueueService
from app.http.services.queue import RequestQueue
from app.http.services.queue import RequestQueueMembers
from app.http.services.queue import GetAllQueue
from app.http.services.queue import Filter
from app.http.services.queue import AddPhonesToTheQueue
from dependency_injector.wiring import inject
from dependency_injector.wiring import Provide
from app.kernel.container import Container
from app.http.services.helpers import default_error
from pydantic import ValidationError

route = APIRouter(
    prefix="/queue/statistics",
    tags=['queue'],
    responses={404: {"description": "Not found"}} 
)

security = HTTPBearer()


@route.get("/loading/{uuid}")
@inject
def loading_the_queue(
    uuid: str

):
...