import hashlib
import json

def generate_meeting_signature(doc):
    """Returns a hash of meeting-related fields to detect changes"""
    data = {
        "scheduled_on": str(doc.scheduled_on),
        "from_time": str(doc.from_time),
        "to_time": str(doc.to_time),
        "interview_round": doc.interview_round,
        "designation": doc.designation,
        "interviewer_emails": sorted([row.interviewer.strip() for row in doc.interview_details if row.interviewer])
    }

    json_data = json.dumps(data, sort_keys=True)
    return hashlib.md5(json_data.encode()).hexdigest()
