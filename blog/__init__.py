from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager

app = Flask(__name__)
app.config.from_object('blog.config')

db = SQLAlchemy(app)
from.models import employee, user

login_manager = LoginManager()
login_manager.init_app(app)

import blog.views