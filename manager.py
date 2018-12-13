from flask import Flask
from config import Config
from flask_sqlalchemy import SQLAlchemy
from flask_script import Manager
from flask_wtf import CSRFProtect

app = Flask(__name__)

app.config.from_object(Config)

CSRFProtect(app)

db = SQLAlchemy(app)



manager = Manager(app)

@app.route("/")
def index():
    return "hello world"


if __name__ == '__main__':
    manager.run()
