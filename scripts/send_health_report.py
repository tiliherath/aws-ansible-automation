import os
import smtplib
from email.message import EmailMessage
from pathlib import Path


# ---------------------------------------------------------
# Configuration from GitHub Actions environment variables
# ---------------------------------------------------------

smtp_server = os.environ["SMTP_SERVER"]
smtp_port = int(os.environ["SMTP_PORT"])
smtp_username = os.environ["SMTP_USERNAME"]
smtp_password = os.environ["SMTP_PASSWORD"]

report_email_to = os.environ["REPORT_EMAIL_TO"]


# ---------------------------------------------------------
# Report locations
# ---------------------------------------------------------

html_report = Path("reports/html/health_report.html")
json_report = Path("reports/json/health_report.json")


# ---------------------------------------------------------
# Verify report files exist
# ---------------------------------------------------------

if not html_report.exists():
    raise FileNotFoundError(
        f"HTML report not found: {html_report}"
    )

if not json_report.exists():
    raise FileNotFoundError(
        f"JSON report not found: {json_report}"
    )


# ---------------------------------------------------------
# Create email
# ---------------------------------------------------------

msg = EmailMessage()

msg["Subject"] = "AWS EC2 Health Report"
msg["From"] = smtp_username
msg["To"] = report_email_to


# ---------------------------------------------------------
# Use HTML report as email body
# ---------------------------------------------------------

html_content = html_report.read_text(encoding="utf-8")

msg.set_content(
    "AWS EC2 Health Report is attached. "
    "Please view the HTML report in an email client that supports HTML."
)

msg.add_alternative(html_content, subtype="html")


# ---------------------------------------------------------
# Attach JSON report
# ---------------------------------------------------------

json_content = json_report.read_bytes()

msg.add_attachment(
    json_content,
    maintype="application",
    subtype="json",
    filename="health_report.json",
)


# ---------------------------------------------------------
# Send email using Gmail SMTP
# ---------------------------------------------------------

print("Connecting to SMTP server...")

with smtplib.SMTP(smtp_server, smtp_port) as smtp:
    smtp.ehlo()
    smtp.starttls()
    smtp.ehlo()

    print("Authenticating with SMTP server...")

    smtp.login(smtp_username, smtp_password)

    print("Sending health report email...")

    smtp.send_message(msg)

print("Health report email sent successfully.")