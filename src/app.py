from flask import Flask, request, jsonify, render_template, send_from_directory, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from werkzeug.utils import secure_filename
import os
from ultralytics import YOLO
import requests

db = SQLAlchemy()

def create_app(config=None):
    app = Flask(__name__)

    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.config['UPLOAD_FOLDER'] = 'static/uploads/'
    app.config['RESULT_FOLDER'] = 'static/results/'
    os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
    os.makedirs(app.config['RESULT_FOLDER'], exist_ok=True)

    db.init_app(app)

    if config:
        app.config.update(config)

    class ApiData(db.Model):
        __tablename__ = 'api_data'
        __table_args__ = {'extend_existing': True}
        id = db.Column(db.Integer, primary_key=True)
        title = db.Column(db.String(255), nullable=False)
        completed = db.Column(db.Boolean, nullable=False)

    class UserInput(db.Model):
        __tablename__ = 'user_input'
        __table_args__ = {'extend_existing': True}
        id = db.Column(db.Integer, primary_key=True)
        user_input = db.Column(db.String(255), nullable=False)
        timestamp = db.Column(db.DateTime, default=db.func.current_timestamp())

    with app.app_context():
        db.create_all()

    model = YOLO('models/yolov10s.pt')

    @app.route('/')
    def index():
        return render_template('upload.html')

    @app.route('/upload', methods=['POST'])
    def upload():
        file = request.files['image']
        if file:
            filename = secure_filename(file.filename)
            filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            file.save(filepath)

            results = model(filepath)
            result_image_path = os.path.join(app.config['RESULT_FOLDER'], 'result_' + filename)
            results[0].save(result_image_path)

            return redirect(url_for('display_result', filename='result_' + filename))
        return 'No file uploaded', 400

    @app.route('/fetch')
    def fetch_api_data():
        try:
            response = requests.get('https://jsonplaceholder.typicode.com/todos/1')
            if response.ok:
                data = response.json()
                new_data = ApiData(title=data['title'], completed=data['completed'])
                db.session.add(new_data)
                db.session.commit()
                return jsonify(data), 200
            return jsonify({'error': 'API request failed'}), 500
        except Exception as e:
            return jsonify({'error': str(e)}), 500

    @app.route('/results/<filename>')
    def uploaded_file(filename):
        return send_from_directory(app.config['RESULT_FOLDER'], filename)

    @app.route('/result/<filename>')
    def display_result(filename):
        return render_template('result.html', image_filename=filename)

    @app.route('/history')
    def history():
        images = os.listdir(app.config['RESULT_FOLDER'])
        return render_template('history.html', images=images)

    return app

if __name__ == '__main__':
    app = create_app()
    app.run(debug=True)
