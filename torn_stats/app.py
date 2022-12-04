from flask import Flask, g
from flask_caching import Cache


app = Flask(__name__)

app.config.from_object("torn_stats.config")

@app.before_request
def init_request():
    g.cache = Cache(app)


from . import views
