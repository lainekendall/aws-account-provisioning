import boto3, time, json, string, random
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
import final


new_account_key = 'AKIAJN2ULCJCKKOVOYSQ'
new_account_secret_key = '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'
client_iam_new = boto3.client('iam', aws_access_key_id=new_account_key, aws_secret_access_key=new_account_secret_key, region_name='us-east-1')

def delete_credentials():
	client_ddb.delete_item(
	    TableName=credentials_table_name,
	    Key={
	        credentials_primary_key: {
	            'S': new_account_number
	        }
	    }
	)

def delete_password_policy():
 	client_iam_new.update_account_password_policy(
      MinimumPasswordLength=8,
      RequireSymbols=True,
      RequireNumbers=True,
      RequireUppercaseCharacters=True,
      RequireLowercaseCharacters=True,
      AllowUsersToChangePassword=False,
      MaxPasswordAge=30,
      HardExpiry=False, 
	)

def delete_alias():  
	client_iam_new.create_account_alias(
	AccountAlias='adsk-eis-training-nonprd'		
	)

def delete_sns_cfn():
	for region in new_default_regions:
		cfn_sns_topic_arn = 'arn:aws:sns:' +  region + ':' + new_account_number + ':' + cfn_sns_topic_name
		client_sns = boto3.client('sns', aws_access_key_id=new_account_key, aws_secret_access_key=new_account_secret_key, region_name=region)
		client_sns.delete_topic(
		TopicArn=cfn_sns_topic_arn, 
		)

def lambda_get_policy():
	global policy
	policy = client_lambda.get_policy(
	FunctionName=lambda_vpc_func_name
	)['Policy']
	policy = json.loads(policy)
	return policy

def delete_s3_act_auto():
	client_s3.delete_object(
    Bucket=account_automation_bucket_name,
    Key=s3_automation_file_name,
)
def delete_lambda_policy():
	policy = client_lambda.get_policy(
	FunctionName=lambda_vpc_func_name
	)['Policy']
	policy = json.loads(policy)
	statements = policy['Statement']
	list_of_sids = []
	for statement in statements:
		list_of_sids += [str(statement['Sid'])]
	for sid in list_of_sids:
		client_lambda.remove_permission(
			FunctionName=lambda_vpc_func_name,
			StatementId=sid
			)

def delete_stack():
	for region in new_default_regions:
		client_cfn = boto3.client('cloudformation', aws_access_key_id=new_account_key, aws_secret_access_key=new_account_secret_key, region_name=region)
		stacks = client_cfn.describe_stacks()
		for stack in stacks:
			stack_name = stacks['Stacks'][0]['StackName']
			client_cfn.delete_stack(
			    StackName=stack_name
			)
			
def disable_ec2():
	for region in new_default_regions:
		client_cfn = boto3.client('cloudformation', aws_access_key_id=new_account_key, aws_secret_access_key=new_account_secret_key, region_name=region)
		client_ec2 = boto3.client('ec2', aws_access_key_id=new_account_key, aws_secret_access_key=new_account_secret_key, region_name=region)
		instances = client_ec2.describe_instances(
		    DryRun=False,
		    MaxResults=123
		)
		for instance in instances['Reservations']:
			instance_id = instance['Instances'][0]['InstanceId']
			print(instance_id)
			if instance['Instances'][0]['State']['Name'] in ['running', 'pending', 'stopping', 'stopped']:
				print('not terminated')
				client_ec2.modify_instance_attribute(
				    DryRun=False,
				    InstanceId=instance_id,
				    Attribute='disableApiTermination',
				    Value='False',
				)

def delete_parameters():
	client_ddb.delete_item(
	    TableName=parameters_table_name,
	    Key={
	        parameters_primary_key: {'S': new_account_number}
	    }
	)

def delete_bucket_policy(service):
	client_s3.put_bucket_policy(
	    Bucket=cloudtrail_bucket_name,								
	    Policy= json.dumps(dummy_cloudtrail_bucket_policy)
	)
	client_s3.put_bucket_policy(
	    Bucket=config_bucket_name,								
	    Policy= json.dumps(dummy_config_bucket_policy)
	)
