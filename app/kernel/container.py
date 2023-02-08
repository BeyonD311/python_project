from dependency_injector import containers, providers
from pathlib import Path
from .database import Database
import app.database as DatabaseCustom
import app.http.services as services
from .redis import init_redis_pool
from app.http.services import JwtManagement


class Container(containers.DeclarativeContainer):
    # wiring_config = containers.WiringConfiguration(packages=["app.http.controllers"])
    config = providers.Configuration(yaml_files=[Path('config.yml')])
    db = providers.Singleton(Database, db_url=config.db.uri) 
    # Service Provider

    redis_pool = providers.Resource(
        init_redis_pool,
        host="redis:6379",
        password=""
    )

    jwt = providers.Factory(
        JwtManagement,
        redis_pool
    )
    
    user_repository = providers.Factory(
        DatabaseCustom.UserRepository,
        session_factory=db.provided.session,
    ) 
    roles_permission = providers.Factory(
        DatabaseCustom.RolesPermissionRepository,
        session_factory=db.provided.session
    )
    roles_permission_service = providers.Factory(
        services.RolesPermission,
        roles_repository = roles_permission
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