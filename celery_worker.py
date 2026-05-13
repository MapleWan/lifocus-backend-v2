from dotenv import load_dotenv
load_dotenv()

from app.app import app  # noqa: E402, F401
from app.extension import celery_app  # noqa: E402, F401
