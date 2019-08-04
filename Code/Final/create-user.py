import time, datetime, json, string, random, os, sys # python pre-installed packages
import boto3, botocore # installed packages

new_account_number = '0000000000000'
project_email_address = 'aws.eis.testfour.tst@autodesk.com'
new_role_name = 'PayerAccountAccessRole'


payer_account_key = "***********************"
payer_account_secret_key = "***************************"

client_sts_payer = boto3.client('sts', aws_access_key_id=payer_account_key, aws_secret_access_key=payer_account_secret_key, region_name='us-east-1')

def client_token_generator():
	""" Generates a random token for the VPC S3 endpoint """
	from random import sample
	lower = string.ascii_lowercase
	upper = string.ascii_uppercase
	seed = sample(lower, 6) + sample(upper, 6)
	return ''.join(sample(seed, 6))

def role_access_keys():
	print('access keys start at: ' + str(datetime.datetime.now()))
	global new_account_role_key, new_account_role_secret_key, session_new, client_support_session, client_iam_session_new, client_iam_new

	new_role_arn = 'arn:aws:iam::' + new_account_number + ':role/' + new_role_name
	assume_role_response = client_sts_payer.assume_role(
	    RoleArn=new_role_arn,
	    RoleSessionName='role-session-' + client_token_generator(),
		DurationSeconds=3600)
	new_account_role_key = assume_role_response['Credentials']['AccessKeyId']
	new_account_role_secret_key = assume_role_response['Credentials']['SecretAccessKey']
	new_session_token = assume_role_response['Credentials']['SessionToken']

	session_new = boto3.session.Session(aws_access_key_id=new_account_role_key, aws_secret_access_key=new_account_role_secret_key, aws_session_token=new_session_token)
	client_support_session = session_new.client('support', region_name='us-east-1')
	client_iam_session_new = session_new.client('iam', region_name='us-east-1')
	client_iam_new = client_iam_session_new
	user_name = 'laine'
	# client_iam_new.create_user(
 #    # Path='string',
 #    UserName=user_name
	# )

	# client_iam_new.create_login_profile(
 #    UserName=user_name,
 #    Password='Password2015*',
 #    PasswordResetRequired=False
	# )
	client_iam_new.attach_user_policy(
    UserName=user_name,
    PolicyArn='arn:aws:iam::aws:policy/AdministratorAccess'
	)








