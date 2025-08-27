import frappe

def notify_misuse(docname):
    """Notify internal team about misuse of meeting creation endpoint"""
    subject = "Misuse of Meeting Link Generation"
    message = f"""
    The create_meeting_for_interview function was called with a non-Interview docname: <strong>{docname}</strong><br><br>
    Please check if a button or script is misconfigured.
    """

    frappe.sendmail(
        recipients=["people@cogniquaint.com"],
        subject=subject,
        message=message
    )