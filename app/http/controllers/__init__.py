
# import pkgutil
# routes = {}
# """ Используется для автоматического подключения контроллеров """
# for loader, module_name, is_pkg in pkgutil.walk_packages(__path__):
#         mod = loader.find_module(module_name).load_module(module_name)
#         if 'route' in mod.__dict__:
#                 routes[module_name] = mod.__dict__['route']

# __all__ = ["routes"]

 