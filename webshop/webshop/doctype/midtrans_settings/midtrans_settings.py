# Copyright (c) 2024, Frappe Technologies Pvt. Ltd. and contributors
# License: MIT. See LICENSE

"""
# Integrating Midtrans (Test Mode)

This is a test payment gateway that simulates the Midtrans payment flow
without requiring real API keys. Perfect for local testing.

### Usage Example:

    from payments.utils import get_payment_gateway_controller

    controller = get_payment_gateway_controller("Midtrans")

    payment_details = {
        "amount": 100000,
        "title": "Payment for order",
        "description": "Test payment",
        "reference_doctype": "Sales Order",
        "reference_docname": "SO-00001",
        "payer_email": "customer@example.com",
        "payer_name": "Test Customer",
        "order_id": "ORDER-001",
        "currency": "IDR",
        "payment_gateway": "Midtrans"
    }

    # Get payment URL
    url = controller().get_payment_url(**payment_details)
"""

import json
import frappe
from frappe import _
from frappe.model.document import Document
from frappe.integrations.utils import create_request_log
from frappe.utils import get_url, fmt_money
from payments.utils import create_payment_gateway
import requests


class MidtransSettings(Document):
    supported_currencies = ["IDR", "USD", "SGD", "MYR", "THB", "VND"]

    def validate(self):
        """Create payment gateway on save"""
        create_payment_gateway("Midtrans")

        # In test mode, we don't need API keys
        if not self.test_mode and not self.server_key:
            frappe.throw(_("Server Key is required when Test Mode is disabled"))

    def validate_transaction_currency(self, currency):
        """Validate if currency is supported"""
        if currency not in self.supported_currencies:
            frappe.throw(
                _("Please select another payment method. Midtrans does not support transactions in currency '{0}'").format(currency)
            )

    def get_payment_url(self, **kwargs):
        """
        Generate payment URL for Midtrans checkout

        Args:
            amount: Payment amount
            title: Payment title
            description: Payment description
            reference_doctype: Reference document type
            reference_docname: Reference document name
            payer_email: Customer email
            payer_name: Customer name
            order_id: Order ID
            currency: Currency code

        Returns:
            str: Payment checkout URL
        """
        # Create integration request log with virtual account information
        integration_request = create_request_log(kwargs, service_name="Midtrans")

        # In test mode, redirect to our custom virtual account checkout page
        if self.test_mode:
            # Generate a mock virtual account number for testing
            kwargs['virtual_account_number'] = f"8888{str(int(kwargs['amount']))[:8].ljust(8, '0')}"
            kwargs['bank_name'] = "BCA"

            # Update the integration request with virtual account info
            integration_data = json.loads(integration_request.data)
            integration_data.update({
                'virtual_account_number': kwargs['virtual_account_number'],
                'bank_name': kwargs['bank_name']
            })

            integration_request.data = json.dumps(integration_data)
            integration_request.save(ignore_permissions=True)

            return get_url(f"./virtual_account_checkout?token={integration_request.name}")
        else:
            # For production mode, call real Midtrans API to generate virtual account
            return self._get_real_payment_url(integration_request, **kwargs)

    def _get_real_payment_url(self, integration_request, **kwargs):
        """
        Generate real Midtrans payment URL (for production mode)
        This integrates with actual Midtrans Snap API to create virtual account
        """
        try:
            # Prepare the payload for Midtrans API
            payload = self._prepare_midtrans_payload(**kwargs)

            # Determine API URL based on test mode
            api_url = "https://api.sandbox.midtrans.com/v2/charge" if self.test_mode else "https://api.midtrans.com/v2/charge"

            # Set up headers with server key
            headers = {
                "Content-Type": "application/json",
                "Accept": "application/json",
                "Authorization": f"Basic {frappe.safe_decode(frappe.utils.password.get_decrypted_password('Midtrans Settings', self.name, 'server_key', raise_exception=False))}"
            }

            # Make the API request to Midtrans
            response = requests.post(api_url, headers=headers, json=payload)

            if response.status_code == 200:
                result = response.json()

                # Update integration request with virtual account info from Midtrans response
                integration_data = json.loads(integration_request.data)
                integration_data.update({
                    'virtual_account_number': result.get('va_numbers', [{}])[0].get('va_number', ''),
                    'bank_name': result.get('va_numbers', [{}])[0].get('bank', 'BCA'),
                    'payment_id': result.get('transaction_id', ''),
                    'transaction_time': result.get('transaction_time', ''),
                    'transaction_status': result.get('transaction_status', 'pending')
                })

                integration_request.data = json.dumps(integration_data)
                integration_request.save(ignore_permissions=True)

                # Return the URL to our virtual account checkout page
                return get_url(f"./virtual_account_checkout?token={integration_request.name}")
            else:
                frappe.log_error(f"Midtrans API Error: {response.text}")
                frappe.throw(_("Failed to create virtual account. Please try again."))

        except Exception as e:
            frappe.log_error(frappe.get_traceback(), "Midtrans API Error")
            frappe.throw(_("Error creating virtual account: {0}").format(str(e)))

    def _prepare_midtrans_payload(self, **kwargs):
        """
        Prepare the payload for Midtrans API call
        """
        # Get customer information
        customer_details = {
            "first_name": kwargs.get('payer_name', '').split()[0] if kwargs.get('payer_name') else '',
            "last_name": ' '.join(kwargs.get('payer_name', '').split()[1:]) if kwargs.get('payer_name') else '',
            "email": kwargs.get('payer_email', ''),
            "phone": kwargs.get('phone', ''),
        }

        # Prepare item details if available
        item_details = [{
            "id": kwargs.get('order_id', 'order'),
            "price": int(kwargs.get('amount', 0)),
            "quantity": 1,
            "name": kwargs.get('description', kwargs.get('title', 'Order'))
        }]

        # Create the payload
        payload = {
            "payment_type": "bank_transfer",
            "bank_transfer": {
                "bank": "bca"  # Using BCA virtual account as example
            },
            "transaction_details": {
                "order_id": kwargs.get('order_id', kwargs.get('reference_docname', '')),
                "gross_amount": int(kwargs.get('amount', 0))
            },
            "customer_details": customer_details,
            "item_details": item_details
        }

        return payload

    def create_request(self, data):
        """
        Handle payment callback/response

        Args:
            data: Payment response data including token and payment status

        Returns:
            dict: Redirect URL and status
        """
        self.data = frappe._dict(data)

        try:
            self.integration_request = frappe.get_doc("Integration Request", self.data.token)
            self.integration_request.update_status(self.data, "Queued")

            # Set frappe.flags.integration_request for use in authorize_payment
            frappe.flags.integration_request = self.integration_request

            return self.authorize_payment()

        except Exception:
            frappe.log_error(frappe.get_traceback(), "Midtrans Payment Error")
            return {
                "redirect_to": frappe.redirect_to_message(
                    _("Server Error"),
                    _("There was an error processing your payment. Please try again.")
                ),
                "status": 401
            }

    def authorize_payment(self):
        """
        Process payment authorization
        """
        data = json.loads(self.integration_request.data)

        # In test mode, we accept the payment status from the test page
        if self.test_mode or self.data.get("test_mode"):
            payment_status = self.data.get("payment_status", "success")

            if payment_status == "success":
                self.integration_request.update_status(data, "Completed")
                self.flags.status_changed_to = "Completed"
            else:
                self.integration_request.update_status(data, "Failed")
                self.flags.status_changed_to = "Failed"
        else:
            # For production, verify with Midtrans API
            # TODO: Implement real payment verification
            pass

        # Handle post-payment actions
        status = self.integration_request.status
        redirect_to = data.get("redirect_to") or None
        redirect_message = data.get("redirect_message") or None

        if self.flags.status_changed_to == "Completed":
            # Set flag for Payment Request to check if it should create Sales Invoice
            frappe.flags.auto_create_sales_invoice = self.get("auto_create_sales_invoice", 0)

            # Call the reference document's payment authorized method
            if self.data.reference_doctype and self.data.reference_docname:
                custom_redirect_to = None
                try:
                    frappe.flags.data = data
                    custom_redirect_to = frappe.get_doc(
                        self.data.reference_doctype, self.data.reference_docname
                    ).run_method("on_payment_authorized", self.flags.status_changed_to)

                except Exception:
                    frappe.log_error(frappe.get_traceback(), "Midtrans Payment Authorization Error")

                if custom_redirect_to:
                    redirect_to = custom_redirect_to

            # Use absolute path for redirect
            redirect_url = f"/payment-success?doctype={self.data.reference_doctype}&docname={self.data.reference_docname}"
        else:
            redirect_url = "/payment-failed"

        if redirect_to:
            from urllib.parse import urlencode
            redirect_url += "&" + urlencode({"redirect_to": redirect_to})
        if redirect_message:
            from urllib.parse import urlencode
            redirect_url += "&" + urlencode({"redirect_message": redirect_message})

        return {"redirect_to": redirect_url, "status": status}


