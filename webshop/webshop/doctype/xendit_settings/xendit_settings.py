import frappe
from frappe.model.document import Document
from frappe import _
import json
import base64
from frappe.utils import get_url, add_days, now_datetime
from frappe.integrations.utils import make_post_request

class XenditSettings(Document):
	def get_api_key(self):
		if self.test_mode:
			return self.get_password("secret_api_key")
		return self.get_password("secret_api_key")

	def get_payment_url(self, **kwargs):
		"""
		Standard Entry point for Payment Request.
		"""
		pr_name = kwargs.get("name") or kwargs.get("order_id")
		payment_request = frappe.get_doc("Payment Request", pr_name)
		self.create_payment_request(payment_request)
		# Return a dummy URL or redirect to success page
		return get_url(f"/order/{payment_request.reference_name}/checkout")

	def create_payment_request(self, payment_request):
		"""
		Create a Virtual Account via Xendit API.
		"""
		self.validate_payment_request(payment_request)

		api_key = self.get_api_key()
		
		# Properly encode API key for Basic authentication
		# Xendit requires: Authorization: Basic <base64(api_key:)>
		api_key_with_colon = f"{api_key}:"
		encoded_api_key = base64.b64encode(api_key_with_colon.encode()).decode('utf-8')
		
		headers = {
			"Authorization": f"Basic {encoded_api_key}",
			"Content-Type": "application/json"
		}

		# Determine Expiration Date (Default 1 day if not specified)
		expiration_date = add_days(now_datetime(), 1)
		
		payload = {
			"external_id": payment_request.name,
			"bank_code": payment_request.payment_channel_code,
			"name": payment_request.party_name or "Customer",
			"is_closed": True,
			"expected_amount": payment_request.grand_total,
			"expiration_date": expiration_date.isoformat()
		}

		# Prepare request log data
		request_log_data = {
			"url": "https://api.xendit.co/callback_virtual_accounts",
			"headers": headers,
			"payload": payload
		}

		# Create Integration Request Log manually (without using create_request_log which commits)
		# This allows the caller to control the transaction and rollback if needed
		integration_request = frappe.get_doc({
			"doctype": "Integration Request",
			"integration_request_service": "Xendit",
			"request_description": f"Create VA for {payment_request.name}",
			"data": json.dumps(payload),
			"reference_doctype": "Payment Request",
			"reference_docname": payment_request.name
		})
		integration_request.insert(ignore_permissions=True)
		# NOTE: Do NOT commit here - let the caller control the transaction
		
		# Store the integration request for later updates
		# frappe.db.commit()  # Commit the integration request creation

		try:
			# Make API Request using Frappe's integration utilities
			# This automatically stores the response in frappe.flags.integration_request
			response_data = make_post_request(
				url="https://api.xendit.co/callback_virtual_accounts",
				headers=headers,
				json=payload
			)
			
			# Get the response object from frappe.flags
			response = frappe.flags.integration_request

			# Store complete request and response information
			log_data = {
				"request": request_log_data,
				"response": {
					"status_code": response.status_code,
					"headers": dict(response.headers),
					"body": response_data
				}
			}

			# Update Payment Request with response data
			# payment_request.db_set("virtual_account_number", response_data.get("account_number"))
			# payment_request.db_set("virtual_account_bank", response_data.get("bank_code"))
			# frappe.db.set_value("Payment Request", payment_request.name, "virtual_account_number", response_data.get("account_number"))
			# frappe.db.set_value("Payment Request", payment_request.name, "virtual_account_bank", response_data.get("bank_code"))
			
			# Parse expiration date
			expiry_str = response_data.get("expiration_date")
			if expiry_str:
				from frappe.utils import get_datetime
				# Remove Z if present as get_datetime might handle it or not depending on version
				if expiry_str.endswith("Z"):
					expiry_str = expiry_str[:-1]
				expiry_date = get_datetime(expiry_str)
				payment_request.db_set("payment_due_date", expiry_date)
				
			payment_request.db_set("status", "Requested")
			
			# Update Integration Request with complete log and mark as completed
			integration_request.db_set("status", "Completed", update_modified=False)
			integration_request.db_set("output", json.dumps(log_data, indent=2), update_modified=False)
			# NOTE: Do NOT commit here - let the caller control the transaction
			# This allows proper rollback if subsequent operations fail

			return response_data

		except Exception as e:
			# Get the response from frappe.flags if available
			response = frappe.flags.get("integration_request")
			
			error_data = {
				"request": request_log_data,
				"error_type": type(e).__name__,
				"error_message": str(e),
				"traceback": frappe.get_traceback()
			}
			
			# Add response details if available
			if response is not None:
				try:
					response_body = response.json()
				except:
					response_body = response.text if hasattr(response, 'text') else str(response)
					
				error_data["response"] = {
					"status_code": response.status_code if hasattr(response, 'status_code') else None,
					"headers": dict(response.headers) if hasattr(response, 'headers') else {},
					"body": response_body
				}
			
			# Update integration request with error details
			integration_request.db_set("status", "Failed", update_modified=False)
			integration_request.db_set("error", json.dumps(error_data, indent=2), update_modified=False)
			integration_request.db_set("output", json.dumps(error_data, indent=2), update_modified=False)
			# NOTE: Do NOT commit here - the caller will handle the rollback
			# Committing here would persist the Sales Order before the error is thrown
			
			frappe.log_error(title="Xendit VA Creation Failed", message=json.dumps(error_data, indent=2))
			frappe.throw(_("Failed to create Virtual Account: {0}").format(str(e)))

	def validate_payment_request(self, payment_request):
		if not payment_request.payment_channel_code:
			frappe.throw(_("Payment Channel Code is required for Xendit VA creation."))

