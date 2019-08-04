import boto3, json

## code: ##
# cloudtrail()

# configures cloudtrail, deletes cloudtrail
central_account_key = '************************'
central_account_secret_key = '*************************************'
new_account_key = '************************'
new_account_secret_key = '*********************************************'
central_account_number = '00000000000000000'
new_account_number = '000000000000000000'

cloudtrail_sns_topic_name = 'intern-test-cloudtrail-notifications'
cloudtrail_name = 'intern-training-trail-name'
s3_bucket_name = 'intern-test-cloudtrail'						# (adsk-eis-cloudtrail)
s3_prefix = ''													# folder in bucket (after this will be foler name 'AWSLogs' then account #)
sns_policy_label = 'cloudtrail sns policy label'

region_names_list = ['us-east-1', 'us-west-1', 'us-west-2', 
'eu-west-1', 'eu-central-1', 'ap-southeast-1', 'ap-northeast-1', 
'ap-southeast-2', 'sa-east-1']

global_dict = {'us-east-1': True, 'us-west-2': False, 'us-west-1': False, 
'eu-west-1': False, 'eu-central-1': False, 'ap-southeast-1': False, 'ap-northeast-1': False, 
'ap-southeast-2': False, 'sa-east-1': False}

def cloudtrail():
	for region in region_names_list:
		client_ct = boto3.client('cloudtrail', aws_access_key_id=new_account_key, aws_secret_access_key=new_account_secret_key, region_name=region)
		client_ct.create_trail(Name=cloudtrail_name,		# name for trail can be anything (if not given will be 'Default')
	    S3BucketName=s3_bucket_name,		
	    # S3KeyPrefix=s3_prefix,				# not sure about this yet
	    SnsTopicName=cloudtrail_sns_topic_name,		# change this
	    IncludeGlobalServiceEvents=global_dict[region],				
		)
		client_ct.start_logging(
	    Name=cloudtrail_name			
		)

def delete_cloudtrail():
	for region in region_names_list:
		client_ct = boto3.client('cloudtrail', aws_access_key_id=new_account_key, aws_secret_access_key=new_account_secret_key, region_name=region)
		client_ct.delete_trail(Name=cloudtrail_name)			# must be same as Name in start_logging and create_trail 


