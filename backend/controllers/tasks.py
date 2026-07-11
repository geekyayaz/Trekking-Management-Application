import csv
import datetime
import io
import os
import smtplib
from email.mime.application import MIMEApplication
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

import requests

from controllers.celery_app import celery
from controllers.models import Booking, Trek, User

# ---------------------------------------------------------------------------
# Notification helpers (email + optional Google Chat webhook)
# ---------------------------------------------------------------------------

SMTP_HOST = os.environ.get("SMTP_HOST", "localhost")
SMTP_PORT = int(os.environ.get("SMTP_PORT", 1025))  # 1025 = python -m smtpd for local testing
SMTP_USER = os.environ.get("SMTP_USER")
SMTP_PASSWORD = os.environ.get("SMTP_PASSWORD")
FROM_EMAIL = os.environ.get("FROM_EMAIL", "no-reply@trekapp.local")
ADMIN_EMAIL = os.environ.get("ADMIN_EMAIL", "admin@trekapp.local")
GCHAT_WEBHOOK_URL = os.environ.get("GCHAT_WEBHOOK_URL")  # optional


def send_email(to_email, subject, html_body, attachment_bytes=None, attachment_name=None):
    msg = MIMEMultipart()
    msg["From"] = FROM_EMAIL
    msg["To"] = to_email
    msg["Subject"] = subject
    msg.attach(MIMEText(html_body, "html"))

    if attachment_bytes is not None:
        part = MIMEApplication(attachment_bytes, Name=attachment_name)
        part["Content-Disposition"] = f'attachment; filename="{attachment_name}"'
        msg.attach(part)

    with smtplib.SMTP(SMTP_HOST, SMTP_PORT) as server:
        if SMTP_USER:
            server.starttls()
            server.login(SMTP_USER, SMTP_PASSWORD)
        server.sendmail(FROM_EMAIL, to_email, msg.as_string())


def send_gchat_message(text):
    if not GCHAT_WEBHOOK_URL:
        return
    try:
        requests.post(GCHAT_WEBHOOK_URL, json={"text": text}, timeout=10)
    except requests.RequestException as e:
        print(f"G-Chat webhook failed: {e}")


# ---------------------------------------------------------------------------
# Task 1: Daily reminder job (Celery Beat, runs every day at 08:00)
# ---------------------------------------------------------------------------

@celery.task(name="controllers.tasks.send_daily_reminders")
def send_daily_reminders():
    """Reminds every user with a Booked booking on a trek starting tomorrow."""
    tomorrow = datetime.date.today() + datetime.timedelta(days=1)

    upcoming_treks = Trek.query.filter(
        Trek.start_date == tomorrow,
        Trek.status == "Open",
    ).all()

    reminders_sent = 0
    for trek in upcoming_treks:
        bookings = trek.booking.filter_by(status="Booked").all()
        for booking in bookings:
            user = booking.user
            subject = f"Reminder: {trek.name} starts tomorrow!"
            body = (
                f"<p>Hi {user.name},</p>"
                f"<p>Your trek <b>{trek.name}</b> in {trek.location} starts tomorrow "
                f"({trek.start_date.isoformat()}).</p>"
                f"<p>Duration: {trek.duration_days} day(s)<br>"
                f"Difficulty: {trek.difficulty}</p>"
                f"<p>Make sure you're packed and ready. See you on the trail!</p>"
            )
            try:
                send_email(user.email, subject, body)
                reminders_sent += 1
            except Exception as e:
                print(f"Failed to email {user.email}: {e}")

            send_gchat_message(f"Reminder sent to {user.name} for trek '{trek.name}'")

    return {"treks_notified": len(upcoming_treks), "reminders_sent": reminders_sent}


# ---------------------------------------------------------------------------
# Task 2: Monthly activity report for Admin (Celery Beat, 1st of month, 06:00)
# ---------------------------------------------------------------------------

@celery.task(name="controllers.tasks.generate_monthly_report")
def generate_monthly_report():
    """Summarizes last month's completed treks and emails an HTML report to admin."""
    today = datetime.date.today()
    first_of_this_month = today.replace(day=1)
    last_month_end = first_of_this_month - datetime.timedelta(days=1)
    last_month_start = last_month_end.replace(day=1)

    completed_treks = Trek.query.filter(
        Trek.status == "Completed",
        Trek.end_date >= last_month_start,
        Trek.end_date <= last_month_end,
    ).all()

    def participant_count(trek):
        return trek.booking.filter_by(status="Completed").count()

    total_participants = sum(participant_count(t) for t in completed_treks)
    popular = sorted(completed_treks, key=participant_count, reverse=True)[:5]

    rows_html = "".join(
        f"<tr><td>{t.name}</td><td>{t.location}</td><td>{participant_count(t)}</td></tr>"
        for t in popular
    ) or "<tr><td colspan='3'>No completed treks this period</td></tr>"

    html_body = f"""
        <h2>Monthly Trekking Activity Report</h2>
        <p>Period: {last_month_start.strftime('%B %Y')}</p>
        <ul>
            <li>Treks conducted: {len(completed_treks)}</li>
            <li>Total participants: {total_participants}</li>
        </ul>
        <h3>Top treks by participation</h3>
        <table border="1" cellpadding="6" cellspacing="0">
            <tr><th>Trek</th><th>Location</th><th>Participants</th></tr>
            {rows_html}
        </table>
    """

    send_email(
        ADMIN_EMAIL,
        f"Monthly Trekking Report - {last_month_start.strftime('%B %Y')}",
        html_body,
    )

    return {"treks_conducted": len(completed_treks), "total_participants": total_participants}


# ---------------------------------------------------------------------------
# Task 3: User-triggered CSV export of booking history (async, on demand)
# ---------------------------------------------------------------------------

@celery.task(name="controllers.tasks.export_booking_history", bind=True)
def export_booking_history(self, user_id):
    """Builds a CSV of the user's booking history, saves it, and emails it."""
    user = User.query.get(user_id)
    if not user:
        return {"error": "User not found"}

    bookings = user.booking.order_by(Booking.booking_date.desc()).all()

    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow(
        ["User ID", "Trek Name", "Location", "Booking Status", "Start Date", "End Date", "Booked On"]
    )
    for b in bookings:
        writer.writerow([
            user.id,
            b.trek.name,
            b.trek.location,
            b.status,
            b.trek.start_date.isoformat(),
            b.trek.end_date.isoformat(),
            b.booking_date.isoformat(),
        ])

    BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))  # project root
    EXPORTS_DIR = os.path.join(BASE_DIR, "exports")

    # ...inside export_booking_history:
    os.makedirs(EXPORTS_DIR, exist_ok=True)
    filename = f"booking_history_user{user_id}_{self.request.id}.csv"
    filepath = os.path.join(EXPORTS_DIR, filename)
    with open(filepath, "w", newline="") as f:
        f.write(output.getvalue())

    try:
        send_email(
            user.email,
            "Your booking history export is ready",
            f"<p>Hi {user.name}, your booking history CSV export is ready. It's attached here.</p>",
            attachment_bytes=output.getvalue().encode(),
            attachment_name=filename,
        )
    except Exception as e:
        print(f"Failed to email export to {user.email}: {e}")

    return {"status": "completed", "file_path": filepath, "filename": filename, "row_count": len(bookings)}