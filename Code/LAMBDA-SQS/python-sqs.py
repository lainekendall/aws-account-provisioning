import time, datetime, json, string, random, os, sys # python pre-installed packages
import boto3, botocore # installed packages

def client_token_generator():
	""" Generates a random token for the VPC S3 endpoint """
	from random import sample
	lower = string.ascii_lowercase
	upper = string.ascii_uppercase
	seed = sample(lower, 6) + sample(upper, 6)
	return ''.join(sample(seed, 6))

#### for testing: (when not gotten from lambda js, or assume role) ###########
## ALL



######### 2: CENTRAL acount variables #########
##############################################################################
central_account_number = '0000000000000'
central_account_key = '*******************'
central_account_secret_key = '**************************************'
central_default_region = 'us-east-1'

payer_account_key = "***********************"
payer_account_secret_key = "***************************"

## DDB tables ##

service_now_table_name = 'aa-servicenowinput'
service_now_primary_key = 'EmailAddress'

credentials_table_name = 'aa-accountdetails'
credentials_primary_key = 'AccountNumber'

parameters_table_name = 'aa-cfnparameters'
parameters_primary_key = 'AccountNumber'

## SQS ##
sqs_cloudtrail_queue_name = 'cloudtrail-notifications'
sqs_config_queue_name = 'config-notifications'

## S3 Buckets/urls ##
s3_config_bucket_name = 'adsk-eis-awsconfig'
s3_cloudtrail_bucket_name = 'adsk-eis-cloudtrail'
s3_account_automation_bucket_name = 'adsk-eis-accountautomation'

cfn_template_url_2azs = 'https://s3.amazonaws.com/adsk-eis-accountautomation/configs/core-2az.json'
cfn_template_url_3azs = 'https://s3.amazonaws.com/adsk-eis-accountautomation/configs/core-3az.json'


## SNS Topics ##
sns_config_topic_name = 'config-notifications'

## Lambda ##
lambda_create_linked_func_name = 'aa-cla'
lambda_cfn_func_name = 'aa-cfn'
lambda_vpc_func_name = 'aa-vpc'
lambda_config_func_name = 'aa-config'
lambda_sqs_func_name = 'aa-sqs'

## IAM ##
saml_provider_name = 'adsk-saml'        
central_saml_provider_arn = 'arn:aws:iam::' + central_account_number + ':saml-provider/' + saml_provider_name

## Email these people ##
support_email_addresses = ['laine.kendall@autodesk.com']    # list of strings
ses_proj_automation_email = 'laine.kendall@autodesk.com' # 'eis.aws.support@autodesk.com'
ses_mfa_email = 'laine.kendall@autodesk.com'
reply_to_email = 'laine.kendall@autodesk.com'


####### 3: NAME THESE #####
######################################################################
config_role_name = 'config-role'
config_role_policy_name = 'config-role-policy'
config_delivery_channel_name = 'config-delivery-channel'
config_recorder_name = 'config-recorder'

cfn_stack_name = 'core'
sns_cfn_topic_name = 'cfncore-notifications'

sns_cloudtrail_topic_name = 'cloudtrail-notifications'
cloudtrail_name = 'adsk-eis-cloudtrail'
cloudtrail_sns_policy_label = 'cloudtrail sns policy label'

new_saml_provider_name = 'adsk-saml'
new_saml_role_name = 'adsk-saml-role'
new_saml_role_policy_name = 'adsk-saml-role-policy'

s3_automation_file_name = 'accountautomation'


######### 4: DO NOT CHANGE: all variables below this do not have to be changed #############################################
##############################################################################
region_names_list = ['us-east-1', 'us-west-1', 'us-west-2', 
'eu-west-1', 'eu-central-1', 'ap-southeast-1', 'ap-northeast-1', 
'ap-southeast-2', 'sa-east-1']
cloudtrail_global_dict = {'us-east-1': True, 'us-west-2': False, 'us-west-1': False, 
'eu-west-1': False, 'eu-central-1': False, 'ap-southeast-1': False, 'ap-northeast-1': False, 
'ap-southeast-2': False, 'sa-east-1': False}


##### 5: CENTRAL ARNs ###### 
######################################################################
config_bucket_arn = 'arn:aws:s3:::' + s3_config_bucket_name
cloudtrail_bucket_arn = 'arn:aws:s3:::' + s3_cloudtrail_bucket_name
sqs_config_queue_arn = "arn:aws:sqs:" + central_default_region + ":" + central_account_number + ":" + sqs_config_queue_name
sqs_cloudtrail_queue_arn = "arn:aws:sqs:" + central_default_region + ":" + central_account_number + ":" + sqs_cloudtrail_queue_name

# this is all for policy stuff: #
lambda_vpc_func_arn = 'arn:aws:lambda:' + central_default_region + ':' + central_account_number + ':function:' + lambda_vpc_func_name

