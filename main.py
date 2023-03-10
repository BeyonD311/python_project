from dotenv import load_dotenv, find_dotenv
from fastapi import FastAPI
from dependency_injector.wiring import register_loader_containers
from starlette.middleware.cors import CORSMiddleware
from app.http.middleware.auth_middleware import Auth
import os



find_dotenv()
load_dotenv()   

os.environ['TZ'] = os.getenv('TIME_ZONE')

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
            nameSplit = module_name.split("_")
            routes[nameSplit[0]] = module.__dict__['route']
    return routes


container = create_container()
db = container.db()
db.create_database()
app = FastAPI(debug=True)
app.container = container

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.add_middleware(Auth)

modules = import_modules_controller(container) 

for route_name in modules:
    app.include_router(modules[route_name])