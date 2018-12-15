from flask import Blueprint

index_blue = Blueprint('index', __name__)

import info.moduels.index.views