# 
# delete_bucket_policy('cloudtrail')
# delete_bucket_policy('config')

def delete_sns_cloudtrail():
	for region in region_names_list:
		cloudtrail_sns_topic_arn = 'arn:aws:sns:' +  region + ':' + new_account_number + ':' + cloudtrail_sns_topic_name
		client_sns = boto3.client('sns', aws_access_key_id=new_account_key, aws_secret_access_key=new_account_secret_key, region_name=region)
		client_sns.delete_topic(
		TopicArn=cloudtrail_sns_topic_arn, 
		)

def delete_cloudtrail():
	for region in region_names_list:
		client_ct = boto3.client('cloudtrail', aws_access_key_id=new_account_key, aws_secret_access_key=new_account_secret_key, region_name=region)
		client_ct.delete_trail(Name=cloudtrail_name)

def delete_config_role():
	client_iam_new.delete_role_policy(
    	RoleName=config_role_name,
    	PolicyName=config_role_policy_name)
	client_iam_new.delete_role(
		RoleName=config_role_name)


def delete_config():
    for region in region_names_list:
        client_config = boto3.client('config', aws_access_key_id=new_account_key, aws_secret_access_key=new_account_secret_key, region_name=region) 
        client_config.stop_configuration_recorder(
	        ConfigurationRecorderName=config_recorder_name
        )
        client_config.delete_delivery_channel(
	        DeliveryChannelName=config_delivery_channel_name
        )

def delete_sqs_policy():
	client_sqs.set_queue_attributes(
    QueueUrl=sqs_config_queue_url,
    Attributes={
        'Policy': json.dumps(initial_queue_policy)
    }
    )
	client_sqs.set_queue_attributes(
	QueueUrl=sqs_cloudtrail_queue_url,
	Attributes={
	    'Policy': json.dumps(initial_queue_policy)
	}
	)

def purge_queue():
	client_sqs.purge_queue(
    QueueUrl=sqs_config_queue_url
	)
	client_sqs.purge_queue(
    QueueUrl=sqs_cloudtrail_queue_url
	)

# errors but still works
def delete_sqs_subscriptions_ct():
	for region in region_names_list:
		client_sns = boto3.client('sns', aws_access_key_id=new_account_key, aws_secret_access_key=new_account_secret_key, region_name=region)                        
		subscriptions = client_sns.list_subscriptions()
		for subscription in subscriptions['Subscriptions']:
			if subscription['SubscriptionArn'] != 'PendingConfirmation':
				client_sns.unsubscribe(
					SubscriptionArn=subscription['SubscriptionArn']
				)

def delete_sqs_subscriptions_config():
	for region in region_names_list:
		client_sns = boto3.client('sns', aws_access_key_id=central_account_key, aws_secret_access_key=central_account_secret_key, region_name=region)                        
		subscriptions = client_sns.list_subscriptions()
		for subscription in subscriptions['Subscriptions']:
			client_sns.unsubscribe(
			SubscriptionArn=subscription['SubscriptionArn']
		)
# if index error: no vpc endpoints
def delete_vpc_endpoint():
	for region in new_default_regions:
		client_ec2 = boto3.client('ec2', aws_access_key_id=new_account_key, aws_secret_access_key=new_account_secret_key, region_name=region)
		endpoints = client_ec2.describe_vpc_endpoints(
		DryRun=False
		)
		if len(endpoints['VpcEndpoints']) == 0:
			print('no vpc endpoints in ' + region)
			return
		vpc_endpoint_id = endpoints['VpcEndpoints'][0]['VpcEndpointId']
		client_ec2.delete_vpc_endpoints(
		    DryRun=False,
		    VpcEndpointIds=[
		        vpc_endpoint_id,
		    ]
		)

