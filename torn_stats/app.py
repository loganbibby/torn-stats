from flask import Flask, g, render_template
from flask_caching import Cache


app = Flask(__name__)

app.config.from_object("torn_stats.config")

@app.route('/API')
def new_page():
  return render_template('API.html')

cache = Cache(app)

from . import views
