# Copyright (c) 2024, Frappe Technologies Pvt. Ltd. and contributors
# License: MIT. See LICENSE

import frappe
import json
from frappe.utils import fmt_money


def get_context(context):
    """
    Get context for virtual account checkout page
    """
    context.no_cache = 1

    # Get token from query string
    token = frappe.form_dict.get("token")

    if not token:
        frappe.throw("Invalid payment request")

    context.token = token
    context.integration_request_name = token  # Using token as integration request name

    # Get payment details from integration request
    try:
        integration_request = frappe.get_doc("Integration Request", token)
        data = json.loads(integration_request.data)

        context.payment_details = {
            "amount": data.get("amount"),
            "currency": data.get("currency", "IDR"),
            "title": data.get("title"),
            "description": data.get("description"),
            "payer_name": data.get("payer_name"),
            "payer_email": data.get("payer_email"),
            "reference_docname": data.get("reference_docname"),
            "reference_doctype": data.get("reference_doctype"),
            "formatted_amount": fmt_money(data.get("amount"), currency=data.get("currency", "IDR"))
        }
        
        # Get virtual account details from the integration request
        # In a real implementation, this would come from Midtrans API response
        context.virtual_account_number = data.get("virtual_account_number", "8888000012345678")
        context.bank_name = data.get("bank_name", "BCA")
        context.payment_status = integration_request.status if integration_request.status != "Queued" else "Waiting for payment"
        
        context.integration_request_name = token

    except Exception as e:
        frappe.log_error(frappe.get_traceback())
        frappe.throw("Unable to load payment details")

    return context