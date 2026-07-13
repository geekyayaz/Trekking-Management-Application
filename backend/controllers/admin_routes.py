import datetime
from flask import Blueprint,request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity, get_jwt


from controllers.database import db
from controllers.models import Trek, Booking, User, StaffProfile
from controllers.cache import invalidate_cache

admin_bp = Blueprint('admin_routes', __name__)

VALID_DIFFICULTIES = {"Easy", "Moderate", "Hard"}
VALID_TREK_STATUSES = {"Pending", "Approved", "Open", "Closed", "Completed"}

def require_role(role_name):
    if get_jwt().get("role") != role_name:
        return jsonify({"message": f"{role_name.capitalize()} access required"}), 403
    return None

def parse_date(value, field_name):
    try:
        return datetime.datetime.strptime(value, "%Y-%m-%d").date()
    except (TypeError, ValueError):
        raise ValueError(f"{field_name} must be in YYYY-MM-DD format")

@admin_bp.route("/dashboard", methods=["GET"])
@jwt_required()
def dashboard():
    role_error = require_role("admin")
    if role_error:
        return role_error
 
    total_treks = Trek.query.count()
    total_users = User.query.filter_by(role="user").count()
    total_staff = User.query.filter_by(role="staff").count()
    total_bookings = Booking.query.count()
 
    return jsonify({
        "total_treks": total_treks,
        "total_users": total_users,
        "total_staff": total_staff,
        "total_bookings": total_bookings,
        "treks_by_status": {
            status: Trek.query.filter_by(status=status).count()
            for status in VALID_TREK_STATUSES
        },
    }), 200
@admin_bp.route("/treks", methods=["GET"])
@jwt_required()
def trek_list():
    role_error=require_role("admin")
    if role_error:
        return role_error
    query =Trek.query

    status=request.args.get("status")
    search=request.args.get("search")
    if status:
        query = query.filter(Trek.status == status)
    if search:
        query = query.filter(
            db.or_(
                Trek.name.ilike(f"%{search}%"),
                Trek.location.ilike(f"%{search}%"),
                Trek.country.ilike(f"%{search}%"),
            )
        )
    treks = query.order_by(Trek.created_at.desc()).all()
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
        "assigned_staff_id": t.assigned_staff_id,
        "assigned_staff_name": t.staff.name if t.staff else None,
        "start_date": t.start_date.isoformat(),
        "end_date": t.end_date.isoformat(),
        "description": t.description,
    } for t in treks]), 200

@admin_bp.route("/treks/<int:trek_id>", methods=["GET"])
@jwt_required()
def admin_get_trek(trek_id):
    role_error = require_role("admin")
    if role_error:
        return role_error
 
    trek = Trek.query.get(trek_id)
    if not trek:
        return jsonify({"message": "Trek not found"}), 404
 
    registered = [{
        "booking_id": b.id,
        "user_id": b.user_id,
        "user_name": b.user.name,
        "status": b.status,
        "payment_status": b.payment_status,
        "booked_on": b.booking_date.isoformat(),
    } for b in trek.booking]
 
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
        "assigned_staff_id": trek.assigned_staff_id,
        "assigned_staff_name": trek.staff.name if trek.staff else None,
        "start_date": trek.start_date.isoformat(),
        "end_date": trek.end_date.isoformat(),
        "description": trek.description,
        "registered_users": registered,
    }), 200
 
 
@admin_bp.route("/treks", methods=["POST"])
@jwt_required()
def create_trek():
    role_error = require_role("admin")
    if role_error:
        return role_error
 
    data = request.get_json() or {}
 
    required_fields = ["name", "country", "location", "difficulty",
                        "duration_days", "total_slots", "start_date", "end_date"]
    missing = [f for f in required_fields if f not in data or data[f] in (None, "")]
    if missing:
        return jsonify({"message": f"Missing required fields: {', '.join(missing)}"}), 400
 
    if data["difficulty"] not in VALID_DIFFICULTIES:
        return jsonify({"message": f"difficulty must be one of {sorted(VALID_DIFFICULTIES)}"}), 400
 
    if Trek.query.filter_by(name=data["name"]).first():
        return jsonify({"message": "A trek with this name already exists"}), 409
 
    try:
        total_slots = int(data["total_slots"])
        duration_days = int(data["duration_days"])
        start_date = parse_date(data["start_date"], "start_date")
        end_date = parse_date(data["end_date"], "end_date")
    except ValueError as e:
        return jsonify({"message": str(e)}), 400
 
    if total_slots <= 0:
        return jsonify({"message": "total_slots must be greater than 0"}), 400
    if end_date < start_date:
        return jsonify({"message": "end_date cannot be before start_date"}), 400
 
    status = data.get("status", "Pending")
    if status not in VALID_TREK_STATUSES:
        return jsonify({"message": f"status must be one of {sorted(VALID_TREK_STATUSES)}"}), 400
 
    trek = Trek(
        name=data["name"],
        country=data["country"],
        location=data["location"],
        difficulty=data["difficulty"],
        duration_days=duration_days,
        total_slots=total_slots,
        available_slots=total_slots,
        status=status,
        start_date=start_date,
        end_date=end_date,
        description=data.get("description"),
    )
 
    db.session.add(trek)
    db.session.commit()
    invalidate_cache("treks:*")
 
    return jsonify({"message": "Trek created", "trek_id": trek.id}), 201
 
 