#### 6: CENTRAL CLIENTS ###### (must specify regions, even if global service)
client_iam_central = boto3.client('iam', aws_access_key_id=central_account_key, aws_secret_access_key=central_account_secret_key, region_name=central_default_region)
client_sns_central = boto3.client('sns', aws_access_key_id=central_account_key, aws_secret_access_key=central_account_secret_key, region_name=central_default_region)
client_ddb = boto3.client('dynamodb', aws_access_key_id=central_account_key, aws_secret_access_key=central_account_secret_key, region_name=central_default_region)
client_s3 = boto3.client('s3', aws_access_key_id=central_account_key, aws_secret_access_key=central_account_secret_key, region_name=central_default_region)
client_sqs = boto3.client('sqs', aws_access_key_id=central_account_key, aws_secret_access_key=central_account_secret_key, region_name=central_default_region)
client_ses = boto3.client('ses', aws_access_key_id=central_account_key, aws_secret_access_key=central_account_secret_key, region_name=central_default_region)
client_lambda = boto3.client('lambda', aws_access_key_id=central_account_key, aws_secret_access_key=central_account_secret_key, region_name=central_default_region)
client_sts = boto3.client('sts', aws_access_key_id=central_account_key, aws_secret_access_key=central_account_secret_key, region_name=central_default_region)
client_sts_payer = boto3.client('sts', aws_access_key_id=payer_account_key, aws_secret_access_key=payer_account_secret_key, region_name=central_default_region)

######## 7: "GET" variables (from DDB tables)###############
###########################################################################
## Lambda ALL: CFN
def get_service_now_item():
	global transaction_id, new_default_regions, short_project_name, availability_zones, environment, creator_email, creator_name, account_alias
	while True:
		try:
			service_now_table_item = client_ddb.get_item(
			    TableName=service_now_table_name,
			    Key={
			        service_now_primary_key: {
			            'S': project_email_address
			        }
			    },
			)
			break
		except botocore.exceptions.ClientError:
			print('service now item not found... try again')
	transaction_id = str(service_now_table_item['Item']['TransactionID']['S'])
	print('problem with new_def regions here:')
	new_default_regions = eval(str(service_now_table_item['Item']['DefaultRegions']['S']))
	short_project_name = str(service_now_table_item['Item']['ShortProjectName']['S'])
	availability_zones = str(service_now_table_item['Item']['AvailabilityZones']['S'])
	environment = str(service_now_table_item['Item']['Environment']['S'])
	creator_email = str(service_now_table_item['Item']['CreatorEmailAddress']['S'])
	creator_name = str(service_now_table_item['Item']['Creator']['S'])
	account_alias = 'adsk-eis-' + short_project_name + '-' + environment

## Lambda 3 ONLY: VPC
def get_credentials_item():
	global new_role_name, project_email_address
	credentials_table_item = client_ddb.get_item(
	    TableName=credentials_table_name,
	    Key={
	        credentials_primary_key: {
	            'S': new_account_number # project_email_address
	        }
	    },
	)
	new_role_name = str(credentials_table_item['Item']['RoleName']['S'])
	project_email_address = str(credentials_table_item['Item']['EmailAddress']['S'])


#### ASSUME ROLE: get access keys ######

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

####### 7: NEW ARNS ... and variables gotten from function calls, client calls, etc. #####
######################################################################
get_queue_url_ct = client_sqs.get_queue_url(
    QueueName=sqs_cloudtrail_queue_name,
    QueueOwnerAWSAccountId=central_account_number)
sqs_cloudtrail_queue_url = get_queue_url_ct['QueueUrl']



