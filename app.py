from flask import Flask, render_template, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from dotenv import load_dotenv
import os

load_dotenv()

app = Flask(__name__)
app.config.from_object("config.Config")
db = SQLAlchemy(app)

class Message(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    text = db.Column(db.String(500), nullable=False)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f"<Message {self.id}: {self.text}>"

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/messages", methods=["GET", "POST"])
def messages():
    if request.method == "POST":
        data = request.get_json()
        new_message = Message(text=data["message"])
        db.session.add(new_message)
        db.session.commit()
        return jsonify({"status": "success", "message": "Message added"}), 201
    else:
        all_messages = Message.query.order_by(Message.timestamp.asc()).all()
        messages_data = [{"id": msg.id, "text": msg.text, "timestamp": msg.timestamp.isoformat()} for msg in all_messages]
        return jsonify(messages_data)

if __name__ == "__main__":
    with app.app_context():
        db.create_all()
    app.run(debug=True)

