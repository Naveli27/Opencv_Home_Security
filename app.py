from flask import Flask
from models import db
import threading
from camera_security import run_security_camera

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///ai_security.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db.init_app(app)

first_request_initialized = False

def initialize_app():
    global first_request_initialized
    with app.app_context():
        db.create_all()
    threading.Thread(target=run_security_camera, daemon=True).start()
    first_request_initialized = True

@app.route('/')
def index():
    global first_request_initialized
    if not first_request_initialized:
        initialize_app()
    return "AI Security System is Running. Camera feed and logging active."

if __name__ == '__main__':
    app.run(debug=True)