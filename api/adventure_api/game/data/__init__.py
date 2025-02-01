import os
import importlib
import pathlib
import logging

logger = logging.getLogger(__name__)

LOCAL_PATH = pathlib.Path(__file__).parent

def load_path(pathname: str):
    for root, _, files in os.walk(os.path.join(LOCAL_PATH, pathname)):
        for file in files:
            if file.endswith('.py'):
                path = os.path.join(root, file)[len(str(LOCAL_PATH)):]
                path = path.replace(os.path.sep, '.')
                path = path.replace('.py', '')
                logging.info(f'loaded data from {path}')
                importlib.import_module(path, package=__package__)

def load_data():
    """Loads data from local entities/**/* folders"""
    load_path('entities')
    load_path('items')
