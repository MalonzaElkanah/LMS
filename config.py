import os

from dotenv import load_dotenv


dotenv_path = os.path.join(os.path.dirname(__file__), ".env")
load_dotenv(dotenv_path)


class Config(object):
    LOG_LEVEL = "ERROR"
    SECRET_KEY = os.getenv("SECRET_KEY")

    SQLALCHEMY_DATABASE_URI = "sqlite:///library.db"
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    RATE_PER_DAY = float(os.environ.get("RATE_PER_DAY", default=20.0))
    OUTSTANDING_DEBT = float(os.environ.get("OUTSTANDING_DEBT", default=500.0))
