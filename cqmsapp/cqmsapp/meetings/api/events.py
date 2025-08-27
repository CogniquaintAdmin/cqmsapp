import frappe
from cqmsapp.cqmsapp.meetings.providers import teams
from cqmsapp.cqmsapp.meetings.utils.signature import generate_meeting_signature
from cqmsapp.cqmsapp.meetings.utils.audit import notify_misuse

@frappe.whitelist()
def create_meeting_for_interview(docname):
    try:
        doc = frappe.get_doc("Interview", docname)

        if doc.doctype != "Interview":
            # Notify misuse
            notify_misuse(docname)
            frappe.throw("This function can only be used with Interview documents.")

        # Generate current signature of meeting-relevant data
        current_signature = generate_meeting_signature(doc)

        if doc.custom_event_id and doc.custom_meeting_signature == current_signature:
            frappe.msgprint(
                f"Meeting already exists at <a href='{doc.custom_meeting_link}' target='_blank'>{doc.custom_meeting_link}</a>.<br>No changes detected."
            )
            return doc.custom_meeting_link

        # Delete previous meeting if exists
        if doc.custom_event_id:
            teams.delete_event(doc.custom_event_id)

        # Create new Teams meeting
        result = teams.create_event(doc)

        if result.get("status") == "success":
            doc.custom_meeting_link = result["teams_link"]
            doc.custom_event_id = result["event_id"]
            doc.custom_meeting_signature = current_signature
            doc.save()
            frappe.db.commit()
            return doc.custom_meeting_link
        else:
            frappe.throw(f"Failed to create Teams meeting: {result['message']}")

    except Exception as e:
        frappe.log_error(frappe.get_traceback(), "Interview Meeting Link Generation Error")
        raise

