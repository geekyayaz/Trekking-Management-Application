from controllers.database import db
import datetime
from werkzeug.security import generate_password_hash, check_password_hash

class User(db.Model):
    __tablename__ = "user"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120), nullable=False)
    email = db.Column(db.String(255), unique=True, nullable=False)
    password =db.Column(db.String(255), nullable=False)
    active= db.Column(db.Boolean(), default=True)
    created_at = db.Column(db.DateTime, default=datetime.datetime.utcnow)
    roles= db.relationship('Role', secondary='roles_users',  backref=db.backref("user", lazy="dynamic"))


    def set_password(self, plain_password):
        self.password = generate_password_hash(plain_password)
 
    def check_password(self, plain_password):
        return check_password_hash(self.password, plain_password)


    def has_role_name(self, role_name):
        return any(r.name == role_name for r in self.roles)
 
    @property
    def role_names(self):
        return [r.name for r in self.roles]
 
    def __repr__(self):
        return f"<User {self.email} roles={self.role_names}>"
    

class Role(db.Model):
    __tablename__='role'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(20), unique=True, nullable=False)
    description= db.Column(db.String(255))

    def __repr__(self):
        return f"<Role {self.name}>"

roles_users = db.Table(
    "roles_users",
    db.Column("user_id", db.Integer, db.ForeignKey("user.id")),
    db.Column("role_id", db.Integer, db.ForeignKey("role.id")),)

class Trek(db.Model):
    __tablename__="trek"

    id=db.Column(db.Integer, primary_key=True, autoincrement=True)
    name =db.Column(db.String(20), unique=True, nullable=False)
    country =db.Column(db.String(20), nullable=False)
    location=db.Column(db.String(50),nullable=False)
    difficulty=db.Column(db.String(20),nullable=False)
    total_slots = db.Column(db.Integer, nullable=False)
    available_slots = db.Column(db.Integer, nullable=False)
    duration_days = db.Column(db.Integer, nullable=False)

    assigned_staff_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=True)
    status = db.Column(db.String(20), default="Pending", nullable=False)

    start_date = db.Column(db.Date, nullable=False)
    end_date = db.Column(db.Date, nullable=False)
    description = db.Column(db.Text)
 
    created_at = db.Column(db.DateTime, default=datetime.datetime.utcnow)

    staff = db.relationship("User", backref=db.backref("assigned_treks", lazy="dynamic"))
    booking = db.relationship("Booking", backref="trek", lazy="dynamic",
                                cascade="all, delete-orphan")
 
    def __repr__(self):
        return f"<Trek {self.name} ({self.status})>"

class Booking(db.Model):
    __tablename__='booking'
    id =db.Column(db.Integer,primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False)
    trek_id = db.Column(db.Integer, db.ForeignKey("trek.id"), nullable=False)

    booking_date = db.Column(db.DateTime, default=datetime.datetime.utcnow)

    status = db.Column(db.String(20), default="Booked", nullable=False)
    payment_status = db.Column(db.String(20), default="Pending")

    user = db.relationship("User", backref=db.backref("booking", lazy="dynamic"))

    __table_args__ = (
        db.UniqueConstraint("user_id", "trek_id", name="uq_user_trek_booking"),
    )

    def __repr__(self):
        return f"<Booking user={self.user_id} trek={self.trek_id} status={self.status}>"