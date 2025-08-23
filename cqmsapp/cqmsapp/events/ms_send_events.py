import frappe
import os
from dotenv import load_dotenv
import requests
import msal
from datetime import datetime

# Load environment variables from .env
load_dotenv()


@frappe.whitelist()
def generate_interview_link(docname):
    """Generate a Teams meeting link from Interview doc and update fields"""
    doc = frappe.get_doc("Interview", docname)

    # Extract details from Interview doc
    candidate_email = doc.get("custom_job_applicant_email")  or 'info@cogniquaint.com'
    candidate_name = doc.get("custom_job_applicant_name")  or 'info@cogniquaint.com'

    # Scheduled date + times → convert to datetime strings
    interview_date = str(doc.get("scheduled_on"))
    interview_start_time = str(doc.get("from_time"))
    interview_end_time = str(doc.get("to_time"))

    # Parse and reformat start time
    start_time = datetime.strptime(interview_start_time, "%H:%M:%S").strftime("%H:%M:%S")
    end_time = datetime.strptime(interview_end_time, "%H:%M:%S").strftime("%H:%M:%S")

    interview_start = f"{interview_date}T{start_time}"
    interview_end = f"{interview_date}T{end_time}"

    subject = f"{doc.interview_round or ''} Interview Invitation - {doc.designation or 'Scheduled'}"

    # Collect interviewer emails from child table `interview_details`
    interviewer_emails = []
    if hasattr(doc, "interview_details"):
        for row in doc.interview_details:
            if row.interviewer:
                interviewer_emails.append(row.interviewer)

    # Call Teams API
    result = create_teams_interview_event(
        candidate_email=candidate_email,
        interview_date=interview_start,
        interview_end=interview_end,
        subject=subject,
        interviewer_emails=interviewer_emails,
        docname=docname
    )

    if result.get("status") == "success":
        link = result.get("teams_link")

        if link:
            doc.custom_meeting_link = link
            doc.save()
            frappe.db.commit()
            return link
    else:
        frappe.throw(f"Failed to create Teams meeting: {result['message']}")

def generate_content(docname):
    """Generate Interview Invitation HTML content with Teams link"""
    doc = frappe.get_doc("Interview", docname)

    # Fetch job title from Job Opening
    job_title = None
    if doc.job_opening:
        job_title = frappe.db.get_value("Job Opening", doc.job_opening, "job_title")

    # Prepare HTML with Jinja-like substitution
    html = f"""
    <!DOCTYPE html>
    <html lang="en">
    <head>
      <meta charset="UTF-8">
      <title>Interview Invitation</title>
      <style>
        body {{
          font-family: 'Segoe UI', Arial, sans-serif;
          background-color: #f4f6f9;
          margin: 0;
          padding: 20px;
          color: #333;
        }}
        .container {{
          max-width: 700px;
          margin: auto;
          background: #fff;
          border-radius: 12px;
          box-shadow: 0 6px 18px rgba(0,0,0,0.08);
          overflow: hidden;
        }}
        .header {{
          background-color: #0d2a63;
          padding: 15px 20px;
          text-align: right;
        }}
        .content {{
          padding: 35px 30px;
          line-height: 1.7;
          font-size: 1rem;
        }}
        .content strong {{
          color: #0d2a63;
        }}
        .interview-table {{
          width: 100%;
          border-collapse: collapse;
          margin: 20px 0;
        }}
        .interview-table td {{
          border: 1px solid #ddd;
          padding: 10px;
          text-align: left;
        }}
        .interview-table th {{
          background-color: #f4f6f9;
          color: #0d2a63;
          border: 1px solid #ddd;
          padding: 10px;
          text-align: left;
        }}
        .footer {{
          background-color: #0d2a63;
          border-radius: 0 0 12px 12px;
          color: white;
          padding: 15px 20px;
          text-align: center;
          font-size: 0.85em;
        }}
        .footer a {{
          color: #1e88e5;
          text-decoration: none;
          margin: 0 5px;
        }}
      </style>
    </head>
    <body>

      <div class="container">
        <!-- Header -->
        <div class="header">
        <img 
            src="https://people.cogniquaint.com/files/Cogniquaint%20Shaping%20Smarter%20Systems%20(250%20x%20180%20px).png" 
            alt="Cogniquaint Logo" 
            height="60"
            onerror="this.style.display='none';"
        />
        </div>

        <!-- Content -->
        <div class="content">
          <p>Dear {doc.custom_job_applicant_name},</p>

          <p>Congratulations! You have been <strong>shortlisted</strong> for the <strong>{doc.interview_round}</strong> for the position of <strong>{doc.designation}</strong> (Job Opening: {job_title}).</p>

          <p>Below are the interview details:</p>

          <table style="width:100%; border-collapse:collapse; margin:20px 0;">
            <tr>
              <th style="border:1px solid #ddd; padding:10px; background-color:#f4f6f9; color:#0d2a63; text-align:left;">Interview Round</th>
              <td style="border:1px solid #ddd; padding:10px; text-align:left;">{doc.interview_round}</td>
            </tr>
            <tr>
              <th style="border:1px solid #ddd; padding:10px; background-color:#f4f6f9; color:#0d2a63; text-align:left;">Designation</th>
              <td style="border:1px solid #ddd; padding:10px; text-align:left;">{doc.designation}</td>
            </tr>
            <tr>
              <th style="border:1px solid #ddd; padding:10px; background-color:#f4f6f9; color:#0d2a63; text-align:left;">Scheduled On</th>
              <td style="border:1px solid #ddd; padding:10px; text-align:left;">{doc.scheduled_on} ({doc.from_time} - {doc.to_time})</td>
            </tr>
          </table>

          <p>Please make sure you are available at the scheduled time. The interview will give us an opportunity to learn more about your skills and experience.</p>

          <p>We look forward to speaking with you and discussing how you could contribute to our team.</p>

          <p>Best Regards,<br>
          <strong>People Team</strong><br>
          Cogniquaint Systems</p>
        </div>

        <!-- Footer -->
        <div class="footer">
          © 2025 Cogniquaint Systems Pvt Ltd. All Rights Reserved.  
          <br>
          <a href="https://www.cogniquaint.com">Company</a> |
          <a href="https://www.cogniquaint.com/careers">Careers</a> |
          <a href="mailto:people@cogniquaint.com">Contact</a>
        </div>
      </div>

    </body>
    </html>
    """

    return html

