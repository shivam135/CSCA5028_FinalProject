from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
import requests

app = Flask(__name__)

# Configure the SQLAlchemy part
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///data.db'  # Adjust this path as needed
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

# Define a data model for API data
class ApiData(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(255), nullable=False)
    completed = db.Column(db.Boolean, nullable=False)

# Define a data model for storing user inputs
class UserInput(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_input = db.Column(db.String(255), nullable=False)
    timestamp = db.Column(db.DateTime, default=db.func.current_timestamp())

# Initialize the database within the app context
with app.app_context():
    db.create_all()

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

@app.route("/", methods=['GET', 'POST'])
def main():
    message = ''
    if request.method == 'POST':
        user_input = request.form.get("user_input", "No input received")
        new_input = UserInput(user_input=user_input)
        db.session.add(new_input)
        db.session.commit()
        message = f"You entered: {user_input}"
    return '''
        <h1>Input Form</h1>
        <form action="/" method="post">
            <input name="user_input" type="text" placeholder="Enter some text...">
            <input type="submit" value="Submit">
        </form>
        ''' + (f"<p>{message}</p>" if message else "")

if __name__ == "__main__":
    app.run(debug=True, host='0.0.0.0')