######### 8: CFN Parameters #########
#####################################################################################################################
def cfn_parameters():
	global cfn_parameters_2az, cfn_parameters_3az
	cfn_parameters_2az = [
	    {'ParameterKey':'ApplicationSubnetCidrAZ1','ParameterValue':'10.43.10.128/26','UsePreviousValue': False},
	    {'ParameterKey':'ApplicationSubnetCidrAZ2','ParameterValue':'10.43.10.192/26','UsePreviousValue': False},
	    {'ParameterKey':'AppName','ParameterValue': short_project_name,'UsePreviousValue':False},         # change this
	    {'ParameterKey':'BastionInstanceType','ParameterValue':'t2.micro','UsePreviousValue':False},
	    {'ParameterKey':'CorporateCidrIp','ParameterValue':'10.0.0.0/8','UsePreviousValue': False},
	    {'ParameterKey':'DatabaseSubnetCidrAZ1','ParameterValue':'10.43.11.192/27','UsePreviousValue': False},
	    {'ParameterKey':'DatabaseSubnetCidrAZ2','ParameterValue':'10.43.11.224/27','UsePreviousValue': False},
	    {'ParameterKey':'EnvironmentName','ParameterValue': environment, 'UsePreviousValue':False},     #possibly change this...?
	    {'ParameterKey':'InternalLoadBalancerSubnetCidrAZ1','ParameterValue':'10.43.11.128/27','UsePreviousValue': False},
	    {'ParameterKey':'InternalLoadBalancerSubnetCidrAZ2','ParameterValue':'10.43.11.160/27','UsePreviousValue': False},
	    {'ParameterKey':'InternetLoadBalancerSubnetCidrAZ1','ParameterValue':'10.43.10.0/26','UsePreviousValue': False},
	    {'ParameterKey':'InternetLoadBalancerSubnetCidrAZ2','ParameterValue':'10.43.10.64/26','UsePreviousValue': False},
	    {'ParameterKey':'NATAMI','ParameterValue':'default','UsePreviousValue': False},
	    {'ParameterKey':'NATInstanceType','ParameterValue':'t2.micro','UsePreviousValue': False},
	    {'ParameterKey':'PresentationSubnetCidrAZ1','ParameterValue':'10.43.11.0/26','UsePreviousValue': False},
	    {'ParameterKey':'PresentationSubnetCidrAZ2','ParameterValue':'10.43.11.64/26','UsePreviousValue': False},
	    {'ParameterKey':'VPCCidr','ParameterValue':'10.43.10.0/23','UsePreviousValue': False}            
	        ]
	cfn_parameters_3az = cfn_parameters_2az[:]

	cfn_parameters_3az += [{'ParameterKey': 'ApplicationSubnetCidrAZ3','ParameterValue':'10.43.11.0/26','UsePreviousValue': False}]
	cfn_parameters_3az += [{'ParameterKey': 'DatabaseSubnetCidrAZ3','ParameterValue':'10.43.11.0/26','UsePreviousValue': False}]
	cfn_parameters_3az += [{'ParameterKey': 'InternalLoadBalancerSubnetCidrAZ3','ParameterValue':'10.43.11.0/26','UsePreviousValue': False}]
	cfn_parameters_3az += [{'ParameterKey': 'InternetLoadBalancerSubnetCidrAZ3','ParameterValue':'10.43.11.0/26','UsePreviousValue': False}]
	cfn_parameters_3az += [{'ParameterKey': 'PresentationSubnetCidrAZ3','ParameterValue':'10.43.11.0/26','UsePreviousValue': False}]

############### credentials table add ##############################

def ddb_add_to_credentials_table():
	""" Pushes credentials-related information of the new account from serviceNow form into an existing dynamoDB
	table called 'Credentials Table,' which resides in the central account """
	client_ddb.put_item(
        TableName=credentials_table_name,                                                      # must enter in table name
        Item={
                'EmailAddress': {'S': project_email_address},
                'AccountNumber' : {'S' : new_account_number},
                'TransactionID' : {'S' : transaction_id}, 
                'RoleName': {'S': new_role_name}
                }
	)
	print('credentials table put complete')

################ IAM: password policy, account alias ##############################
def iam_password_policy():
	""" Configures IAM password policy in the new account to match ADSK standards """
	client_iam_session_new.update_account_password_policy(
		MinimumPasswordLength=8,
		RequireSymbols=True,
		RequireNumbers=True,
		RequireUppercaseCharacters=True,
		RequireLowercaseCharacters=True,
		AllowUsersToChangePassword=True,
		MaxPasswordAge=90,
		HardExpiry=False, 
	)
	print('iam_password_policy complete')
	
def iam_create_alias():  
	""" Creates AWS account alias for the new account"""
	client_iam_session_new.create_account_alias(
	AccountAlias=account_alias			
	)
	print('iam_create_alias complete')

###### SNS for CFN (and lambda) ########################
################################################
def sns_create_topic_cfn():
	for region in new_default_regions:
		client_sns = session_new.client('sns', region_name=region)
		# client_sns = boto3.client('sns', aws_access_key_id=new_account_key, aws_secret_access_key=new_account_secret_key, region_name=region)
		cfn_sns_topic_arn = 'arn:aws:sns:' +  region + ':' + new_account_number + ':' + sns_cfn_topic_name
		client_sns.create_topic(
		Name=sns_cfn_topic_name,
		)
		# add policy
		cfn_sns_topic_policy["Statement"][0]["Resource"] = cfn_sns_topic_arn
		cfn_sns_topic_policy["Statement"][0]["Condition"]["StringEquals"]["AWS:SourceOwner"] = new_account_number
		cfn_sns_topic_policy["Statement"][1]["Resource"] = cfn_sns_topic_arn
		cfn_sns_topic_policy["Statement"][1]["Principal"]["AWS"] = "arn:aws:iam::" + central_account_number + ":root"
		cfn_sns_topic_policy_json = json.dumps(cfn_sns_topic_policy)	#convert to JSON format
		client_sns.set_topic_attributes(
		  	TopicArn=cfn_sns_topic_arn,
		  	AttributeName='Policy',
		  	AttributeValue=cfn_sns_topic_policy_json
		)
		print('cfn sns topic created in ' + region)

def lambda_permission_sns_cfn():
	for region in new_default_regions:
		cfn_sns_topic_arn = 'arn:aws:sns:' +  region + ':' + new_account_number + ':' + sns_cfn_topic_name
		client_lambda.add_permission(
		    FunctionName=lambda_vpc_func_name,
		    StatementId='sns__cfn-stack-' + region + short_project_name,
		    Action='lambda:InvokeFunction',
		    Principal='sns.amazonaws.com',
		    SourceArn=cfn_sns_topic_arn)
		print('lambda permission put in ' + region)

