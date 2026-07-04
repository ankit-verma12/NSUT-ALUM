from datetime import datetime

from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()


class Mentor(db.Model):
    __tablename__ = "mentor"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120), nullable=False)
    domain = db.Column(db.String(80), nullable=False)
    experience = db.Column(db.String(80), nullable=False)
    bio = db.Column(db.Text, nullable=False)
    availability = db.Column(db.String(120), nullable=False)

    bookings = db.relationship(
        "Booking", backref="mentor", cascade="all, delete-orphan"
    )

    def to_dict(self):
        return {
            "id": self.id,
            "name": self.name,
            "domain": self.domain,
            "experience": self.experience,
            "bio": self.bio,
            "availability": self.availability,
        }


class Booking(db.Model):
    __tablename__ = "booking"

    id = db.Column(db.Integer, primary_key=True)
    mentor_id = db.Column(db.Integer, db.ForeignKey("mentor.id"), nullable=False)
    student_name = db.Column(db.String(120), nullable=False)
    email = db.Column(db.String(120), nullable=False)
    reason = db.Column(db.Text, nullable=False)
    date = db.Column(db.String(40), nullable=False)
    status = db.Column(db.String(20), nullable=False, default="pending")

    def to_dict(self):
        return {
            "id": self.id,
            "mentor_id": self.mentor_id,
            "mentor_name": self.mentor.name if self.mentor else None,
            "student_name": self.student_name,
            "email": self.email,
            "reason": self.reason,
            "date": self.date,
            "status": self.status,
        }


class Posts(db.Model):
    __tablename__ = "posts"

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    body = db.Column(db.Text, nullable=False)
    author = db.Column(db.String(120), nullable=False)
    date = db.Column(
        db.DateTime, nullable=False, default=datetime.utcnow
    )

    comments = db.relationship(
        "Comments", backref="post", cascade="all, delete-orphan"
    )

    def to_dict(self):
        return {
            "id": self.id,
            "title": self.title,
            "body": self.body,
            "author": self.author,
            "date": self.date.isoformat(),
        }


class Comments(db.Model):
    __tablename__ = "comments"

    id = db.Column(db.Integer, primary_key=True)
    post_id = db.Column(db.Integer, db.ForeignKey("posts.id"), nullable=False)
    author = db.Column(db.String(120), nullable=False)
    comment = db.Column(db.Text, nullable=False)
    date = db.Column(
        db.DateTime, nullable=False, default=datetime.utcnow
    )

    def to_dict(self):
        return {
            "id": self.id,
            "post_id": self.post_id,
            "author": self.author,
            "comment": self.comment,
            "date": self.date.isoformat(),
        }
