from flask import Flask, render_template, request, redirect, session, url_for, flash
from models import db
from auth.routes import auth_bp
from tools.pingtool.routes import ping_bp
from tools.nmap.routes import nmap_bp

app = Flask(__name__)
app.secret_key = 'your_secret_key'

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///cyberdash.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db.init_app(app)

# Register blueprints
app.register_blueprint(auth_bp)
app.register_blueprint(ping_bp)
app.register_blueprint(nmap_bp)

@app.route('/')
def index():
    if 'username' in session:
        return redirect(url_for('auth.dashboard'))
    return redirect(url_for('auth.login'))

if __name__ == '__main__':
    app.run(debug=True)