@admin_bp.route("/treks/<int:trek_id>", methods=["PUT"])
@jwt_required()
def update_trek(trek_id):
    role_error = require_role("admin")
    if role_error:
        return role_error
 
    trek = Trek.query.get(trek_id)
    if not trek:
        return jsonify({"message": "Trek not found"}), 404
 
    data = request.get_json() or {}
 
    if "name" in data:
        existing = Trek.query.filter(Trek.name == data["name"], Trek.id != trek.id).first()
        if existing:
            return jsonify({"message": "A trek with this name already exists"}), 409
        trek.name = data["name"]
 
    if "country" in data:
        trek.country = data["country"]
    if "location" in data:
        trek.location = data["location"]
    if "description" in data:
        trek.description = data["description"]
 
    if "difficulty" in data:
        if data["difficulty"] not in VALID_DIFFICULTIES:
            return jsonify({"message": f"difficulty must be one of {sorted(VALID_DIFFICULTIES)}"}), 400
        trek.difficulty = data["difficulty"]
 
    if "duration_days" in data:
        try:
            trek.duration_days = int(data["duration_days"])
        except (TypeError, ValueError):
            return jsonify({"message": "duration_days must be an integer"}), 400
 
    if "total_slots" in data:
        try:
            new_total = int(data["total_slots"])
        except (TypeError, ValueError):
            return jsonify({"message": "total_slots must be an integer"}), 400
        booked_count = Booking.query.filter_by(trek_id=trek.id, status="Booked").count()
        if new_total < booked_count:
            return jsonify({
                "message": f"total_slots cannot be less than current bookings ({booked_count})"
            }), 400
        trek.available_slots = new_total - booked_count
        trek.total_slots = new_total
 
    if "status" in data:
        if data["status"] not in VALID_TREK_STATUSES:
            return jsonify({"message": f"status must be one of {sorted(VALID_TREK_STATUSES)}"}), 400
        trek.status = data["status"]
 
    if "start_date" in data or "end_date" in data:
        try:
            start_date = parse_date(data.get("start_date"), "start_date") if "start_date" in data else trek.start_date
            end_date = parse_date(data.get("end_date"), "end_date") if "end_date" in data else trek.end_date
        except ValueError as e:
            return jsonify({"message": str(e)}), 400
        if end_date < start_date:
            return jsonify({"message": "end_date cannot be before start_date"}), 400
        trek.start_date = start_date
        trek.end_date = end_date
 
    db.session.commit()
    invalidate_cache("treks:*")
    return jsonify({"message": "Trek updated"}), 200
 
 
@admin_bp.route("/treks/<int:trek_id>", methods=["DELETE"])
@jwt_required()
def delete_trek(trek_id):
    role_error = require_role("admin")
    if role_error:
        return role_error
 
    trek = Trek.query.get(trek_id)
    if not trek:
        return jsonify({"message": "Trek not found"}), 404
 
    active_bookings = Booking.query.filter_by(trek_id=trek.id, status="Booked").count()
    if active_bookings > 0:
        return jsonify({
            "message": f"Cannot delete trek with {active_bookings} active booking(s). "
                       f"Close or cancel bookings first."
        }), 400
 
    db.session.delete(trek)
    db.session.commit()
    invalidate_cache("treks:*")
    return jsonify({"message": "Trek removed"}), 200
 
 

