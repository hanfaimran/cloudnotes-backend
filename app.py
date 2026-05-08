from flask import Flask
from flask_cors import CORS
from config import Config
from extensions import db
from routes.auth import auth_bp
from routes.notes import notes_bp
from dotenv import load_dotenv
import os

load_dotenv()

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    allowed_origins = [
        "http://localhost:3000",
        "http://127.0.0.1:5500",
        "http://localhost:5500",
        "https://stickynotesz.netlify.app",
        "https://heroic-mousse-f1e162.netlify.app",
    ]

    CORS(app,
         supports_credentials=True,
         origins=allowed_origins,
         allow_headers=["Content-Type", "Authorization"],
         methods=["GET", "POST", "PUT", "DELETE", "PATCH", "OPTIONS"]
    )

    db.init_app(app)

    app.register_blueprint(auth_bp, url_prefix="/api/auth")
    app.register_blueprint(notes_bp, url_prefix="/api/notes")

    with app.app_context():
        db.create_all()

    return app

if __name__ == "__main__":
    app = create_app()
    app.run(debug=True, port=5000)
