from dotenv import load_dotenv, find_dotenv
from fastapi import FastAPI
from dependency_injector.wiring import register_loader_containers
from pathlib import Path
import pkgutil

find_dotenv()
load_dotenv()   

def create_app():
    from app.kernel import Container
    container = Container()
    db = container.db()
    db.create_database()
    app = FastAPI(debug=True)
    app.container = container
    return app, container

def import_modules_controller(container):
    register_loader_containers(container)
    routes = {}
    for loader, module_name, is_pkg in pkgutil.walk_packages(['/app/./app/http/controllers']):
        module = loader.find_module(module_name).load_module(module_name)
        if 'route' in module.__dict__:
            routes[module_name] = module.__dict__['route']
    return routes

app, container = create_app()

modules = import_modules_controller(container)
print(modules)
for moduleName in modules:
    route = modules[moduleName]
    app.include_router(route)