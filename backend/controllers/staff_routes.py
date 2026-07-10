import datetime

from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity, get_jwt

from controllers.database import db
from controllers.models import Trek, Booking, User, StaffProfile

staff_bp = Blueprint("staff_routes", __name__)


STAFF_ALLOWED_STATUSES = {"Open", "Closed", "Completed"}


def require_role(role_name):
    if get_jwt().get("role") != role_name:
        return jsonify({"message": f"{role_name.capitalize()} access required"}), 403
    return None


def get_owned_trek_or_error(trek_id, staff_id):
    """Fetch a trek and make sure it is assigned to this staff member.

    Returns (trek, None) on success, or (None, (response, status)) on failure,
    so callers can do: trek, err = get_owned_trek_or_error(...); if err: return err
    """
    trek = Trek.query.get(trek_id)
    if not trek:
        return None, (jsonify({"message": "Trek not found"}), 404)

    if trek.assigned_staff_id != staff_id:
        return None, (jsonify({"message": "You are not assigned to this trek"}), 403)

    return trek, None


# ---------------------------------------------------------------------------
# Dashboard
# ---------------------------------------------------------------------------

@staff_bp.route("/dashboard", methods=["GET"])
@jwt_required()
def dashboard():
    role_error = require_role("staff")
    if role_error:
        return role_error

    staff_id = int(get_jwt_identity())

    assigned_treks = Trek.query.filter_by(assigned_staff_id=staff_id).all()

    treks_summary = [{
        "id": t.id,
        "name": t.name,
        "location": t.location,
        "status": t.status,
        "available_slots": t.available_slots,
        "total_slots": t.total_slots,
        "registered_count": t.booking.filter(Booking.status != "Cancelled").count(),
        "start_date": t.start_date.isoformat(),
        "end_date": t.end_date.isoformat(),
    } for t in assigned_treks]

    return jsonify({
        "total_assigned_treks": len(assigned_treks),
        "open_treks": sum(1 for t in assigned_treks if t.status == "Open"),
        "completed_treks": sum(1 for t in assigned_treks if t.status == "Completed"),
        "total_registered_trekkers": sum(
            t.booking.filter(Booking.status != "Cancelled").count() for t in assigned_treks
        ),
        "treks": treks_summary,
    }), 200


# ---------------------------------------------------------------------------
# Assigned treks (list / detail)
# ---------------------------------------------------------------------------

@staff_bp.route("/treks", methods=["GET"])
@jwt_required()
def list_assigned_treks():
    role_error = require_role("staff")
    if role_error:
        return role_error

    staff_id = int(get_jwt_identity())
    query = Trek.query.filter_by(assigned_staff_id=staff_id)

    status = request.args.get("status")
    if status:
        query = query.filter(Trek.status == status)

    treks = query.order_by(Trek.start_date.asc()).all()

    return jsonify([{
        "id": t.id,
        "name": t.name,
        "country": t.country,
        "location": t.location,
        "difficulty": t.difficulty,
        "duration_days": t.duration_days,
        "available_slots": t.available_slots,
        "total_slots": t.total_slots,
        "status": t.status,
        "start_date": t.start_date.isoformat(),
        "end_date": t.end_date.isoformat(),
        "registered_count": t.booking.filter(Booking.status != "Cancelled").count(),
    } for t in treks]), 200


@staff_bp.route("/treks/<int:trek_id>", methods=["GET"])
@jwt_required()
def get_assigned_trek(trek_id):
    role_error = require_role("staff")
    if role_error:
        return role_error

    staff_id = int(get_jwt_identity())
    trek, err = get_owned_trek_or_error(trek_id, staff_id)
    if err:
        return err

    return jsonify({
        "id": trek.id,
        "name": trek.name,
        "country": trek.country,
        "location": trek.location,
        "difficulty": trek.difficulty,
        "duration_days": trek.duration_days,
        "available_slots": trek.available_slots,
        "total_slots": trek.total_slots,
        "status": trek.status,
        "start_date": trek.start_date.isoformat(),
        "end_date": trek.end_date.isoformat(),
        "description": trek.description,
    }), 200


# ---------------------------------------------------------------------------
# Trek operations: slots, status
# ---------------------------------------------------------------------------

