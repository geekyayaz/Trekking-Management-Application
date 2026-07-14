from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity, get_jwt
from controllers.cache import invalidate_cache


from controllers.models import db, Trek, Booking, User

user_bp = Blueprint("user_routes", __name__)


def require_role(role_name):

    if get_jwt().get("role") != role_name:
        return jsonify({"message": f"{role_name.capitalize()} access required"}), 403
    return None


from controllers.cache import get_cached, set_cached

@user_bp.route("/treks", methods=["GET"])
@jwt_required()
def trek_list():
    difficulty = request.args.get("difficulty")
    location = request.args.get("location")
    duration = request.args.get("duration")

    cache_key = f"treks:open:{difficulty}:{location}:{duration}"
    cached = get_cached(cache_key)
    if cached is not None:
        return jsonify(cached), 200

    query = Trek.query.filter_by(status="Open")
    if difficulty:
        query = query.filter(Trek.difficulty == difficulty)
    if location:
        query = query.filter(Trek.location.ilike(f"%{location}%"))
    if duration:
        query = query.filter(Trek.duration_days == int(duration))

    treks = query.all()
    result = [{
        "id": t.id, "name": t.name, "country": t.country, "location": t.location,
        "difficulty": t.difficulty, "duration_days": t.duration_days,
        "available_slots": t.available_slots, "total_slots": t.total_slots,
        "start_date": t.start_date.isoformat(), "end_date": t.end_date.isoformat(),
    } for t in treks]

    set_cached(cache_key, result)
    return jsonify(result), 200


@user_bp.route("/treks/<int:trek_id>/book", methods=["POST"])
@jwt_required()
def book_trek(trek_id):
    role_error = require_role("user")
    if role_error:
        return role_error

    user_id = int(get_jwt_identity())
    trek = Trek.query.get(trek_id)

    if not trek:
        return jsonify({"message": "Trek not found"}), 404

    if trek.status != "Open":
        return jsonify({"message": "This trek is not open for booking right now"}), 400

    if trek.available_slots <= 0:
        return jsonify({"message": "No slots available"}), 400

    existing = Booking.query.filter_by(
        user_id=user_id, trek_id=trek.id, status="Booked"
    ).first()
    if existing:
        return jsonify({"message": "You already booked this trek"}), 409

    booking = Booking(user_id=user_id, trek_id=trek.id, status="Booked")
    trek.available_slots -= 1

    db.session.add(booking)
    db.session.commit()
    invalidate_cache("treks:*")

    return jsonify({
        "message": "Trek booked successfully",
        "booking_id": booking.id,
        "remaining_slots": trek.available_slots,
    }), 201


@user_bp.route("/bookings/<int:booking_id>/cancel", methods=["POST"])
@jwt_required()
def cancel_booking(booking_id):
    role_error = require_role("user")
    if role_error:
        return role_error

    user_id = int(get_jwt_identity())
    booking = Booking.query.get(booking_id)

    if not booking or booking.user_id != user_id:
        return jsonify({"message": "Booking not found"}), 404

    if booking.status == "Cancelled":
        return jsonify({"message": "Booking already cancelled"}), 400

    booking.status = "Cancelled"
    booking.trek.available_slots += 1
    db.session.commit()
    invalidate_cache("treks:*")

    return jsonify({"message": "Booking cancelled"}), 200


@user_bp.route("/bookings/history", methods=["GET"])
@jwt_required()
def booking_history():
    role_error = require_role("user")
    if role_error:
        return role_error

    user_id = int(get_jwt_identity())
    bookings = (
        Booking.query
        .filter_by(user_id=user_id)
        .order_by(Booking.booking_date.desc())
        .all()
    )

    return jsonify([{
        "booking_id": b.id,
        "trek_name": b.trek.name,
        "location": b.trek.location,
        "start_date": b.trek.start_date.isoformat(),
        "end_date": b.trek.end_date.isoformat(),
        "status": b.status,
        "payment_status": b.payment_status,
        "booked_on": b.booking_date.isoformat(),
    } for b in bookings]), 200


@user_bp.route("/profile", methods=["GET"])
@jwt_required()
def get_profile():
    user_id = int(get_jwt_identity())
    user = User.query.get(user_id)

    if not user:
        return jsonify({"message": "User not found"}), 404

    return jsonify({
        "name": user.name,
        "username": user.username,
        "email": user.email,
        "phone": user.phone,
        "address": user.address,
    }), 200


@user_bp.route("/profile", methods=["PUT"])
@jwt_required()
def update_profile():
    user_id = int(get_jwt_identity())
    user = User.query.get(user_id)

    if not user:
        return jsonify({"message": "User not found"}), 404

    data = request.get_json() or {}

    if "name" in data:
        user.name = data["name"]
    if "phone" in data:
        user.phone = data["phone"]
    if "address" in data:
        user.address = data["address"]

    db.session.commit()
    return jsonify({"message": "Profile updated"}), 200



from controllers.tasks import export_booking_history

@user_bp.route("/export-history", methods=["POST"])
@jwt_required()
def trigger_export_history():
    role_error = require_role("user")
    if role_error:
        return role_error

    user_id = int(get_jwt_identity())
    task = export_booking_history.delay(user_id)

    return jsonify({
        "message": "Export started. You'll be emailed when it's ready.",
        "task_id": task.id,
    }), 202


@user_bp.route("/export-history/status/<task_id>", methods=["GET"])
@jwt_required()
def export_history_status(task_id):
    role_error = require_role("user")
    if role_error:
        return role_error

    from controllers.celery_app import celery
    result = celery.AsyncResult(task_id)

    response = {"task_id": task_id, "state": result.state}
    if result.state == "SUCCESS":
        response["result"] = result.result
    elif result.state == "FAILURE":
        response["error"] = str(result.info)

    return jsonify(response), 200