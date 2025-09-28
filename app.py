from flask import Flask, render_template, request, jsonify
from flask_migrate import Migrate
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from dotenv import load_dotenv
import os

load_dotenv()

app = Flask(__name__)
app.config.from_object("config.Config")
db = SQLAlchemy(app)
migrate = Migrate(app, db)

class Message(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    text = db.Column(db.String(500), nullable=False)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)
    likes = db.Column(db.Integer, default=0)

    def __repr__(self):
        return f"<Message {self.id}: {self.text}>"
    
class Like(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    message_id = db.Column(db.Integer, db.ForeignKey("message.id"), nullable=False)
    ip_address = db.Column(db.String(50), nullable=False)

    __table_args__ = (db.UniqueConstraint("message_id", "ip_address", name="unique_like"),)

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
        ip = request.remote_addr  # IP do cliente
        all_messages = Message.query.order_by(Message.timestamp.asc()).all()

        messages_data = []
        for msg in all_messages:
            # verificar se o IP já curtiu
            user_liked = Like.query.filter_by(message_id=msg.id, ip_address=ip).first() is not None
            messages_data.append({
                "id": msg.id,
                "text": msg.text,
                "timestamp": msg.timestamp.isoformat(),
                "likes": msg.likes,
                "userLiked": user_liked  # <- adiciona persistência
            })

        return jsonify(messages_data)


# rota para pegar top 5
@app.route("/top-messages", methods=["GET"])
def top_messages():
    top = Message.query.order_by(Message.likes.desc()).limit(5).all()
    return jsonify([{"id": m.id, "text": m.text, "likes": m.likes} for m in top])

# rota de like
@app.route("/like/<int:msg_id>", methods=["POST"])
def like_message(msg_id):
    msg = Message.query.get_or_404(msg_id)
    ip = request.remote_addr  # IP do cliente

    existing_like = Like.query.filter_by(message_id=msg.id, ip_address=ip).first()
    
    if existing_like:
        # desfazer like
        db.session.delete(existing_like)
        msg.likes = max(msg.likes - 1, 0)  # evita negativos
        db.session.commit()
        return jsonify({"status": "undone", "likes": msg.likes})
    else:
        # adicionar like
        new_like = Like(message_id=msg.id, ip_address=ip)
        db.session.add(new_like)
        msg.likes += 1
        db.session.commit()
        return jsonify({"status": "success", "likes": msg.likes})


if __name__ == "__main__":
    with app.app_context():
        db.create_all()
    app.run(debug=True)