@staff_bp.route("/treks/<int:trek_id>/slots", methods=["PUT"])
@jwt_required()
def update_slots(trek_id):
    role_error = require_role("staff")
    if role_error:
        return role_error

    staff_id = int(get_jwt_identity())
    trek, err = get_owned_trek_or_error(trek_id, staff_id)
    if err:
        return err

    data = request.get_json() or {}
    if "available_slots" not in data:
        return jsonify({"message": "available_slots is required"}), 400

    try:
        new_available = int(data["available_slots"])
    except (TypeError, ValueError):
        return jsonify({"message": "available_slots must be an integer"}), 400

    if new_available < 0:
        return jsonify({"message": "available_slots cannot be negative"}), 400
    if new_available > trek.total_slots:
        return jsonify({
            "message": f"available_slots cannot exceed total_slots ({trek.total_slots})"
        }), 400

    trek.available_slots = new_available
    db.session.commit()

    return jsonify({
        "message": "Slots updated",
        "trek_id": trek.id,
        "available_slots": trek.available_slots,
        "total_slots": trek.total_slots,
    }), 200


@staff_bp.route("/treks/<int:trek_id>/status", methods=["PUT"])
@jwt_required()
def update_trek_status(trek_id):
    role_error = require_role("staff")
    if role_error:
        return role_error

    staff_id = int(get_jwt_identity())
    trek, err = get_owned_trek_or_error(trek_id, staff_id)
    if err:
        return err

    data = request.get_json() or {}
    new_status = data.get("status")

    if new_status not in STAFF_ALLOWED_STATUSES:
        return jsonify({
            "message": f"status must be one of {sorted(STAFF_ALLOWED_STATUSES)}"
        }), 400

    if trek.status not in {"Approved", "Open", "Closed"}:
        return jsonify({
            "message": f"Trek cannot be updated from its current status ('{trek.status}')"
        }), 400

    # Simple forward-only lifecycle for staff-driven transitions.
    valid_transitions = {
        "Approved": {"Open"},
        "Open": {"Closed", "Completed"},
        "Closed": {"Open", "Completed"},
    }
    if new_status not in valid_transitions.get(trek.status, set()):
        return jsonify({
            "message": f"Cannot move trek from '{trek.status}' to '{new_status}'"
        }), 400

    trek.status = new_status

    # When a trek completes, any still-"Booked" bookings are marked Completed too.
    if new_status == "Completed":
        for booking in trek.booking.filter_by(status="Booked"):
            booking.status = "Completed"

    db.session.commit()

    return jsonify({"message": "Trek status updated", "trek_id": trek.id, "status": trek.status}), 200


# ---------------------------------------------------------------------------
# Participants
# ---------------------------------------------------------------------------

@staff_bp.route("/treks/<int:trek_id>/participants", methods=["GET"])
@jwt_required()
def list_participants(trek_id):
    role_error = require_role("staff")
    if role_error:
        return role_error

    staff_id = int(get_jwt_identity())
    trek, err = get_owned_trek_or_error(trek_id, staff_id)
    if err:
        return err

    status_filter = request.args.get("status")
    query = trek.booking
    if status_filter:
        query = query.filter_by(status=status_filter)

    bookings = query.order_by(Booking.booking_date.asc()).all()

    return jsonify([{
        "booking_id": b.id,
        "user_id": b.user_id,
        "name": b.user.name,
        "email": b.user.email,
        "phone": b.user.phone,
        "status": b.status,
        "payment_status": b.payment_status,
        "booked_on": b.booking_date.isoformat(),
    } for b in bookings]), 200


# ---------------------------------------------------------------------------
# Staff's own profile
# ---------------------------------------------------------------------------

@staff_bp.route("/profile", methods=["GET"])
@jwt_required()
def get_profile():
    role_error = require_role("staff")
    if role_error:
        return role_error

    staff_id = int(get_jwt_identity())
    staff = User.query.get(staff_id)

    if not staff:
        return jsonify({"message": "Staff member not found"}), 404

    profile = staff.staff_profile

    return jsonify({
        "id": staff.id,
        "name": staff.name,
        "username": staff.username,
        "email": staff.email,
        "phone": staff.phone,
        "address": staff.address,
        "contact_number": profile.contact_number if profile else None,
        "specialization": profile.specialization if profile else None,
        "status": profile.status if profile else None,
    }), 200


@staff_bp.route("/profile", methods=["PUT"])
@jwt_required()
def update_profile():
    role_error = require_role("staff")
    if role_error:
        return role_error

    staff_id = int(get_jwt_identity())
    staff = User.query.get(staff_id)

    if not staff:
        return jsonify({"message": "Staff member not found"}), 404

    data = request.get_json() or {}

    # Staff can update their own contact info, not their name/email/role
    # (those stay admin-controlled — see admin_routes.update_staff).
    if "phone" in data:
        staff.phone = data["phone"]
    if "address" in data:
        staff.address = data["address"]

    profile = staff.staff_profile
    if profile and "contact_number" in data:
        profile.contact_number = data["contact_number"]

    db.session.commit()
    return jsonify({"message": "Profile updated"}), 200