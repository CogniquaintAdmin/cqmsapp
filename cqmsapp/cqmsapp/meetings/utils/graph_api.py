import frappe
import msal

def get_graph_token():
    CLIENT_ID = frappe.conf.get("AZURE_CLIENT_ID")
    CLIENT_SECRET = frappe.conf.get("AZURE_CLIENT_SECRET")
    TENANT_ID = frappe.conf.get("AZURE_TENANT_ID")
    AUTHORITY = f"https://login.microsoftonline.com/{TENANT_ID}"
    SCOPE = ["https://graph.microsoft.com/.default"]

    app = msal.ConfidentialClientApplication(
        CLIENT_ID, authority=AUTHORITY, client_credential=CLIENT_SECRET
    )

    token = app.acquire_token_for_client(SCOPE)
    return token.get("access_token")
