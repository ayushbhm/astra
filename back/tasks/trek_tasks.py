from celery import shared_task
from datetime import datetime, timedelta
from smtplib import SMTP
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email import encoders
from models.model import db, User, Trek, Booking
import csv
import uuid
import os

SMTP_HOST = "localhost"
SMTP_PORT = 1025
SENDER_EMAIL = "noreply@trekapp.com"


def send_message(to, subject, content_body):
    msg = MIMEMultipart()
    msg["To"] = to
    msg["Subject"] = subject
    msg["From"] = SENDER_EMAIL
    msg.attach(MIMEText(content_body, "html"))

    client = SMTP(host=SMTP_HOST, port=SMTP_PORT)
    client.send_message(msg=msg)
    client.quit()


def send_message_with_attachment(to, subject, content_body, file_path):

    msg = MIMEMultipart()
    msg["To"] = to
    msg["Subject"] = subject
    msg["From"] = SENDER_EMAIL
    msg.attach(MIMEText(content_body, "html"))

    filename = file_path.split('/')[-1]

    with open(file_path, "rb") as f:
        part = MIMEBase("text", "csv")
        part.set_payload(f.read())

    encoders.encode_base64(part)
    part.add_header("Content-Disposition", f'attachment; filename="{filename}"')
    msg.attach(part)

    client = SMTP(host=SMTP_HOST, port=SMTP_PORT)
    client.send_message(msg=msg)
    client.quit()


@shared_task(ignore_result=True)
def daily_reminder():

    users = User.query.filter(User.role != "admin" and User.role != "staff").all()

    for user in users:
        body = f"""
            <p>Hi {user.name},</p>

            <p>This is your daily trekking reminder! 🥾</p>

            <p>Check out the latest treks and don't miss exciting adventures waiting for you.</p>

            <p>Log in to TrekApp today to explore new destinations and book your next trek.</p>

            <p>Happy Trekking!</p>
        """

        send_message(
            user.email,
            "Your Daily Trek Reminder",
            body
        )

    return f"Sent reminders to {len(users)} users"


@shared_task(ignore_result=True)
def send_monthly_activity_reports():

    admin = User.query.filter_by(role="admin").first()
    if not admin:
        return "No admin found"

    total_treks = Trek.query.count()
    total_bookings = Booking.query.filter_by(status="Booked").count()

    popular = db.session.query(
        Trek.name, db.func.count(Booking.id).label("count")
    ).join(Booking, Booking.trek_id == Trek.id).group_by(Trek.id).order_by(
        db.text("count DESC")
    ).limit(5).all()

    rows = "".join(f"<tr><td>{name}</td><td>{count}</td></tr>" for name, count in popular)

    body = f"""
        <h2>Monthly Trekking Report</h2>
        <p>Total treks conducted: {total_treks}</p>
        <p>Total users participated: {total_bookings}</p>
        <h3>Popular Treks</h3>
        <table border="1">
            <tr><th>Trek</th><th>Bookings</th></tr>
            {rows}
        </table>
    """

    send_message(admin.email, "Monthly Trekking Activity Report", body)
    return "Monthly report sent"


@shared_task(bind=True)
def export_booking_history(self, user_id):

    os.makedirs("./static/exports", exist_ok=True)

    bookings = Booking.query.filter_by(user_id=user_id).all()

    file_name = f"booking_history_{user_id}_{uuid.uuid4().hex[:8]}.csv"
    file_path = f"./static/exports/{file_name}"

    with open(file_path, mode="w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["User ID", "Trek Name", "Location", "Booking Status", "Start Date", "End Date"])

        for b in bookings:
            trek = Trek.query.get(b.trek_id)
            writer.writerow([user_id, trek.name, trek.location, b.status, trek.start_date, trek.end_date])

    user = User.query.get(user_id)

    if user:
        send_message_with_attachment(
            user.email,
            "Your booking history export is ready",
            "<p>Your export is complete. See attached CSV.</p>",
            file_path
        )

    if os.path.exists(file_path):
        os.remove(file_path)

    return file_name