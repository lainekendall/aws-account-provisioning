def ses_email_requestor(): 
	""" Sends email to the requestor notifying him/her that the account has been successfully provisioned """
	client_ses.send_email(
		Source=ses_proj_automation_email,
		Destination={
		'ToAddresses': [
		creator_email,
		],
		'CcAddresses': [
		ses_proj_automation_email,
		]
		},
		Message={ 
		'Subject': {
		'Data': 'Your AWS account has been provisioned'#,
		# 'Charset': 'string'
		},
		'Body': {
		'Text': {
		'Data': 'Your Amazon Web Services Account has been successfully provisioned. Your account number is ' + new_account_number + ', Your account email address is ' + project_email_address + '. Go to awsconsole.autodesk.com and log in with your AD admin credentials.'
		},
		}
		},
		ReplyToAddresses=[
		reply_to_email,
		]
	)
  
def ses_email_mfa():
	""" Emails the MFA person to have MFA enabled in the  new account """
	client_ses.send_email(
		Source=ses_proj_automation_email,
		Destination={
		'ToAddresses': [
		ses_mfa_email,
		],
		'CcAddresses': [
		ses_proj_automation_email,
		]
		},
		Message={
		'Subject': {
		'Data': 'MFA for AWS account'
		},
		'Body': { 
		'Text': {
		'Data': 'Please create email address, form AD security group, and have MFA enabled for the account with the following information: ' + 'ACCOUNT NUMBER= ' + new_account_number 
		+ ', SHORTNAME FOR THE PROJECT= ' + short_project_name + ',  EMAIL ADDRESS: ' + project_email_address + ', ENVIRONMENT= ' + environment
		+ ', SERVICENOW TRANSACTION ID= ' + transaction_id 
		}
		}
		},
		ReplyToAddresses=[
		reply_to_email,
		]
	)