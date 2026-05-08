from flask import Flask, request, jsonify
from config import Config
from extensions import db
from routes.auth import auth_bp
from routes.notes import notes_bp
from dotenv import load_dotenv

load_dotenv()

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    db.init_app(app)

    app.register_blueprint(auth_bp, url_prefix="/api/auth")
    app.register_blueprint(notes_bp, url_prefix="/api/notes")

    @app.after_request
    def add_cors_headers(response):
        origin = request.headers.get("Origin", "")
        allowed = [
            "https://stickynotesz.netlify.app",
            "https://heroic-mousse-f1e162.netlify.app",
            "http://localhost:3000",
            "http://127.0.0.1:5500",
        ]
        if origin in allowed:
            response.headers["Access-Control-Allow-Origin"] = origin
        response.headers["Access-Control-Allow-Credentials"] = "true"
        response.headers["Access-Control-Allow-Methods"] = "GET, POST, PUT, DELETE, PATCH, OPTIONS"
        response.headers["Access-Control-Allow-Headers"] = "Content-Type, Authorization"
        return response

    @app.before_request
    def handle_options():
        if request.method == "OPTIONS":
            response = jsonify({})
            response.status_code = 200
            return response

    with app.app_context():
        db.create_all()

    return app

if __name__ == "__main__":
    app = create_app()
    app.run(debug=True, port=5000)
