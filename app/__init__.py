from flask import Flask
from flask_cors import CORS, cross_origin

def create_app():
    app = Flask(__name__)
    CORS(app)
    app.config['CORS_HEADERS'] = 'Content-Type'
    # Register blueprints here
    from app.main import bp as main_bp
    app.register_blueprint(main_bp)
    from app.users import bp as users_bp
    app.register_blueprint(users_bp, url_prefix='/users')
    from app.posts import bp as posts_bp
    app.register_blueprint(posts_bp, url_prefix='/posts')
    from app.skills import bp as skills_bp
    app.register_blueprint(skills_bp,url_prefix='/skills')

    return app