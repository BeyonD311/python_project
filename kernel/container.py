from dependency_injector import containers, providers
from pathlib import Path
from .endpoints import modules
from .database import Database
import database
import app.services as services

class Container(containers.DeclarativeContainer):
    wiring_config = containers.WiringConfiguration(modules=modules)
    config = providers.Configuration(yaml_files=[Path('config.yml')])
    db = providers.Singleton(Database, db_url=config.db.uri) 
    
    # Service Provider
    user_repository = providers.Factory(
        database.UserRepository,
        session_factory=db.provided.session,
    )

    user_service = providers.Factory(
        services.UserService,
        user_repository = user_repository
    )