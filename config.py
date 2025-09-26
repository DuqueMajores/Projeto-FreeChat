import os

class Config:
    SECRET_KEY = os.environ.get("SECRET_KEY") or "uma-chave-secreta-muito-dificil"
    SQLALCHEMY_DATABASE_URI = os.environ.get("DATABASE_URL") or "postgresql://freechat_db_user:MGsjJYsoxLNYpUnzmHmJdjowedZmnsOl@dpg-d3bbjjbe5dus73ce46dg-a.oregon-postgres.render.com/freechat_db"
    SQLALCHEMY_TRACK_MODIFICATIONS = False

