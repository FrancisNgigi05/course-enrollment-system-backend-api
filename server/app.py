from flask import Flask
from config import Config
from flask_migrate import Migrate
from models import db

app = Flask(__name__)
app.config.from_object(Config)
migrate = Migrate(app, db)

db.init_app(app)