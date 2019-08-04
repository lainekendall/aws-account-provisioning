import time, datetime, json, string, random, os, sys # python pre-installed packages
import boto3 # installed packages
central_account_number = '0000000000000'
central_account_key = '*******************'
central_account_secret_key = '**************************************'
central_default_region = 'us-east-1'


client_s3 = boto3.client('s3', aws_access_key_id=central_account_key, aws_secret_access_key=central_account_secret_key, region_name=central_default_region)

s3_config_bucket_name = 'adsk-eis-awsconfig'
s3_cloudtrail_bucket_name = 'adsk-eis-cloudtrail'
s3_account_automation_bucket_name = 'adsk-eis-accountautomation'
s3_account_automation_folder_name = 'logs'
s3_automation_file_name = 'automation.log'


def s3_account_automation_info_put():
	try:
		current = client_s3.get_object(
		    Bucket=s3_account_automation_bucket_name,
		    Key=s3_automation_file_name,
		)['Body'].read()
		current += times
	except botocore.exceptions.ClientError:
		current = times
		pass
	client_s3.put_object(
	    ACL='private', # |'public-read'|'public-read-write'|'authenticated-read'|'bucket-owner-read'|'bucket-owner-full-control'
	    Body=current,
	    Bucket=s3_account_automation_bucket_name,
	    Key=s3_account_automation_folder_name + '/' + s3_automation_file_name,	# name for the object
	    StorageClass='STANDARD',
	)
	print('account automation times file put into s3 and is x long: ' + str(len(current)))
