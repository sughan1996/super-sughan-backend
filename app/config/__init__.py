import os
from dotenv import load_dotenv
from app.utils.AppExceptions import AppBaseException

try:
    load_dotenv()
    environment = os.getenv('environment')
    database_environment = os.getenv('database_environment')
    log_level = os.getenv('log_level').upper()
    username = os.getenv('username')
    password = os.getenv('password')
    database_url = os.getenv('database')
except Exception as err:
    raise AppBaseException(f"Error loading environment variables: {err}")