@frappe.whitelist(allow_guest=True)
def handle_webhook():
	"""
	Handle Xendit Webhooks.
	"""
	data = frappe.request.get_json()
	
	# Validation
	if not data:
		return

	settings = frappe.get_doc("Xendit Settings")

	# Verify Token
	token = settings.webhook_token
	request_token = frappe.request.headers.get("x-callback-token")
	if token and request_token != token:
		frappe.throw(_("Invalid Webhook Token"), frappe.PermissionError)

	external_id = data.get("external_id")
	status = data.get("status")

	if not external_id:
		return

	try:
		payment_request = frappe.get_doc("Payment Request", external_id)
	except frappe.DoesNotExistError:
		return

	if status == "COMPLETED" or data.get("payment_id"): # Adjust based on actual Xendit Callback payload for FVA Paid
		# Xendit "Paid" callback for FVA usually has 'amount', 'id', etc. 
		# Assuming this is the 'Payment' callback, not 'Created' callback.
		# For FVA, Xendit sends a callback when payment is received.
		
		# Ensure Payment Request is submitted before processing
		# docstatus: 0=Draft, 1=Submitted, 2=Cancelled
		if payment_request.docstatus != 1:
			frappe.log_error(
				f"Payment Request {payment_request.name} is not submitted (docstatus={payment_request.docstatus})",
				"Xendit Webhook: Payment Request Not Submitted"
			)
			return {"status": "error", "message": "Payment Request not submitted"}
		
		# Check if already paid to avoid double processing
		# Check both status field and outstanding_amount
		if payment_request.status == "Paid" or payment_request.get("outstanding_amount", payment_request.grand_total) <= 0:
			return {"status": "already_processed"}

		# Webhooks are authenticated via token, so this is safe
		frappe.set_user("xendit_integration@system.local")
		
		# Reuse Standard Logic
		payment_request.run_method("set_as_paid")
		
		return {"status": "success"}

	return {"status": "ignored"}

@frappe.whitelist()
def simulate_va_payment(payment_request_name):
	settings = frappe.get_doc("Xendit Settings")
	payment_request = frappe.get_doc("Payment Request", payment_request_name)
	api_key = settings.get_api_key()
	
	# Validate
	if not api_key:
		frappe.throw(_("API Key not found"))
		
	# Prepare Headers
	api_key_with_colon = f"{api_key}:"
	encoded_api_key = base64.b64encode(api_key_with_colon.encode()).decode('utf-8')
	
	headers = {
		"Authorization": f"Basic {encoded_api_key}",
		"Content-Type": "application/json"
	}
	
	# URL for simulation
	url = f"https://api.xendit.co/callback_virtual_accounts/external_id={payment_request.name}/simulate_payment"
	
	# Payload
	payload = {
		"amount": payment_request.grand_total
	}
	
	try:
		response = make_post_request(
			url=url,
			headers=headers,
			json=payload
		)
		return response
	except Exception as e:
		frappe.log_error(title="Xendit VA Simulation Failed", message=str(e))
		frappe.throw(_("Simulation Failed: {0}").format(str(e)))
