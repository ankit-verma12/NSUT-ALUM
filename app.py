import os

from flask import Flask, jsonify, render_template, request
from flask_cors import CORS

from models import Booking, Comments, Mentor, Posts, db
from seed import seed_mentors

BASE_DIR = os.path.abspath(os.path.dirname(__file__))

VALID_BOOKING_STATUSES = ("pending", "accepted", "rejected")

MENTOR_FIELDS = ("name", "domain", "experience", "bio", "availability")
BOOKING_CREATE_FIELDS = ("mentor_id", "student_name", "email", "reason", "date")
POST_CREATE_FIELDS = ("title", "body", "author")
COMMENT_CREATE_FIELDS = ("author", "comment")


def error(message, status=400):
    return jsonify({"error": message}), status


def get_json_body():
    return request.get_json(silent=True) or {}


def require_fields(data, fields):
    missing = [f for f in fields if not data.get(f)]
    if missing:
        return f"Missing required field(s): {', '.join(missing)}"
    return None


def create_app():
    app = Flask(__name__)
    app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///" + os.path.join(
        BASE_DIR, "nalum.db"
    )
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

    db.init_app(app)
    CORS(app)

    with app.app_context():
        db.create_all()
        seed_mentors()

    register_routes(app)

    return app


def register_routes(app):
    @app.route("/api/health")
    def health():
        return {"status": "ok"}

    # ---------- Pages ----------

    @app.route("/")
    def index_page():
        return render_template("index.html")

    @app.route("/mentor/<int:mentor_id>")
    def mentor_page(mentor_id):
        return render_template("mentor.html", mentor_id=mentor_id)

    @app.route("/forum")
    def forum_page():
        return render_template("forum.html")

    @app.route("/post/<int:post_id>")
    def post_page(post_id):
        return render_template("post.html", post_id=post_id)

    @app.route("/mentor-dashboard")
    def mentor_dashboard_page():
        return render_template("mentor-dashboard.html")

    @app.route("/student-dashboard")
    def student_dashboard_page():
        return render_template("student-dashboard.html")

    # ---------- Mentors ----------

    @app.route("/api/mentors", methods=["GET"])
    def list_mentors():
        query = Mentor.query
        domain = request.args.get("domain")
        if domain:
            query = query.filter(Mentor.domain.ilike(domain))
        mentors = query.order_by(Mentor.id).all()
        return jsonify([m.to_dict() for m in mentors])

    @app.route("/api/mentors/<int:mentor_id>", methods=["GET"])
    def get_mentor(mentor_id):
        mentor = Mentor.query.get(mentor_id)
        if not mentor:
            return error("Mentor not found", 404)
        return jsonify(mentor.to_dict())

    @app.route("/api/mentors", methods=["POST"])
    def create_mentor():
        data = get_json_body()
        missing = require_fields(data, MENTOR_FIELDS)
        if missing:
            return error(missing)

        mentor = Mentor(
            name=data["name"],
            domain=data["domain"],
            experience=data["experience"],
            bio=data["bio"],
            availability=data["availability"],
        )
        db.session.add(mentor)
        db.session.commit()
        return jsonify(mentor.to_dict()), 201

    @app.route("/api/mentors/<int:mentor_id>", methods=["PUT"])
    def update_mentor(mentor_id):
        mentor = Mentor.query.get(mentor_id)
        if not mentor:
            return error("Mentor not found", 404)

        data = get_json_body()
        if not data:
            return error("No fields provided to update")

        for field in MENTOR_FIELDS:
            if field in data:
                setattr(mentor, field, data[field])

        db.session.commit()
        return jsonify(mentor.to_dict())

    @app.route("/api/mentors/<int:mentor_id>", methods=["DELETE"])
    def delete_mentor(mentor_id):
        mentor = Mentor.query.get(mentor_id)
        if not mentor:
            return error("Mentor not found", 404)

        db.session.delete(mentor)
        db.session.commit()
        return jsonify({"message": "Mentor and related bookings deleted"})

    # ---------- Bookings ----------

    @app.route("/api/bookings", methods=["GET"])
    def list_bookings():
        bookings = Booking.query.order_by(Booking.id.desc()).all()
        return jsonify([b.to_dict() for b in bookings])

    @app.route("/api/bookings/mentor/<int:mentor_id>", methods=["GET"])
    def bookings_for_mentor(mentor_id):
        if not Mentor.query.get(mentor_id):
            return error("Mentor not found", 404)
        bookings = (
            Booking.query.filter_by(mentor_id=mentor_id)
            .order_by(Booking.id.desc())
            .all()
        )
        return jsonify([b.to_dict() for b in bookings])

    @app.route("/api/bookings/student", methods=["GET"])
    def bookings_for_student():
        email = request.args.get("email")
        if not email:
            return error("Missing required query param: email")
        bookings = (
            Booking.query.filter(Booking.email.ilike(email))
            .order_by(Booking.id.desc())
            .all()
        )
        return jsonify([b.to_dict() for b in bookings])

    @app.route("/api/bookings", methods=["POST"])
    def create_booking():
        data = get_json_body()
        missing = require_fields(data, BOOKING_CREATE_FIELDS)
        if missing:
            return error(missing)

        mentor = Mentor.query.get(data["mentor_id"])
        if not mentor:
            return error("mentor_id does not match an existing mentor")

        booking = Booking(
            mentor_id=data["mentor_id"],
            student_name=data["student_name"],
            email=data["email"],
            reason=data["reason"],
            date=data["date"],
            status="pending",
        )
        db.session.add(booking)
        db.session.commit()
        return jsonify(booking.to_dict()), 201

    @app.route("/api/bookings/<int:booking_id>", methods=["PUT"])
    def update_booking_status(booking_id):
        booking = Booking.query.get(booking_id)
        if not booking:
            return error("Booking not found", 404)

        data = get_json_body()
        status = data.get("status")
        if not status:
            return error("Missing required field: status")
        if status not in VALID_BOOKING_STATUSES:
            return error(
                f"Invalid status '{status}'. Must be one of: "
                f"{', '.join(VALID_BOOKING_STATUSES)}"
            )

        booking.status = status
        db.session.commit()
        return jsonify(booking.to_dict())

    @app.route("/api/bookings/<int:booking_id>", methods=["DELETE"])
    def delete_booking(booking_id):
        booking = Booking.query.get(booking_id)
        if not booking:
            return error("Booking not found", 404)

        db.session.delete(booking)
        db.session.commit()
        return jsonify({"message": "Booking deleted"})

    # ---------- Forum: Posts ----------

    @app.route("/api/posts", methods=["GET"])
    def list_posts():
        posts = Posts.query.order_by(Posts.date.desc()).all()
        result = []
        for p in posts:
            d = p.to_dict()
            d["comment_count"] = len(p.comments)
            result.append(d)
        return jsonify(result)

    @app.route("/api/posts/<int:post_id>", methods=["GET"])
    def get_post(post_id):
        post = Posts.query.get(post_id)
        if not post:
            return error("Post not found", 404)

        d = post.to_dict()
        comments = Comments.query.filter_by(post_id=post_id).order_by(
            Comments.date
        ).all()
        d["comments"] = [c.to_dict() for c in comments]
        return jsonify(d)

    @app.route("/api/posts", methods=["POST"])
    def create_post():
        data = get_json_body()
        missing = require_fields(data, POST_CREATE_FIELDS)
        if missing:
            return error(missing)

        post = Posts(
            title=data["title"],
            body=data["body"],
            author=data["author"],
        )
        db.session.add(post)
        db.session.commit()
        return jsonify(post.to_dict()), 201

    @app.route("/api/posts/<int:post_id>", methods=["DELETE"])
    def delete_post(post_id):
        post = Posts.query.get(post_id)
        if not post:
            return error("Post not found", 404)

        db.session.delete(post)
        db.session.commit()
        return jsonify({"message": "Post and its comments deleted"})

    @app.route("/api/posts/<int:post_id>/comments", methods=["POST"])
    def add_comment(post_id):
        post = Posts.query.get(post_id)
        if not post:
            return error("Post not found", 404)

        data = get_json_body()
        missing = require_fields(data, COMMENT_CREATE_FIELDS)
        if missing:
            return error(missing)

        comment = Comments(
            post_id=post_id,
            author=data["author"],
            comment=data["comment"],
        )
        db.session.add(comment)
        db.session.commit()
        return jsonify(comment.to_dict()), 201

    @app.route("/api/comments/<int:comment_id>", methods=["DELETE"])
    def delete_comment(comment_id):
        comment = Comments.query.get(comment_id)
        if not comment:
            return error("Comment not found", 404)

        db.session.delete(comment)
        db.session.commit()
        return jsonify({"message": "Comment deleted"})

    # ---------- Dashboard ----------

    @app.route("/api/dashboard", methods=["GET"])
    def dashboard():
        recent_bookings = (
            Booking.query.order_by(Booking.id.desc()).limit(5).all()
        )
        recent_posts = Posts.query.order_by(Posts.date.desc()).limit(5).all()

        return jsonify(
            {
                "mentor_count": Mentor.query.count(),
                "booking_count": Booking.query.count(),
                "pending_bookings": Booking.query.filter_by(
                    status="pending"
                ).count(),
                "post_count": Posts.query.count(),
                "recent_bookings": [b.to_dict() for b in recent_bookings],
                "recent_posts": [p.to_dict() for p in recent_posts],
            }
        )


app = create_app()

if __name__ == "__main__":
    debug_mode = os.environ.get("FLASK_DEBUG", "0") == "1"
    app.run(debug=debug_mode)