@admin_bp.route("/staff", methods=["GET"])
@jwt_required()
def list_staff():
    role_error = require_role("admin")
    if role_error:
        return role_error
 
    query = User.query.filter_by(role="staff")
 
    search = request.args.get("search")
    if search:
        query = query.filter(
            db.or_(
                User.name.ilike(f"%{search}%"),
                User.username.ilike(f"%{search}%"),
                User.email.ilike(f"%{search}%"),
            )
        )
 
    staff_members = query.all()
 
    return jsonify([{
        "id": s.id,
        "name": s.name,
        "username": s.username,
        "email": s.email,
        "phone": s.phone,
        "active": s.active,
        "blacklisted": s.blacklisted,
        "contact_number": s.staff_profile.contact_number if s.staff_profile else None,
        "specialization": s.staff_profile.specialization if s.staff_profile else None,
        "status": s.staff_profile.status if s.staff_profile else None,
        "assigned_trek_count": s.assigned_treks.count(),
    } for s in staff_members]), 200
 
 
@admin_bp.route("/staff/<int:staff_id>", methods=["GET"])
@jwt_required()
def get_staff(staff_id):
    role_error = require_role("admin")
    if role_error:
        return role_error
 
    staff = User.query.filter_by(id=staff_id, role="staff").first()
    if not staff:
        return jsonify({"message": "Staff member not found"}), 404
 
    assigned_treks = [{
        "id": t.id,
        "name": t.name,
        "status": t.status,
        "start_date": t.start_date.isoformat(),
        "end_date": t.end_date.isoformat(),
    } for t in staff.assigned_treks]
 
    return jsonify({
        "id": staff.id,
        "name": staff.name,
        "username": staff.username,
        "email": staff.email,
        "phone": staff.phone,
        "address": staff.address,
        "active": staff.active,
        "blacklisted": staff.blacklisted,
        "contact_number": staff.staff_profile.contact_number if staff.staff_profile else None,
        "specialization": staff.staff_profile.specialization if staff.staff_profile else None,
        "status": staff.staff_profile.status if staff.staff_profile else None,
        "assigned_treks": assigned_treks,
    }), 200
 
 
@admin_bp.route("/staff", methods=["POST"])
@jwt_required()
def create_staff():
    role_error = require_role("admin")
    if role_error:
        return role_error
 
    data = request.get_json() or {}
 
    required_fields = ["name", "username", "email", "password"]
    missing = [f for f in required_fields if f not in data or data[f] in (None, "")]
    if missing:
        return jsonify({"message": f"Missing required fields: {', '.join(missing)}"}), 400
 
    if User.query.filter_by(username=data["username"]).first():
        return jsonify({"message": "Username already taken"}), 409
    if User.query.filter_by(email=data["email"]).first():
        return jsonify({"message": "Email already registered"}), 409
 
    staff_user = User(
        name=data["name"],
        username=data["username"],
        email=data["email"],
        role="staff",
        phone=data.get("phone"),
        address=data.get("address"),
    )
    staff_user.set_password(data["password"])
 
    db.session.add(staff_user)
    db.session.flush()
 
    profile = StaffProfile(
        user_id=staff_user.id,
        contact_number=data.get("contact_number", data.get("phone")),
        specialization=data.get("specialization"),
        status="active",
    )
    db.session.add(profile)
    db.session.commit()
 
    return jsonify({"message": "Staff member created", "staff_id": staff_user.id}), 201
 
 
@admin_bp.route("/staff/<int:staff_id>", methods=["PUT"])
@jwt_required()
def update_staff(staff_id):
    role_error = require_role("admin")
    if role_error:
        return role_error
 
    staff = User.query.filter_by(id=staff_id, role="staff").first()
    if not staff:
        return jsonify({"message": "Staff member not found"}), 404
 
    data = request.get_json() or {}
 
    if "name" in data:
        staff.name = data["name"]
    if "phone" in data:
        staff.phone = data["phone"]
    if "address" in data:
        staff.address = data["address"]
    if "email" in data:
        existing = User.query.filter(User.email == data["email"], User.id != staff.id).first()
        if existing:
            return jsonify({"message": "Email already registered"}), 409
        staff.email = data["email"]
 
    profile = staff.staff_profile
    if profile:
        if "contact_number" in data:
            profile.contact_number = data["contact_number"]
        if "specialization" in data:
            profile.specialization = data["specialization"]
        if "status" in data:
            profile.status = data["status"]
 
    db.session.commit()
    return jsonify({"message": "Staff member updated"}), 200
 
 
