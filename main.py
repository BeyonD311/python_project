from dotenv import load_dotenv, find_dotenv
from fastapi import FastAPI, Depends
from dependency_injector.wiring import register_loader_containers, inject, Provide
from starlette.middleware.cors import CORSMiddleware
from app.http.middleware.auth_middleware import Auth
from app.http.services.users.users_service import UserService
import os, time
find_dotenv()
load_dotenv()   

os.environ['TZ'] = os.getenv('TIME_ZONE')
time.tzset()

def create_container():
    from app.kernel import Container
    container = Container()
    return container

def import_modules_controller(container):
    import pkgutil
    register_loader_containers(container)
    routes = {}
    for loader, module_name, is_pkg in pkgutil.walk_packages(['/app/./app/http/controllers']):
        module = loader.find_module(module_name).load_module(module_name)
        if 'route' in module.__dict__:
            routes[module_name] = module.__dict__['route'] 
    return routes


container = create_container()
db = container.db()
asterisk = container.asterisk()
db.create_database()
app = FastAPI(debug=True)
app.container = container

origins = [
    "https://localhost.tiangolo.com",
    "http://localhost",
    "http://localhost:8010",
    "http://10.3.0.48:8010",
    "http://10.3.0.48:3001",
    "http://localhost:3000",
    "http://127.0.0.1:3000"
    "http://app"
]
app.add_middleware(Auth)
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.add_middleware(Auth)

modules = import_modules_controller(container)

for route_name in modules:
    app.include_router(modules[route_name])


@app.on_event("startup")
async def start():
    user_service = await container.user_service()
    await user_service.add_status_to_redis()
    await user_service.all()
    await user_service.add_status_user_to_redis()