def sns_subscribe_lambda_cfn():
	for region in new_default_regions:
		client_sns_central = boto3.client('sns', aws_access_key_id=central_account_key, aws_secret_access_key=central_account_secret_key, region_name=region)
		cfn_sns_topic_arn = 'arn:aws:sns:' +  region + ':' + new_account_number + ':' + sns_cfn_topic_name
		client_sns_central.subscribe(
		    TopicArn=cfn_sns_topic_arn,
		    Protocol='lambda',
		    Endpoint=lambda_vpc_func_arn
		)
		print('sns lambda subscribed in ' + region)

################ CloudFormation: create and validate stack, notify correct people if failed ##############################
def cfn_create_stack():
	""" Creates a CloudFormation stack in each specified region for the new account """
	if availability_zones == '2':
		template_url = cfn_template_url_2azs
		cfn_parameters = cfn_parameters_2az
	else:
		template_url = cfn_template_url_3azs
		cfn_parameters = cfn_parameters_3az
	for region in new_default_regions:
		cfn_sns_topic_arn = 'arn:aws:sns:' +  region + ':' + new_account_number + ':' + sns_cfn_topic_name
		client_cfn = session_new.client('cloudformation', region_name=region)
		# client_cfn = boto3.client('cloudformation', aws_access_key_id=new_account_key, aws_secret_access_key=new_account_secret_key, region_name=region)
		client_cfn.create_stack(
		    StackName=cfn_stack_name,
		    TemplateURL=template_url,
		    Parameters=cfn_parameters,
		    DisableRollback=True,
		    TimeoutInMinutes=15,
		    Capabilities=[
		        'CAPABILITY_IAM',
		    ],
			NotificationARNs=[
		    	cfn_sns_topic_arn,
			]
		)
		print('stack created in ' + region + ' and timeout started')

# ############ DDB: account automation table ###################
def ddb_add_to_parameters_table():
	table_item_dict = {
	parameters_primary_key : {'S' : new_account_number},
	'EmailAddress' : {'S': project_email_address},
	'TransactionID' : {'S' : transaction_id},
	'CFNStackRegions' : {'S': str(new_default_regions)}
	}
	if availability_zones == '2':
		template_url = cfn_template_url_2azs
		cfn_parameters = cfn_parameters_2az
	elif availability_zones == '3':
		template_url = cfn_template_url_3azs
		cfn_parameters = cfn_parameters_3az
	for region in new_default_regions:
		# client_cfn = boto3.client('cloudformation', aws_access_key_id=new_account_key, aws_secret_access_key=new_account_secret_key, region_name=region)
		for dict_item in cfn_parameters:
			key = dict_item['ParameterKey']
			value = dict_item['ParameterValue']
			table_item_dict[region + ': ' + key] = {'S': value}
	client_ddb.put_item(
		TableName=parameters_table_name,                                                      # must enter in table name
		Item=table_item_dict
	)
	print('parameters table put complete')

times = ''

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
	    Key=s3_automation_file_name,	# name for the object
	    StorageClass='STANDARD',
	)
	print('account automation times file put into s3 and is x long: ' + str(len(current)))

################# S3 Bucket Policies######################
##################################################################

def s3_update_bucket_policy(service):
	central_account_cloudtrail_folder_arn = cloudtrail_bucket_arn + '/' + account_alias + '/AWSLogs/' + new_account_number + '/*'
	central_account_config_folder_arn = config_bucket_arn + '/' + account_alias + '/AWSLogs/' + new_account_number + '/*'
	if service == 'cloudtrail':
		bucket_name = s3_cloudtrail_bucket_name
		bucket_folder_arn = central_account_cloudtrail_folder_arn
	elif service == 'config':
		bucket_name = s3_config_bucket_name
		bucket_folder_arn = central_account_config_folder_arn
	bucket_policy_json = client_s3.get_bucket_policy(
	    Bucket=bucket_name					
		)["Policy"]
	bucket_policy = json.loads(bucket_policy_json)		# convert from JSON to python dict
	resources = bucket_policy["Statement"][1]["Resource"]
	if type(resources) == list:		#this means it's a list, bc there are 2 or more resources
		bucket_policy["Statement"][1]["Resource"] = resources + [bucket_folder_arn]
		print('list type')
	elif type(resources) == unicode:
		bucket_policy["Statement"][1]["Resource"] = [resources] + [bucket_folder_arn]
		print('unicode type')
	bucket_policy_json = json.dumps(bucket_policy)			# convert to JSON
	client_s3.put_bucket_policy(
	    Bucket=bucket_name,								
	    Policy= bucket_policy_json
	)
	print('bucket policy updated ' + service)

