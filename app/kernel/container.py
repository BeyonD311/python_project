from dependency_injector import containers, providers
from pathlib import Path
from .database import Database
import app.database as DatabaseCustom
import app.http.services as services

class Container(containers.DeclarativeContainer):
    # wiring_config = containers.WiringConfiguration(packages=["app.http.controllers"])
    config = providers.Configuration(yaml_files=[Path('config.yml')])
    db = providers.Singleton(Database, db_url=config.db.uri) 
    # Service Provider
    user_repository = providers.Factory(
        DatabaseCustom.UserRepository,
        session_factory=db.provided.session,
    ) 
    user_service = providers.Factory(
        services.UserService, 
        user_repository = user_repository
    )
    dependencies_repository = providers.Factory(
        DatabaseCustom.DeparmentsRepository,
        session_factory=db.provided.session,
    )
    position_repository = providers.Factory(
        DatabaseCustom.PositionRepository,
        session_factory=db.provided.session,
    )
    groups_repository = providers.Factory(
        DatabaseCustom.GroupsRepository,
        session_factory=db.provided.session,
    )
    roles_repository = providers.Factory(
        DatabaseCustom.RolesRepository,
        session_factory=db.provided.session,
    )
    roles_service = providers.Factory(
        services.RolesServices,
        roles_repository=roles_repository
    )