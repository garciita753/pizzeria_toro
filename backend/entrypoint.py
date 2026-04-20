import os
from dotenv import load_dotenv

# load environment variables from a .env file if present
load_dotenv()

from app import create_app

settings_module = os.getenv('APP_SETTINGS_MODULE')
app = create_app(settings_module)