@admin_bp.route("/staff/<int:staff_id>", methods=["DELETE"])
@jwt_required()
def remove_staff(staff_id):
    role_error = require_role("admin")
    if role_error:
        return role_error
 
    staff = User.query.filter_by(id=staff_id, role="staff").first()
    if not staff:
        return jsonify({"message": "Staff member not found"}), 404
 
    active_treks = Trek.query.filter(
        Trek.assigned_staff_id == staff.id,
        Trek.status.in_(["Approved", "Open"]),
    ).count()
    if active_treks > 0:
        return jsonify({
            "message": f"Cannot remove staff assigned to {active_treks} active trek(s). "
                       f"Reassign those treks first."
        }), 400
 
    staff.active = False
    if staff.staff_profile:
        staff.staff_profile.status = "removed"
 
    db.session.commit()
    return jsonify({"message": "Staff member deactivated"}), 200
 
 
@admin_bp.route("/treks/<int:trek_id>/assign-staff", methods=["POST"])
@jwt_required()
def assign_staff_to_trek(trek_id):
    role_error = require_role("admin")
    if role_error:
        return role_error
 
    trek = Trek.query.get(trek_id)
    if not trek:
        return jsonify({"message": "Trek not found"}), 404
 
    data = request.get_json() or {}
    staff_id = data.get("staff_id")
 
    if staff_id is None:
        trek.assigned_staff_id = None
        db.session.commit()
        return jsonify({"message": "Staff unassigned from trek"}), 200
 
    staff = User.query.filter_by(id=staff_id, role="staff").first()
    if not staff:
        return jsonify({"message": "Staff member not found"}), 404
    if not staff.active or staff.blacklisted:
        return jsonify({"message": "Cannot assign an inactive or blacklisted staff member"}), 400
 
    trek.assigned_staff_id = staff.id
    db.session.commit()
    invalidate_cache("treks:*")
 
    return jsonify({
        "message": "Staff assigned to trek",
        "trek_id": trek.id,
        "staff_id": staff.id,
        "staff_name": staff.name,
    }), 200
 
 

@admin_bp.route("/users", methods=["GET"])
@jwt_required()
def list_users():
    role_error = require_role("admin")
    if role_error:
        return role_error
 
    query = User.query.filter_by(role="user")
 
    search = request.args.get("search")
    if search:
        query = query.filter(
            db.or_(
                User.name.ilike(f"%{search}%"),
                User.username.ilike(f"%{search}%"),
                User.email.ilike(f"%{search}%"),
            )
        )
 
    users = query.all()
 
    return jsonify([{
        "id": u.id,
        "name": u.name,
        "username": u.username,
        "email": u.email,
        "phone": u.phone,
        "active": u.active,
        "blacklisted": u.blacklisted,
        "total_bookings": u.booking.count(),
        "created_at": u.created_at.isoformat() if u.created_at else None,
    } for u in users]), 200
 
 
@admin_bp.route("/users/<int:user_id>", methods=["GET"])
@jwt_required()
def get_user_detail(user_id):
    role_error = require_role("admin")
    if role_error:
        return role_error
 
    user = User.query.filter_by(id=user_id, role="user").first()
    if not user:
        return jsonify({"message": "User not found"}), 404
 
    bookings = [{
        "booking_id": b.id,
        "trek_id": b.trek_id,
        "trek_name": b.trek.name,
        "status": b.status,
        "payment_status": b.payment_status,
        "booked_on": b.booking_date.isoformat(),
    } for b in user.booking]
 
    return jsonify({
        "id": user.id,
        "name": user.name,
        "username": user.username,
        "email": user.email,
        "phone": user.phone,
        "address": user.address,
        "active": user.active,
        "blacklisted": user.blacklisted,
        "created_at": user.created_at.isoformat() if user.created_at else None,
        "bookings": bookings,
    }), 200
 
 