def create_teams_interview_event(
    candidate_email=None,
    interview_date=None,
    interview_end=None,
    subject=None,
    interviewer_emails=None,
    docname = None,
    candidate_name="Candidate"
):
   
    CLIENT_ID = frappe.conf.get("AZURE_CLIENT_ID")
    CLIENT_SECRET = frappe.conf.get("AZURE_CLIENT_SECRET")
    TENANT_ID = frappe.conf.get("AZURE_TENANT_ID")
    ORGANIZER_EMAIL = frappe.conf.get("ORGANIZER_EMAIL")

    # MSAL Authentication
    AUTHORITY = f"https://login.microsoftonline.com/{TENANT_ID}"
    SCOPE = ["https://graph.microsoft.com/.default"]

    app = msal.ConfidentialClientApplication(
        CLIENT_ID, authority=AUTHORITY, client_credential=CLIENT_SECRET
    )
    token = app.acquire_token_for_client(SCOPE)

    if "access_token" not in token:
        return {"status": "error", "message": token.get("error_description")}

    url = f"https://graph.microsoft.com/v1.0/users/{ORGANIZER_EMAIL}/events"

    # Build attendees list
    attendees = []
    if candidate_email:
        attendees.append({
            "emailAddress": {"address": candidate_email, "name": candidate_name},
            "type": "required"
        })
    for email in (interviewer_emails or []):
        if email.strip():
            attendees.append({
                "emailAddress": {"address": email.strip(), "name": "Interviewer"},
                "type": "required"
            })

    content = generate_content(docname)
    payload = {
        "subject": subject or "Interview",
        "body": {
            "contentType": "HTML",
            "content": content
        },
        "start": {"dateTime": interview_date, "timeZone": "India Standard Time"},
        "end": {"dateTime": interview_end, "timeZone": "India Standard Time"},
        "attendees": attendees,
        "isOnlineMeeting": True,
        "onlineMeetingProvider": "teamsForBusiness",
        "sensitivity": "private",
        "allowNewTimeProposals": False,
    }

    headers = {
        "Authorization": "Bearer " + token["access_token"],
        "Content-Type": "application/json"
    }

    response = requests.post(url, headers=headers, json=payload)

    if response.status_code == 201:
        event = response.json()
        return {
            "status": "success",
            "teams_link": event["onlineMeeting"]["joinUrl"],
            "event_id": event["id"]
        }
    else:
        return {
            "status": "error",
            "code": response.status_code,
            "message": response.text
        }
