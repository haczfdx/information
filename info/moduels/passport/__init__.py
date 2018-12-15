from flask import Blueprint

passport_blue = Blueprint('passport', __name__)

import info.moduels.passport.views