def delete_saml_provider():
	saml_providers = client_iam_new.list_saml_providers()['SAMLProviderList']
	for saml_provider in saml_providers:
		saml_name = saml_provider['Arn'][40:]
		if saml_name == new_saml_provider_name:
			client_iam_new.delete_saml_provider(
				SAMLProviderArn=saml_provider['Arn']
			)

def delete_saml_role():
	client_iam_new.delete_role_policy(
    	RoleName=new_saml_role_name,
    	PolicyName=new_saml_role_policy_name)	
	client_iam_new.delete_role(
		RoleName=new_saml_role_name)


def variables_print():
	for v in dir(final):
		print(v + ' = final.' + v)

account_automation_bucket_name = final.account_automation_bucket_name
amazon_ec2_full_access_role_policy = final.amazon_ec2_full_access_role_policy
boto3 = final.boto3
botocore = final.botocore
central_account_cloudtrail_folder_arn = final.central_account_cloudtrail_folder_arn
central_account_config_folder_arn = final.central_account_config_folder_arn
central_account_key = final.central_account_key
central_account_number = final.central_account_number
central_account_secret_key = final.central_account_secret_key
central_default_region = final.central_default_region
central_saml_provider_arn = final.central_saml_provider_arn
central_saml_provider_name = final.central_saml_provider_name
cfn_create_stack = final.cfn_create_stack
# cfn_parameters_2az = final.cfn_parameters_2az
# cfn_parameters_3az = final.cfn_parameters_3az
cfn_sns_topic_name = final.cfn_sns_topic_name
cfn_sns_topic_policy = final.cfn_sns_topic_policy
cfn_stack_name = final.cfn_stack_name
client_ddb = final.client_ddb
client_iam_central = final.client_iam_central

client_lambda = final.client_lambda
client_s3 = final.client_s3
client_ses = final.client_ses
client_sns_central = final.client_sns_central
client_sqs = final.client_sqs
client_sts = final.client_sts

client_token_generator = final.client_token_generator
cloudtrail_and_config = final.cloudtrail_and_config
cloudtrail_bucket_arn = final.cloudtrail_bucket_arn
cloudtrail_bucket_name = final.cloudtrail_bucket_name
cloudtrail_global_dict = final.cloudtrail_global_dict
cloudtrail_name = final.cloudtrail_name
cloudtrail_parallelprocess = final.cloudtrail_parallelprocess
cloudtrail_sns_policy_label = final.cloudtrail_sns_policy_label
cloudtrail_sns_topic_name = final.cloudtrail_sns_topic_name
cloudtrail_sns_topic_policy = final.cloudtrail_sns_topic_policy
config_bucket_arn = final.config_bucket_arn
config_bucket_name = final.config_bucket_name
config_delivery_channel_name = final.config_delivery_channel_name
config_parallelprocess = final.config_parallelprocess
config_recorder_name = final.config_recorder_name
config_role_arn = final.config_role_arn
config_role_name = final.config_role_name
config_role_policy = final.config_role_policy
config_role_policy_name = final.config_role_policy_name
config_role_trust_relationship = final.config_role_trust_relationship
config_sns_topic_name = final.config_sns_topic_name
config_sns_topic_policy = final.config_sns_topic_policy
credentials_primary_key = final.credentials_primary_key
credentials_secondary_key = final.credentials_secondary_key
credentials_table_name = final.credentials_table_name
datetime = final.datetime
ddb_add_to_credentials_table = final.ddb_add_to_credentials_table
ddb_add_to_parameters_table = final.ddb_add_to_parameters_table
dummy_cloudtrail_bucket_policy = final.dummy_cloudtrail_bucket_policy
dummy_config_bucket_policy = final.dummy_config_bucket_policy
environment = final.environment