def sns_create_topic_cloudtrail():
	for region in region_names_list:
		cloudtrail_sns_topic_arn = 'arn:aws:sns:' +  region + ':' + new_account_number + ':' + sns_cloudtrail_topic_name
		client_sns = session_new.client('sns', region_name=region)
		# client_sns = boto3.client('sns', aws_access_key_id=new_account_key, aws_secret_access_key=new_account_secret_key, region_name=region)
		client_sns.create_topic(
		Name=sns_cloudtrail_topic_name, 
		)
		# add policy
		cloudtrail_sns_topic_policy["Statement"][0]["Resource"] = cloudtrail_sns_topic_arn
		cloudtrail_sns_topic_policy_json = json.dumps(cloudtrail_sns_topic_policy)	#convert to JSON format

		client_sns.set_topic_attributes(
    	TopicArn=cloudtrail_sns_topic_arn,
    	AttributeName='Policy',
    	AttributeValue=cloudtrail_sns_topic_policy_json
		)
		print('cloudtrail sns topic created in ' + region)

def sns_update_policy_config():
	for region in region_names_list:
		client_sns_central = boto3.client('sns', aws_access_key_id=central_account_key, aws_secret_access_key=central_account_secret_key, region_name=region)                        
		sns_config_topic_arn = "arn:aws:sns:" + region + ":" + central_account_number + ":" + sns_config_topic_name
		new_account_iam_root_arn = 'arn:aws:iam::' + new_account_number + ':root'
		config_sns_topic_policy = client_sns_central.get_topic_attributes(
			TopicArn=sns_config_topic_arn)["Attributes"]["Policy"]
		config_sns_topic_policy = eval(config_sns_topic_policy)
		root_accounts = config_sns_topic_policy["Statement"][1]["Principal"]["AWS"] 
		if type(root_accounts) == list:
			config_sns_topic_policy["Statement"][1]["Principal"]["AWS"] = config_sns_topic_policy["Statement"][1]["Principal"]["AWS"] + [new_account_iam_root_arn]
		else:
			config_sns_topic_policy["Statement"][1]["Principal"]["AWS"] = [config_sns_topic_policy["Statement"][1]["Principal"]["AWS"]] + [new_account_iam_root_arn]
		config_sns_topic_policy_json = json.dumps(config_sns_topic_policy)	#convert to JSON format
		client_sns_central.set_topic_attributes(
		TopicArn=sns_config_topic_arn,
		AttributeName='Policy',
		AttributeValue=config_sns_topic_policy_json
		)
	print('config sns topic policy updated')

def config():
	for region in region_names_list:
		config_role_arn = 'arn:aws:iam::' + new_account_number + ':role/' + config_role_name 
		client_config = session_new.client('config', region_name=region) 
		# client_config = boto3.client('config', aws_access_key_id=new_account_key, aws_secret_access_key=new_account_secret_key, region_name=region) 
		config_topic_arn = 'arn:aws:sns:' + region + ':' + central_account_number + ':' + sns_config_topic_name
		client_config.put_configuration_recorder(
			ConfigurationRecorder={
			'name': config_recorder_name,
			'roleARN': config_role_arn
			}
		)
		while True:
			try:
				client_config.put_delivery_channel(
					DeliveryChannel={
					'name': config_delivery_channel_name,
					's3BucketName': s3_config_bucket_name,
					's3KeyPrefix': account_alias,                                                
					'snsTopicARN':  config_topic_arn
					}
				)
				break
			except botocore.exceptions.ClientError:
				print('config put delivery channel failed in ' + region)
		client_config.start_configuration_recorder(
			ConfigurationRecorderName=config_recorder_name                        # same as above in put_configuration_recorder name
		)
		print('config done in ' + region)

def cloudtrail():
	for region in region_names_list:
		client_ct = session_new.client('cloudtrail', region_name=region)
		# client_ct = boto3.client('cloudtrail', aws_access_key_id=new_account_key, aws_secret_access_key=new_account_secret_key, region_name=region)
		client_ct.create_trail(Name=cloudtrail_name,		# name for trail can be anything (if not given will be 'Default')
	    S3BucketName=s3_cloudtrail_bucket_name,		
	    S3KeyPrefix=account_alias,				# not sure about this yet
	    SnsTopicName=sns_cloudtrail_topic_name,		# change this
	    IncludeGlobalServiceEvents=cloudtrail_global_dict[region],				
		)
		client_ct.start_logging(
	    Name=cloudtrail_name			
		)
		print('cloudtrail created in ' + region)

def iam_create_config_role():
    client_iam_session_new.create_role(
        RoleName=config_role_name,
        AssumeRolePolicyDocument=json.dumps(config_role_trust_relationship)
        )
    client_iam_session_new.put_role_policy(
        RoleName=config_role_name,
        PolicyName=config_role_policy_name,
        PolicyDocument=json.dumps(config_role_policy)
        )
    print('config role created')


def support_create_case_enterprise():
	client_support_session.create_case(
		subject='THIS IS A TEST: Add to Enterprise Support',
        serviceCode='customer-account',
        severityCode='low',
        categoryCode='other-account-issues',
        communicationBody='DO NOT REPLY: Please add this account to Enterprise Support',
        ccEmailAddresses=
            support_email_addresses,
        language='en',
        issueType='customer-service',
    )
	print('support case opened')


