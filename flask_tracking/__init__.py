from flask import Flask

from .auth import login_manager
from .data import db
from .tracking.views import tracking
from .users.views import users
from .users.models import User

app = Flask(__name__)
app.config.from_object('config')


@app.context_processor
def provide_constants():
    return {"constants": {"TEST_PART_": 2}}

db.init_app(app)

login_manager.init_app(app)

app.register_blueprint(tracking)
app.register_blueprint(users)
