import os

from flask import Flask
import json 

configfile = None
with open('config.json', 'r') as f:
    configfile = json.load(f)

UPLOAD_FOLDER = configfile['UPLOAD_FOLDER'] if configfile['UPLOAD_FOLDER'] else "file_library"
ALLOWED_EXTENSIONS = configfile['ALLOWED_EXTENSIONS'] if configfile['ALLOWED_EXTENSIONS'] else {'gif'}

def create_app(test_config=None):
    # create and configure the app
    app = Flask(__name__, instance_relative_config=True)
    app.config.from_mapping(
        SECRET_KEY=configfile['SECRET_KEY'] if configfile['SECRET_KEY'] else 'dev',
        DATABASE=os.path.join(app.instance_path, 'flaskr.sqlite'),
        UPLOAD_FOLDER=UPLOAD_FOLDER,
    )

    if test_config is None:
        # load the instance config, if it exists, when not testing
        app.config.from_pyfile('config.py', silent=True)
    else:
        # load the test config if passed in
        app.config.from_mapping(test_config)

    # ensure the instance folder exists
    try:
        os.makedirs(app.instance_path)
    except OSError:
        pass
    try:
        os.makedirs("flaskr/"+UPLOAD_FOLDER)
    except OSError:
        pass

    # a simple page that says hello
    @app.route('/hello')
    def hello():
        return 'Hello, World!'


    from . import db
    db.init_app(app)

    from . import auth
    app.register_blueprint(auth.bp)
    from . import library
    app.register_blueprint(library.bp)
    app.add_url_rule('/', endpoint='index')


    return app