##############################################################################
##############################################################################
## SQS ##########################
def sqs_config_sns_subscribe():
    for region in region_names_list:
        client_sns_central = boto3.client('sns', aws_access_key_id=central_account_key, aws_secret_access_key=central_account_secret_key, region_name=region)                        
        sns_config_topic_arn = "arn:aws:sns:" + region + ":" + central_account_number + ":" + sns_config_topic_name
        response = client_sns_central.subscribe(
        TopicArn= sns_config_topic_arn,
        Protocol='sqs',
        Endpoint=sqs_config_queue_arn
        )
    print('sqs config sns subscribe all regions')

# cloudtrail first
def sqs_update_policy_cloudtrail():
	get_queue_attributes = client_sqs.get_queue_attributes(
	    QueueUrl=sqs_cloudtrail_queue_url,
	    AttributeNames=[
	        'Policy',
	    ]
	)
	queue_policy = get_queue_attributes['Attributes']['Policy']
	queue_policy = json.loads(queue_policy)                         # convert to regular python dictionary                              # add sns topic arns to source arn list
	sns_cloudtrail_topic_arn = "arn:aws:sns:*:" + new_account_number + ":" + sns_cloudtrail_topic_name
	queue_policy["Statement"][0]["Condition"]["ArnEquals"]["aws:SourceArn"] = queue_policy["Statement"][0]["Condition"]["ArnEquals"]["aws:SourceArn"] + [sns_cloudtrail_topic_arn]
	queue_policy = json.dumps(queue_policy)                         # convert back to JSON format
	client_sqs.set_queue_attributes(
	    QueueUrl=sqs_cloudtrail_queue_url,
	    Attributes={
	        'Policy': queue_policy
	    }
	)
	print('sqs policy updated for cloudtrail')


token_dict = {}
def sqs_cloudtrail_sns_subscribe():
	for region in region_names_list:
		# client_sns = boto3.client('sns', aws_access_key_id=new_account_key, aws_secret_access_key=new_account_secret_key, region_name=region)                        
		client_sns = session_new.client('sns', region_name=region)                        
		cloudtrail_sns_topic_arn = "arn:aws:sns:" + region + ":" + new_account_number + ":" + sns_cloudtrail_topic_name
		client_sns.subscribe(
		TopicArn= cloudtrail_sns_topic_arn,
		Protocol='sqs',
		Endpoint=sqs_cloudtrail_queue_arn
		)
		print(region + ' is subscribed')
		while True:         # wait for message to arrive
			try:
				messages = client_sqs.receive_message(
				QueueUrl=sqs_cloudtrail_queue_url,
				MaxNumberOfMessages=1,
				VisibilityTimeout=30,
				WaitTimeSeconds=0)["Messages"]
				break
			except KeyError:
				print('retry')
		for message in messages:
			if json.loads(messages[0]["Body"])["Type"] == "SubscriptionConfirmation":       # possibly not necessary
				receipt_handle = messages[0]["ReceiptHandle"]
				token = str(json.loads(messages[0]["Body"])["Token"])
				token_dict[region] = token
				client_sqs.delete_message(
				QueueUrl=sqs_cloudtrail_queue_url,
				ReceiptHandle=receipt_handle
				)
				print('message deleted')
			else:
				print('non-subscription confirmation message delivered... try again')

def sqs_cloudtrail_sns_confirm_subscriptions():
	for region in region_names_list:
		token = token_dict[region]
		client_sns = session_new.client('sns', region_name=region)                        
		cloudtrail_sns_topic_arn = "arn:aws:sns:" + region + ":" + new_account_number + ":" + sns_cloudtrail_topic_name
		while True:
			try:
			# client_sns = boto3.client('sns', aws_access_key_id=new_account_key, aws_secret_access_key=new_account_secret_key, region_name=region)
				client_sns.confirm_subscription(
					TopicArn=cloudtrail_sns_topic_arn,
					Token=token,
					AuthenticateOnUnsubscribe='true')
				break
			except botocore.exceptions.ClientError:
				print('confirmation does not exist in ' + region + ' ...try again...')
		print('sqs ct subscription confirmation in ' + region)


## VPC S3 Endpoint ###
def vpc_create_endpoint():
	client_cfn = session_new.client('cloudformation', region_name=region)                              
	client_ec2 = session_new.client('ec2', region_name=region)
	vpc = client_cfn.describe_stack_resource(
		StackName=cfn_stack_name,
		LogicalResourceId='VPC'
	)
	vpc_id = vpc['StackResourceDetail']['PhysicalResourceId']
	internal_route_table = client_cfn.describe_stack_resource(
		StackName=cfn_stack_name,
		LogicalResourceId='InternalRouteTable'
	)
	internal_route_table_id = internal_route_table['StackResourceDetail']['PhysicalResourceId']
	internet_route_table = client_cfn.describe_stack_resource(
		StackName=cfn_stack_name,
		LogicalResourceId='InternetRouteTable'
	)
	internet_route_table_id = internet_route_table['StackResourceDetail']['PhysicalResourceId']
	client_ec2.create_vpc_endpoint(
		DryRun=False,
		VpcId=vpc_id,
		ServiceName='com.amazonaws.' + region + '.s3', 
		PolicyDocument=json.dumps(vpc_endpoint_policy),
		RouteTableIds=[
			internal_route_table_id,
			internet_route_table_id
		],
		ClientToken= new_account_number + client_token_generator() ## has to be new every time you do this
	)
	print('vpc endpoint created in ' + region)

