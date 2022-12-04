from flask import Flask, g
from flask_caching import Cache


app = Flask(__name__)

app.config.from_object("torn_stats.config")

cache = Cache(app)

from . import views
