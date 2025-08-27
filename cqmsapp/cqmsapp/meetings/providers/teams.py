import frappe
import datetime
import requests
from cqmsapp.cqmsapp.meetings.templates.invitation_content import generate_content
from cqmsapp.cqmsapp.meetings.utils.graph_api import get_graph_token

def create_event(doc):
    ORGANIZER_EMAIL = frappe.conf.get("ORGANIZER_EMAIL")
    access_token = get_graph_token()

    if not access_token:
        return {"status": "error", "message": "Unable to get MS Graph token"}

    candidate_email = doc.custom_job_applicant_email or "info@cogniquaint.com"
    candidate_name = doc.custom_job_applicant_name or "Candidate"


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

    content = generate_content(doc)

    payload = {
        "subject": subject,
        "body": {
            "contentType": "HTML",
            "content": content
        },
        "start": {"dateTime": interview_start, "timeZone": "India Standard Time"},
        "end": {"dateTime": interview_end, "timeZone": "India Standard Time"},
        "attendees": attendees,
        "isOnlineMeeting": True,
        "onlineMeetingProvider": "teamsForBusiness",
        "sensitivity": "private"
    }

    url = f"https://graph.microsoft.com/v1.0/users/{ORGANIZER_EMAIL}/events"
    headers = {
        "Authorization": f"Bearer {access_token}",
        "Content-Type": "application/json"
    }

    res = requests.post(url, headers=headers, json=payload)
    if res.status_code == 201:
        data = res.json()
        return {"status": "success", "teams_link": data["onlineMeeting"]["joinUrl"], "event_id": data["id"]}
    else:
        return {"status": "error", "message": res.text}

def delete_event(event_id):
    ORGANIZER_EMAIL = frappe.conf.get("ORGANIZER_EMAIL")
    access_token = get_graph_token()
    if not access_token:
        return

    url = f"https://graph.microsoft.com/v1.0/users/{ORGANIZER_EMAIL}/events/{event_id}"
    headers = {"Authorization": f"Bearer {access_token}"}
    res = requests.delete(url, headers=headers)
    return res.status_code in [204, 200]