def iam_saml_provider():
#grab metadata from the central account
	new_saml_provider_arn = 'arn:aws:iam::' + new_account_number + ':saml-provider/' + new_saml_provider_name
	central_metadata = client_iam_central.get_saml_provider(
	    SAMLProviderArn=central_saml_provider_arn
	)
	central_saml_metadata = central_metadata['SAMLMetadataDocument']
	# create saml identity provider
	client_iam_session_new.create_saml_provider(
	    SAMLMetadataDocument=central_saml_metadata,
	    Name=new_saml_provider_name
	)
	print('iam saml provider created')
	# create saml role
	saml_assume_role_policy["Statement"][0]["Principal"]["Federated"] = 'arn:aws:iam::' + new_account_number + ':saml-provider/' + saml_provider_name
	client_iam_session_new.create_role(
	  RoleName=new_saml_role_name,
	  AssumeRolePolicyDocument=json.dumps(saml_assume_role_policy)
	)
	client_iam_session_new.put_role_policy(
	    RoleName=new_saml_role_name,
	    PolicyName=new_saml_role_policy_name,
	    PolicyDocument=json.dumps(new_saml_role_policy)
	)
	print('saml provider role created and attached')


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


############ POLICIES ###################

config_role_policy = {
  "Version": "2012-10-17",
  "Statement": [
    {
      "Action": [
        "appstream:Get*",
        "autoscaling:Describe*",
        "cloudformation:DescribeStacks",
        "cloudformation:DescribeStackEvents",
        "cloudformation:DescribeStackResource",
        "cloudformation:DescribeStackResources",
        "cloudformation:GetTemplate",
        "cloudformation:List*",
        "cloudfront:Get*",
        "cloudfront:List*",
        "cloudtrail:DescribeTrails",
        "cloudtrail:GetTrailStatus",
        "cloudwatch:Describe*",
        "cloudwatch:Get*",
        "cloudwatch:List*",
        "config:Get*",
        "config:Describe*",
        "config:Deliver*",
        "directconnect:Describe*",
        "dynamodb:GetItem",
        "dynamodb:BatchGetItem",
        "dynamodb:Query",
        "dynamodb:Scan",
        "dynamodb:DescribeTable",
        "dynamodb:ListTables",
        "ec2:Describe*",
        "elasticache:Describe*",
        "elasticbeanstalk:Check*",
        "elasticbeanstalk:Describe*",
        "elasticbeanstalk:List*",
        "elasticbeanstalk:RequestEnvironmentInfo",
        "elasticbeanstalk:RetrieveEnvironmentInfo",
        "elasticloadbalancing:Describe*",
        "elastictranscoder:Read*",
        "elastictranscoder:List*",
        "iam:List*",
        "iam:Get*",
        "kinesis:Describe*",
        "kinesis:Get*",
        "kinesis:List*",
        "opsworks:Describe*",
        "opsworks:Get*",
        "route53:Get*",
        "route53:List*",
        "redshift:Describe*",
        "redshift:ViewQueriesInConsole",
        "rds:Describe*",
        "rds:ListTagsForResource",
        "s3:Get*",
        "s3:List*",
        "sdb:GetAttributes",
        "sdb:List*",
        "sdb:Select*",
        "ses:Get*",
        "ses:List*",
        "sns:Get*",
        "sns:List*",
        "sqs:GetQueueAttributes",
        "sqs:ListQueues",
        "sqs:ReceiveMessage",
        "storagegateway:List*",
        "storagegateway:Describe*",
        "trustedadvisor:Describe*"
      ],
      "Effect": "Allow",
      "Resource": "*"
    }
  ]
}

config_role_trust_relationship = {
  "Version": "2012-10-17",
  "Statement": [
    {
      "Sid": "",
      "Effect": "Allow",
      "Principal": {
        "Service": "config.amazonaws.com"
      },
      "Action": "sts:AssumeRole"
    }
  ]
}

sns_config_initial_policy = {
  "Version": "2008-10-17",
  "Id": "__default_policy_ID",
  "Statement": [
    {
      "Sid": "__default_statement_ID",
      "Effect": "Allow",
      "Principal": {
        "AWS": "*"
      },
      "Action": [
        "SNS:ListSubscriptionsByTopic",
        "SNS:Subscribe",
        "SNS:DeleteTopic",
        "SNS:GetTopicAttributes",
        "SNS:Publish",
        "SNS:RemovePermission",
        "SNS:AddPermission",
        "SNS:Receive",
        "SNS:SetTopicAttributes"
      ],
      "Resource": "arn:aws:sns:us-east-1:************:intern-test-config-notifications",
      "Condition": {
        "StringEquals": {
          "AWS:SourceOwner": "************"
        }
      }
    },
    {
      "Sid": "configPolicy",
      "Effect": "Allow",
      "Principal": {
        "AWS": "arn:aws:iam::************:root"
      },
      "Action": "SNS:Publish",
      "Resource": "arn:aws:sns:*:************:intern-test-config-notifications"
    }
  ]
}