@admin_bp.route("/accounts/<int:account_id>/status", methods=["PUT"])
@jwt_required()
def update_account_status(account_id):
    """Blacklist / activate-deactivate any account (user or staff) by id."""
    role_error = require_role("admin")
    if role_error:
        return role_error
 
    account = User.query.get(account_id)
    if not account:
        return jsonify({"message": "Account not found"}), 404
 
    if account.role == "admin":
        return jsonify({"message": "Cannot modify an admin account"}), 400
 
    data = request.get_json() or {}
    if "active" not in data and "blacklisted" not in data:
        return jsonify({"message": "Provide 'active' and/or 'blacklisted' in the request body"}), 400
 
    if "active" in data:
        account.active = bool(data["active"])
    if "blacklisted" in data:
        account.blacklisted = bool(data["blacklisted"])
        if account.blacklisted:
            account.active = False
 
    db.session.commit()
 
    return jsonify({
        "message": "Account status updated",
        "id": account.id,
        "role": account.role,
        "active": account.active,
        "blacklisted": account.blacklisted,
    }), 200
 
@admin_bp.route("/users/<int:user_id>", methods=["PUT"])
@jwt_required()
def update_user_details(user_id):
    """Admin editing a trekker's profile fields (name, phone, address, email)."""
    role_error = require_role("admin")
    if role_error:
        return role_error

    user = User.query.filter_by(id=user_id, role="user").first()
    if not user:
        return jsonify({"message": "User not found"}), 404

    data = request.get_json() or {}

    if "name" in data:
        user.name = data["name"]
    if "phone" in data:
        user.phone = data["phone"]
    if "address" in data:
        user.address = data["address"]
    if "email" in data:
        existing = User.query.filter(User.email == data["email"], User.id != user.id).first()
        if existing:
            return jsonify({"message": "Email already registered"}), 409
        user.email = data["email"]

    db.session.commit()
    return jsonify({"message": "User updated"}), 200

@admin_bp.route("/bookings", methods=["GET"])
@jwt_required()
def all_bookings():
    role_error = require_role("admin")
    if role_error:
        return role_error
 
    query = Booking.query
 
    status = request.args.get("status")
    trek_id = request.args.get("trek_id")
    user_id = request.args.get("user_id")
 
    if status:
        query = query.filter(Booking.status == status)
    if trek_id:
        query = query.filter(Booking.trek_id == int(trek_id))
    if user_id:
        query = query.filter(Booking.user_id == int(user_id))
 
    bookings = query.order_by(Booking.booking_date.desc()).all()
 
    return jsonify([{
        "booking_id": b.id,
        "user_id": b.user_id,
        "user_name": b.user.name,
        "trek_id": b.trek_id,
        "trek_name": b.trek.name,
        "status": b.status,
        "payment_status": b.payment_status,
        "booked_on": b.booking_date.isoformat(),
    } for b in bookings]), 200
 
 

@admin_bp.route("/reports/stats", methods=["GET"])
@jwt_required()
def trek_statistics():
    role_error = require_role("admin")
    if role_error:
        return role_error
 
    popular_treks_raw = (
        db.session.query(
            Trek.id, Trek.name, db.func.count(Booking.id).label("booking_count")
        )
        .join(Booking, Booking.trek_id == Trek.id)
        .filter(Booking.status.in_(["Booked", "Completed"]))
        .group_by(Trek.id)
        .order_by(db.func.count(Booking.id).desc())
        .limit(5)
        .all()
    )
 
    popular_treks = [
        {"trek_id": row[0], "trek_name": row[1], "booking_count": row[2]}
        for row in popular_treks_raw
    ]
 
    completed_treks = Trek.query.filter_by(status="Completed").count()
    open_treks = Trek.query.filter_by(status="Open").count()
 
    total_bookings = Booking.query.count()
    cancelled_bookings = Booking.query.filter_by(status="Cancelled").count()
    completed_bookings = Booking.query.filter_by(status="Completed").count()
 
    cancellation_rate = (
        round((cancelled_bookings / total_bookings) * 100, 2) if total_bookings else 0
    )
 
    return jsonify({
        "popular_treks": popular_treks,
        "completed_treks": completed_treks,
        "open_treks": open_treks,
        "total_bookings": total_bookings,
        "cancelled_bookings": cancelled_bookings,
        "completed_bookings": completed_bookings,
        "cancellation_rate_percent": cancellation_rate,
        "active_staff": User.query.filter_by(role="staff", active=True).count(),
        "blacklisted_accounts": User.query.filter_by(blacklisted=True).count(),
    }), 200

from controllers.tasks import generate_monthly_report

@admin_bp.route("/reports/trigger-monthly", methods=["POST"])
@jwt_required()
def trigger_monthly_report():
    role_error = require_role("admin")
    if role_error:
        return role_error

    task = generate_monthly_report.delay()
    return jsonify({
        "message": "Monthly report generation started",
        "task_id": task.id,
    }), 202