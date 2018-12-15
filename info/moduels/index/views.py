from . import index
from flask import render_template

@index.route("/")
def index():

    return render_template('news/index.html')