@frappe.whitelist(allow_guest=True)
def get_checkout_details(token):
    """
    Get payment details for checkout page

    Args:
        token: Integration Request token

    Returns:
        dict: Payment details including amount, currency, description, etc.
    """
    try:
        integration_request = frappe.get_doc("Integration Request", token)
        data = json.loads(integration_request.data)

        return {
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
    except Exception as e:
        frappe.log_error(frappe.get_traceback(), "Midtrans Checkout Details Error")
        frappe.throw(_("Invalid payment request"))


@frappe.whitelist(allow_guest=True)
def check_payment_status(integration_request_name):
    """
    Check payment status for virtual account

    Args:
        integration_request_name: Name of the integration request

    Returns:
        dict: Payment status information
    """
    try:
        integration_request = frappe.get_doc("Integration Request", integration_request_name)
        data = json.loads(integration_request.data)

        # In test mode, we can simulate the payment status
        # In production, this would check the actual Midtrans API
        if frappe.db.get_single_value("Midtrans Settings", "test_mode"):
            # For demo purposes, return status based on some criteria
            # In a real implementation, you'd check with Midtrans API
            status = integration_request.status
            if status == "Completed":
                return {
                    "status": "Completed",
                    "reference_docname": data.get("reference_docname"),
                    "message": "Payment confirmed"
                }
            else:
                return {
                    "status": "Pending",
                    "reference_docname": data.get("reference_docname"),
                    "message": "Waiting for payment"
                }
        else:
            # In production, call Midtrans API to check actual payment status
            midtrans_settings = frappe.get_doc("Midtrans Settings")
            server_key = frappe.utils.password.get_decrypted_password('Midtrans Settings', midtrans_settings.name, 'server_key', raise_exception=False)

            # Use the transaction_id to check status with Midtrans API
            transaction_id = data.get('payment_id')
            if transaction_id:
                api_url = f"https://api.sandbox.midtrans.com/v2/{transaction_id}/status" if midtrans_settings.test_mode else f"https://api.midtrans.com/v2/{transaction_id}/status"

                headers = {
                    "Accept": "application/json",
                    "Authorization": f"Basic {frappe.safe_decode(server_key)}"
                }

                response = requests.get(api_url, headers=headers)

                if response.status_code == 200:
                    result = response.json()
                    status = result.get('transaction_status', 'pending')

                    # Update the integration request status based on Midtrans response
                    integration_request.status = status.capitalize() if status != 'pending' else 'Queued'
                    integration_request.save(ignore_permissions=True)

                    return {
                        "status": status.capitalize() if status != 'pending' else "Pending",
                        "reference_docname": data.get("reference_docname"),
                        "message": f"Transaction status: {status}"
                    }

            # If we can't get status from Midtrans API, return current status
            return {
                "status": integration_request.status,
                "reference_docname": data.get("reference_docname"),
                "message": f"Current status: {integration_request.status}"
            }

    except Exception as e:
        frappe.log_error(frappe.get_traceback(), "Check Payment Status Error")
        return {
            "status": "Error",
            "reference_docname": None,
            "message": str(e)
        }


@frappe.whitelist(allow_guest=True)
def process_payment(token, payment_status):
    """
    Process payment from checkout page

    Args:
        token: Integration Request token
        payment_status: 'success' or 'failed'

    Returns:
        dict: Redirect URL
    """
    controller = frappe.get_doc("Midtrans Settings")

    # Prepare payment data
    payment_data = {
        "token": token,
        "payment_status": payment_status,
        "test_mode": True
    }

    # Add reference doctype and docname from integration request
    integration_request = frappe.get_doc("Integration Request", token)
    data = json.loads(integration_request.data)
    payment_data["reference_doctype"] = data.get("reference_doctype")
    payment_data["reference_docname"] = data.get("reference_docname")

    # Process the payment
    result = controller.create_request(payment_data)

    return result


@frappe.whitelist()
def handle_midtrans_notification():
    """
    Handle Midtrans payment notification (webhook)
    This function should be called by Midtrans when payment status changes
    """
    try:
        # Get JSON payload from request
        request_data = frappe.local.request.get_data()
        notification = json.loads(request_data.decode('utf-8'))

        # Verify the notification with Midtrans
        # In production, you should verify the signature here

        # Get the order ID from the notification
        order_id = notification.get('order_id')

        # Find the related Integration Request
        integration_requests = frappe.get_all(
            'Integration Request',
            filters={'data': ['like', f'%{order_id}%']},
            fields=['name', 'data']
        )

        if integration_requests:
            integration_request = frappe.get_doc('Integration Request', integration_requests[0].name)

            # Update the status based on the notification
            transaction_status = notification.get('transaction_status')
            if transaction_status in ['settlement', 'capture']:
                integration_request.status = 'Completed'
            elif transaction_status == 'cancel':
                integration_request.status = 'Failed'
            elif transaction_status == 'expire':
                integration_request.status = 'Failed'
            elif transaction_status == 'pending':
                integration_request.status = 'Queued'

            integration_request.save(ignore_permissions=True)

            # Update the related Payment Request status
            data = json.loads(integration_request.data)
            payment_request = frappe.get_all(
                'Payment Request',
                filters={
                    'reference_doctype': data.get('reference_doctype'),
                    'reference_name': data.get('reference_docname')
                }
            )

            if payment_request:
                pr = frappe.get_doc('Payment Request', payment_request[0].name)
                if transaction_status in ['settlement', 'capture']:
                    # Complete the payment
                    pr.run_method('set_as_paid')
                elif transaction_status in ['cancel', 'expire']:
                    # Mark as failed
                    pr.db_set('status', 'Failed')

            frappe.db.commit()

        return {'status': 'OK'}

    except Exception as e:
        frappe.log_error(frappe.get_traceback(), "Midtrans Notification Error")
        frappe.log_error(f"Notification data: {request_data}", "Midtrans Notification Error")
        return {'status': 'ERROR', 'message': str(e)}
