import os
from dotenv import load_dotenv
from datetime import timedelta

def load_config(app):
    load_dotenv()
    app.config["SECRET_KEY"] = os.getenv("SECRET_KEY")
    app.config["JWT_SECRET_KEY"] = os.getenv("JWT_SECRET_KEY")
    app.config["MONGO_URI"] = os.getenv("MONGO_URI")
    app.config["JWT_ACCESS_TOKEN_EXPIRES"] = timedelta(days=7)
