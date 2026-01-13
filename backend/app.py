from flask import Flask
from flask_cors import CORS
from flask_jwt_extended import JWTManager
from config.settings import load_config

from config.jwt import jwt

from routes.auth_routes import auth_bp
from routes.voice_routes import voice_bp
from routes.task_routes import task_bp
def create_app():
    app = Flask(__name__)
    load_config(app)
    CORS(
        app,
        resources={r"/api/*": {"origins": "http://116.202.210.102:5174"}},
        supports_credentials=True,    
        methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],     
        allow_headers=["Content-Type", "Authorization"]
    )


    jwt.init_app(app)
    

    app.register_blueprint(auth_bp, url_prefix="/api/auth")
    app.register_blueprint(voice_bp, url_prefix="/api/voice")
    app.register_blueprint(task_bp, url_prefix="/api/tasks")

    from flask import send_from_directory

    @app.route("/storage/audio_responses/<path:filename>")
    def serve_audio(filename):
        return send_from_directory("storage/audio_responses", filename,mimetype="audio/wav")


    return app

app = create_app()

if __name__ == "__main__":
    app.run(debug=True,port=5050)
