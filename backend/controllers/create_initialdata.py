import datetime
from controllers.models import User, Trek, db

DEFAULT_PASSWORD = "password123"

TREKKERS = [
    dict(name="Ram", email="ram@gmail.com", phone="9876543210", address="Bolpur, West Bengal"),
    dict(name="Sham", email="sham@gmail.com", phone="8765432198", address="Kirnahar, West Bengal"),
    dict(name="Jodu", email="jodu@gmail.com", phone="9123456780", address="Kolkata, West Bengal"),
    dict(name="Modhu", email="modhu@gmail.com", phone="8987654321", address="Darjeeling, West Bengal"),
    dict(name="Moumita", email="moumita@gmail.com", phone="9345678123", address="Kota, Rajasthan"),
    dict(name="Sayan", email="sayan@gmail.com", phone="8765432190", address="Pune, Maharashtra"),
    dict(name="Samtu", email="samtu@gmail.com", phone="9654321876", address="Siliguri, West Bengal"),
    dict(name="Arpan", email="arpan@gmail.com", phone="9812345678", address="Durgapur, West Bengal"),
    dict(name="Ayesha", email="ayesha@gmail.com", phone="9098765432", address="Bengaluru, Karnataka"),
    dict(name="Aniket", email="aniket@gmail.com", phone="8877665544", address="Guwahati, Assam"),
]

STAFF = [
    dict(name="Rina Staff", email="rina.staff@trekking.com", phone="9911223344", address="Kolkata, West Bengal"),
    dict(name="Debu Staff", email="debu.staff@trekking.com", phone="9822334455", address="Siliguri, West Bengal"),
]

TREKS = [
    dict(name="Inca Trail", country="Peru", location="Cusco", difficulty="Hard",
         total_slots=20, duration_days=4,
         description="A world-famous trek leading to Machu Picchu through ancient Incan ruins."),
    dict(name="Mount Fuji Summit Trail", country="Japan", location="Shizuoka", difficulty="Moderate",
         total_slots=30, duration_days=2,
         description="Iconic volcanic mountain trek with sunrise views from Japan's highest peak."),
    dict(name="Torres del Paine W Trek", country="Chile", location="Patagonia", difficulty="Hard",
         total_slots=25, duration_days=5,
         description="Multi-day trek featuring glaciers, turquoise lakes, and granite towers."),
    dict(name="Mount Kilimanjaro", country="Tanzania", location="Kilimanjaro National Park", difficulty="Hard",
         total_slots=20, duration_days=7,
         description="Africa's highest mountain, through diverse ecosystems to the summit."),
    dict(name="Laitlum Canyons", country="India", location="Shillong, Meghalaya", difficulty="Moderate",
         total_slots=30, duration_days=1,
         description="Scenic canyon with breathtaking viewpoints, ideal for hiking and photography."),
    dict(name="Malshej Ghat", country="India", location="Maharashtra", difficulty="Easy",
         total_slots=40, duration_days=1,
         description="Popular mountain pass known for waterfalls and misty landscapes."),
    dict(name="Bumla Pass", country="India", location="Arunachal Pradesh", difficulty="Hard",
         total_slots=20, duration_days=2,
         description="High-altitude pass near the India-China border with Himalayan views."),
    dict(name="Sonamarg", country="India", location="Jammu & Kashmir", difficulty="Moderate",
         total_slots=35, duration_days=2,
         description="Alpine valley offering glacier walks and stunning landscapes."),
]


def _username_from_email(email):
    """'ram@gmail.com' -> 'ram'. Our User model needs a unique username."""
    return email.split("@")[0]


def seed_trekkers():
    created = 0
    for t in TREKKERS:
        if User.query.filter_by(email=t["email"]).first():
            continue

        user = User(
            name=t["name"],
            username=_username_from_email(t["email"]),
            email=t["email"],
            phone=t["phone"],
            address=t["address"],
            role="user",
        )
        user.set_password(DEFAULT_PASSWORD)

        db.session.add(user)
        created += 1

    db.session.commit()
    print(f"[seed] Trekkers -> {created} created, {len(TREKKERS) - created} already existed")


def seed_staff():
    created = 0
    for s in STAFF:
        if User.query.filter_by(email=s["email"]).first():
            continue

        staff_user = User(
            name=s["name"],
            username=_username_from_email(s["email"]),
            email=s["email"],
            phone=s["phone"],
            address=s["address"],
            role="staff",
        )
        staff_user.set_password(DEFAULT_PASSWORD)

        db.session.add(staff_user)
        created += 1

    db.session.commit()
    print(f"[seed] Staff -> {created} created, {len(STAFF) - created} already existed")


def seed_treks():
    today = datetime.date.today()
    created = 0

    for i, t in enumerate(TREKS):
        if Trek.query.filter_by(name=t["name"]).first():
            continue

        start = today + datetime.timedelta(days=14 + i * 3)
        end = start + datetime.timedelta(days=t["duration_days"] - 1)

        trek = Trek(
            name=t["name"], country=t["country"], location=t["location"],
            difficulty=t["difficulty"], total_slots=t["total_slots"],
            available_slots=t["total_slots"], duration_days=t["duration_days"],
            status="Pending", start_date=start, end_date=end,
            description=t["description"],
        )
        db.session.add(trek)
        created += 1

    db.session.commit()
    print(f"[seed] Treks -> {created} created, {len(TREKS) - created} already existed")


def seed_data():
    seed_trekkers()
    seed_staff()
    seed_treks()