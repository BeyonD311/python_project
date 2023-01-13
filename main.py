from dotenv import load_dotenv, find_dotenv
from fastapi import FastAPI
import app.controllers as controller

find_dotenv()
load_dotenv()   

def create_app():
    import kernel
    container = kernel.Container()
    db = container.db()
    db.create_database()

    app = FastAPI(debug=True)
    app.container = container
    return app

app = create_app()

for router in controller.routes.values():
    app.include_router(router)