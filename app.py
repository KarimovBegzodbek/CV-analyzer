from flask import Flask, request, session
from config import Config
from extensions import db, bcrypt, login_manager, csrf, babel, mail

def get_locale():
    # if a user is logged in, use the locale from the user settings
    return session.get('lang', request.accept_languages.best_match(Config.LANGUAGES))

def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)

    # Initialize Flask extensions here
    db.init_app(app)
    bcrypt.init_app(app)
    login_manager.init_app(app)
    csrf.init_app(app)
    babel.init_app(app, locale_selector=get_locale)
    mail.init_app(app)

    # Register blueprints here
    from routes.main import main as main_bp
    app.register_blueprint(main_bp)

    from routes.auth import auth as auth_bp
    app.register_blueprint(auth_bp, url_prefix='/auth')

    # Ensure database is created
    with app.app_context():
        db.create_all()

    return app

if __name__ == '__main__':
    app = create_app()
    app.run(debug=True)
