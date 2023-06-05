from dependency_injector import containers, providers
from pathlib import Path
from .database import Database
import app.database as DatabaseCustom
from app.http.services.users import UserService
from app.http.services.users import SkillService
from app.http.services.roles import RolesPermission
from app.http.services.groups import GroupsService
from app.http.services.roles import RolesServices
from app.http.services.departments import DepartmentsService
from app.http.services.images_service import ImagesServices
from app.http.services.inner_phone import InnerPhoneServices
from app.http.services.schedule.schedule import ScheduleService
from app.http.services.analytics.analytics import AnalyticsService
from app.http.services.queue import QueueService
from .redis import init_redis_pool
from app.http.services.jwt_managment import JwtManagement
from app.http.services.helpers import RedisInstance
from app.http.services.ssh import Ssh


class Container(containers.DeclarativeContainer):
    wiring_config = containers.WiringConfiguration(modules=['app.http.middleware.auth_middleware'])
    config = providers.Configuration(yaml_files=[Path('config.yml')])
    db = providers.Singleton(Database, db_url=config.db.uri, echo=False)
    asterisk = providers.Singleton(Database, db_url=config.asterisk.uri, echo=True)
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
    redis_instance = providers.Factory(
        RedisInstance,
        redis_pool
    )
    user_repository = providers.Factory(
        DatabaseCustom.UserRepository,
        session_factory=db.provided.session,
        session_asterisk=asterisk.provided.session
    )
    skills_repository = providers.Factory(
        DatabaseCustom.SkillsRepository,
        session_factory=db.provided.session,
    )
    roles_permission = providers.Factory(
        DatabaseCustom.RolesPermissionRepository,
        session_factory=db.provided.session
    )
    roles_permission_service = providers.Factory(
        RolesPermission,
        roles_repository=roles_permission
    )
    user_service = providers.Factory(
        UserService,
        user_repository=user_repository,
        redis=redis_instance,
    )
    skill_service = providers.Factory(
        SkillService,
        skill_repository=skills_repository
    )
    dependencies_repository = providers.Factory(
        DatabaseCustom.DepartmentsRepository,
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
    groups_service = providers.Factory(
        GroupsService,
        groups_repository=groups_repository
    )
    roles_repository = providers.Factory(
        DatabaseCustom.RolesRepository,
        session_factory=db.provided.session,
    )
    roles_service = providers.Factory(
        RolesServices,
        roles_repository=roles_repository
    )
    department_repository = providers.Factory(
        DatabaseCustom.DepartmentsRepository,
        session_factory=db.provided.session,
    )
    department_service = providers.Factory(
        DepartmentsService,
        repository=department_repository
    )
    image_repository = providers.Factory(
        DatabaseCustom.ImagesRepository,
        session_factory=db.provided.session
    )
    image_services = providers.Factory(
        ImagesServices,
        image_repository=image_repository
    )
    inner_phone_repository = providers.Factory(
        DatabaseCustom.InnerPhones,
        session_factory=db.provided.session,
        session_asterisk=asterisk.provided.session,
        asterisk_host=config.asterisk.host,
        asterisk_port=config.asterisk.port
    )
    asterisk_repository = providers.Factory(
        DatabaseCustom.Asterisk,
        session_asterisk = asterisk.provided.session
    )
    inner_phone_service = providers.Factory(
        InnerPhoneServices,
        inner_phone_repository=inner_phone_repository
    )
    schedule_repository = providers.Factory(
        DatabaseCustom.ScheduleRepository,
        session_asterisk=asterisk.provided.session
    )
    schedule_service = providers.Factory(
        ScheduleService,
        schedule_repository=schedule_repository
    )

    ssh = providers.Factory(
        Ssh,
         host = config.asterisk_ssh.host,  
         port = config.asterisk_ssh.port,  
         user = config.asterisk_ssh.user,
         password = config.asterisk_ssh.password
    )

    queue_service = providers.Factory(
        QueueService,
        position_repository = position_repository,
        asterisk = asterisk_repository,
        inner_phones = inner_phone_repository,
        redis = redis_instance,
        hyperscript_uri = config.hyperscript.uri,
        ssh=ssh
    )

    analytics_repository = providers.Factory(
        DatabaseCustom.AnalyticsRepository,
        session_asterisk=asterisk.provided.session
    )

    analytics_service = providers.Factory(
        AnalyticsService,
        analytics_repository=analytics_repository,
        inner_phone_repository=inner_phone_repository,
        user_repository=user_repository,
        disposal_statuses=config.analytics.disposal,
        ant_statuses=config.analytics.ant,
        call_dispositions=config.analytics.call
    )