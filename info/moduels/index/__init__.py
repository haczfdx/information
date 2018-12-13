from flask import Blueprint

index = Blueprint('index', __name__)

import info.moduels.index.views