initial_bucket_policy_cloudtrail = {
	"Version": "2012-10-17",
	"Statement": [
		{
			"Sid": "AWSCloudTrailAclCheck20131101",
			"Effect": "Allow",
			"Principal": {
				"AWS": [
					"arn:aws:iam::************:root",
					"arn:aws:iam::************:root",
					"arn:aws:iam::************:root",
					"arn:aws:iam::************:root",
					"arn:aws:iam::************:root",
					"arn:aws:iam::************:root",
					"arn:aws:iam::************:root",
					"arn:aws:iam::************:root",
					"arn:aws:iam::************:root"
				]
			},
			"Action": "s3:GetBucketAcl",
			"Resource": 'place holder'		# this is where the cloudtrail bucket arn goes
		},
		{
			"Sid": "AWSCloudTrailWrite20131101",
			"Effect": "Allow",
			"Principal": {
				"AWS": [
					"arn:aws:iam::************:root",
					"arn:aws:iam::************:root",
					"arn:aws:iam::************:root",
					"arn:aws:iam::************:root",
					"arn:aws:iam::************:root",
					"arn:aws:iam::************:root",
					"arn:aws:iam::************:root",
					"arn:aws:iam::************:root",
					"arn:aws:iam::************:root"
				]
			},
			"Action": "s3:PutObject",
			"Resource": [	# this is where the folder in the bucket goes (looks like: "arn:aws:s3:::nltest1/AWSLogs/************/*")
							# new one will be added everytime a new account is created
			],
			"Condition": {
				"StringEquals": {
					"s3:x-amz-acl": "bucket-owner-full-control"
				}
			}
		}
	]
}

initial_bucket_policy_config = {
	"Version": "2012-10-17",
	"Statement": [
		{
			"Sid": "AWSConfigBucketPermissionsCheck",
			"Effect": "Allow",
			"Principal": {
				"Service": "config.amazonaws.com"
			},
			"Action": "s3:GetBucketAcl",
			"Resource": 	'place holder' # this is where the config bucket arn goes (only one)
		},
		{
			"Sid": " AWSConfigBucketDelivery",
			"Effect": "Allow",
			"Principal": {
				"Service": "config.amazonaws.com"
			},
			"Action": "s3:PutObject",
			"Resource": [	# this is where the folder arn goes (new one added each time new account is created)
			],
			"Condition": {
				"StringEquals": {
					"s3:x-amz-acl": "bucket-owner-full-control"
				}
			}
		}
	]
}

cloudtrail_sns_topic_policy = {	# this says that cloudtrail service is allowed to publish into whichever topic arns you put in resource
		"Version": "2012-10-17",
 
		"Statement": [
		{
   
		"Sid": "AWSCloudTrailSNSPolicy20140219",  
		"Effect": "Allow",
		# 'resource' here: its own topic arn
		"Principal": {
   		    	
			"AWS": [
				"arn:aws:iam::************:root",
				"arn:aws:iam::************:root",
				"arn:aws:iam::************:root",
				"arn:aws:iam::************:root",
				"arn:aws:iam::************:root",
				"arn:aws:iam::************:root",
				"arn:aws:iam::************:root",
				"arn:aws:iam::************:root",
				"arn:aws:iam::************:root"
				]  
			},
			"Action": "SNS:Publish",
		}
		]
}

config_sns_topic_policy = {			# this says that config is allowed to publish into the topic arn you put in resource (its own topic arn)
          "Id": "Policy1415489375392",
          "Statement": [
            {
              "Sid": "AWSConfigSNSPolicy20150201",
              "Action": [
                "SNS:Publish"
              ],				# new account info will NEVER go in here, once this is set it never changes
              "Effect": "Allow",
              # 'resource' here: its own topic arn
              "Principal": {
                "AWS": [
                  "arn:aws:iam::************:root",
                  "arn:aws:iam::************:root",
                  "arn:aws:iam::************:root",
                  "arn:aws:iam::************:root"
                ]
              }
            }
          ]
}








times = ''


def lambda_sqs():
	print('lambda sqs start')
	global times, new_account_number
	new_account_number = os.environ['LAMBDA_ACCOUNT_NUMBER']

	get_credentials_item()
	get_service_now_item()
	role_access_keys()

	time_sqs_start = datetime.datetime.utcnow()
	sqs_config_sns_subscribe()
	sqs_update_policy_cloudtrail()
	sqs_cloudtrail_sns_subscribe()
	sqs_cloudtrail_sns_confirm_subscriptions()
	time_sqs_end = datetime.datetime.utcnow()

	times += str(time_sqs_start) + ' UTC, SQS start, ' + new_account_number + '\n' + \
	str(time_sqs_end) + ' UTC, SQS end, ' + new_account_number + '\n'
	s3_account_automation_info_put()
	print('lambda sqs end')



print('account created!!')
print('lambda sqs end')


lambda_sqs()