get_credentials_item = final.get_credentials_item
get_queue_url_config = final.get_queue_url_config
get_queue_url_ct = final.get_queue_url_ct
get_service_now_item = final.get_service_now_item
iam_create_alias = final.iam_create_alias
iam_create_config_role = final.iam_create_config_role
iam_password_policy = final.iam_password_policy
iam_saml_provider = final.iam_saml_provider
initial_bucket_policy_cloudtrail = final.initial_bucket_policy_cloudtrail
initial_bucket_policy_config = final.initial_bucket_policy_config
initial_queue_policy = final.initial_queue_policy
json = final.json
lambda_cfn = final.lambda_cfn
lambda_cfn_func_name = final.lambda_cfn_func_name
lambda_create_linked_func_name = final.lambda_create_linked_func_name
lambda_permission_sns_cfn = final.lambda_permission_sns_cfn
lambda_vpc = final.lambda_vpc
lambda_vpc_func_arn = final.lambda_vpc_func_arn
lambda_vpc_func_name = final.lambda_vpc_func_name
multiprocess_map = final.multiprocess_map
multiprocessing = final.multiprocessing
new_account_cloudtrail_folder_arn = final.new_account_cloudtrail_folder_arn
new_account_config_folder_arn = final.new_account_config_folder_arn

new_account_number = final.new_account_number

# new_default_regions = final.new_default_regions
new_role_name = final.new_role_name
new_saml_provider_arn = final.new_saml_provider_arn
new_saml_provider_name = final.new_saml_provider_name
new_saml_role_name = final.new_saml_role_name
new_saml_role_policy = final.new_saml_role_policy
new_saml_role_policy_name = final.new_saml_role_policy_name
os = final.os
parameters_primary_key = final.parameters_primary_key
parameters_secondary_key = final.parameters_secondary_key
parameters_table_name = final.parameters_table_name
project_email_address = final.project_email_address
random = final.random
region_names_list = final.region_names_list
reply_to_email = final.reply_to_email
s3_account_automation_info_put = final.s3_account_automation_info_put
s3_automation_file_name = final.s3_automation_file_name
s3_update_bucket_policy = final.s3_update_bucket_policy
saml_assume_role_policy = final.saml_assume_role_policy
service_now_primary_key = final.service_now_primary_key
service_now_secondary_key = final.service_now_secondary_key
service_now_table_name = final.service_now_table_name
ses_email_mfa = final.ses_email_mfa
ses_email_requestor = final.ses_email_requestor
ses_mfa_email = final.ses_mfa_email
ses_proj_automation_email = final.ses_proj_automation_email
short_project_name = final.short_project_name
sns_create_topic_cfn = final.sns_create_topic_cfn
sns_create_topic_cloudtrail = final.sns_create_topic_cloudtrail
sns_subscribe_lambda_cfn = final.sns_subscribe_lambda_cfn
sqs_cloudtrail_queue_arn = final.sqs_cloudtrail_queue_arn
sqs_cloudtrail_queue_name = final.sqs_cloudtrail_queue_name
sqs_cloudtrail_queue_url = final.sqs_cloudtrail_queue_url
sqs_cloudtrail_sns_confirm_subscriptions = final.sqs_cloudtrail_sns_confirm_subscriptions
sqs_cloudtrail_sns_subscribe = final.sqs_cloudtrail_sns_subscribe
sqs_config_queue_arn = final.sqs_config_queue_arn
sqs_config_queue_name = final.sqs_config_queue_name
sqs_config_queue_url = final.sqs_config_queue_url
sqs_config_sns_subscribe = final.sqs_config_sns_subscribe
sqs_queue_policy = final.sqs_queue_policy
sqs_update_policy = final.sqs_update_policy
string = final.string
support_create_case_enterprise = final.support_create_case_enterprise
support_email_addresses = final.support_email_addresses
sys = final.sys
template_url_2azs = final.template_url_2azs
template_url_3azs = final.template_url_3azs
time = final.time
times = final.times
token_dict = final.token_dict
# transaction_id = final.transaction_id
vpc_create_endpoint = final.vpc_create_endpoint
vpc_endpoint_policy = final.vpc_endpoint_policy



new_account_key = 'AKIAJN2ULCJCKKOVOYSQ'
new_account_secret_key = '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'

