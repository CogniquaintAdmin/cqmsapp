import requests
import frappe
from dotenv import load_dotenv


# Load environment variables from .env
load_dotenv()

GSTINCHECK_BASE_URL = "https://sheet.gstincheck.co.in/check"


def get_gstin_details(gstin: str) -> dict:
    """
    Fetch GSTIN details from GSTINCheck API
    """
    api_key = frappe.conf.get("gstincheck_api_key") or "ac529be4eb6fed716c067b38bce82044"

    if not api_key or api_key == "ac529be4eb6fed716c067b38bce82044":
        frappe.throw("GSTINCheck API key not configured in site_config.json")

    url = f"{GSTINCHECK_BASE_URL}/{api_key}/{gstin}"

    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        data = response.json()

    except requests.exceptions.RequestException:
        frappe.log_error(frappe.get_traceback(), "GSTIN API Error")
        frappe.throw("Unable to connect to GST verification service")

    if not data.get("flag"):
        return {
            "success": False,
            "message": data.get("message", "GSTIN not found")
        }

    gst_data = data.get("data", {})

    return {
        "success": True,
        "gstin": gst_data.get("gstin"),
        "legal_name": gst_data.get("lgnm"),
        "trade_name": gst_data.get("tradeNam"),
        "status": gst_data.get("sts"),
        "constitution": gst_data.get("ctb"),
        "registration_date": gst_data.get("rgdt"),
        "business_type": gst_data.get("nba"),
        "state_code": gst_data.get("pradr", {}).get("addr", {}).get("stcd"),
        "address": gst_data.get("pradr", {}).get("adr"),
        "einvoice_enabled": gst_data.get("einvoiceStatus")
    }


@frappe.whitelist()
def update_supplier_from_gst(supplier: str, gstin: str):
    """
    Fetch GST details and update Supplier doctype
    """

    if not supplier or not gstin:
        frappe.throw("Supplier and GSTIN are required")

    gst_response = get_gstin_details(gstin)

    if not gst_response.get("success"):
        sup.gst_category = "Unregistered"

    sup = frappe.get_doc("Supplier", supplier)

    # ---- Update Supplier Fields ----
    sup.gstin = gst_response.get("gstin")
    sup.supplier_name = gst_response.get("legal_name")
    sup.gst_category = "Registered Regular"
    sup.tax_id = gst_response.get("gstin")

    # Optional custom fields (recommended)
    if hasattr(sup, "trade_name"):
        sup.trade_name = gst_response.get("trade_name")

    if hasattr(sup, "gst_status"):
        sup.gst_status = gst_response.get("status")

    if hasattr(sup, "constitution_of_business"):
        sup.constitution_of_business = gst_response.get("constitution")

    sup.save(ignore_permissions=True)

    return {
        "message": "Supplier updated successfully from GST",
        "supplier": sup.name,
        "gst_details": gst_response
    }
