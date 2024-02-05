from fastapi import FastAPI
import pkgutil
import importlib
from typing import Iterable

app = FastAPI()

def import_routers(package: str) -> Iterable:
    """
    Dynamically import routers from a package and return an iterable of routers.
    """
    package = importlib.import_module(package)
    for _, name, is_pkg in pkgutil.iter_modules(package.__path__):
        if not is_pkg:
            module = importlib.import_module(f"{package.__name__}.{name}")
            yield getattr(module, 'router', None)

# Automatically include routers from all controllers
for router in import_routers('app.controllers'):
    if router:
        app.include_router(router)
