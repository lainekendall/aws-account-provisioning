import boto3, time, json, string, random
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
import variables
import mainpolicies
from multiprocessing import Process

################ credentials table add ##############################

def ddb_add_to_credentials_table():
	client_ddb.put_item(
        TableName=credentials_table_name,                                                      # must enter in table name
        Item={
                transaction_id_column_name : {'S' : transaction_id}, 
                account_number_column_name : {'S' : new_account_number},
                email_address_column_name: {'S': project_email_address},
                password_column_name: {'S': password}
                }
	)  
	print('credentials table put complete')

################ IAM: password policy, account alias ##############################
def iam_password_policy():
 	client_iam_new.update_account_password_policy(
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
	client_iam_new.create_account_alias(
	AccountAlias=new_account_alias			
	)
	print('iam_create_alias complete')

################ CFN/EC2: create key pair ##############################
def iam_create_key_pair():
	for region in new_default_regions:
		client_ec2 = boto3.client('ec2', aws_access_key_id=new_account_key, aws_secret_access_key=new_account_secret_key, region_name=region)
		client_ec2.create_key_pair(
		    DryRun=False,
		    KeyName=cfn_key_pair_name
		)

################ CloudFormation: create and validate stack, notify correct people if failed ##############################
message, subject = '', ''
stack_resource_list = []
resource_start_dict = {}
resource_end_dict = {}
events_by_region = {}
stack_timeout = 0
def create_dict():
	for region in new_default_regions:
		resource_start_dict[region] = {}
		resource_end_dict[region] = {}
		events_by_region[region] = []
def cfn_create_stack():
	global message, subject, stack_timeout	#only need for lists and strings
	if availability_zones == '2':
		template_url = template_url_2azs
		cfn_parameters = cfn_parameters_2az
	else:
		# add necessary parameters for third availability zone
		template_url = template_url_3azs
		cfn_parameters = cfn_parameters_3az
	for region in new_default_regions:
		client_cfn = boto3.client('cloudformation', aws_access_key_id=new_account_key, aws_secret_access_key=new_account_secret_key, region_name=region)
		client_cfn.create_stack(
		    StackName=cfn_stack_name,
		    TemplateURL=template_url,
		    Parameters=cfn_parameters,
		    DisableRollback=True,
		    TimeoutInMinutes=123,
		    Capabilities=[
		        'CAPABILITY_IAM',
		    ]
		)
		stack_timeout = time.time() + 60*15
		print('stack created and timeout started')

def get_events():
	stack_done_list = []
	global message, subject, stack_timeout
	stack_regions = new_default_regions
	while True:
		for region in stack_regions:
			client_cfn = boto3.client('cloudformation', aws_access_key_id=new_account_key, aws_secret_access_key=new_account_secret_key, region_name=region)
			stack_events = client_cfn.describe_stack_events(StackName=cfn_stack_name)			
			events_list_by_region = events_by_region[region] + stack_events['StackEvents']
			events_list_by_region = [dict(t) for t in set([tuple(event.items()) for event in events_list_by_region])]
			events_by_region[region] = events_list_by_region
			if client_cfn.describe_stacks(StackName=cfn_stack_name)['Stacks'][0]['StackStatus'] != 'CREATE_IN_PROGRESS':
				print('stack created or failed in ' + region)
				stack_done_list += [region]
				stack_done_list = list(set(stack_done_list))		# get rid of duplicates
			if stack_timeout < time.time(): # the creation is taking too long
				client_sns_central.publish(
				    TopicArn=cfn_sns_topic_arn,
				    Message='Stack Creation in ' + region +  ' did not complete in 15 minutes',
				    Subject='Timeout')
				print('stack timeout')
				stack_done_list += [region]
				stack_done_list = list(set(stack_done_list))		# get rid of duplicates
			if len(stack_done_list) == len(new_default_regions):
				print('events by region dictionary in ' + region + ' is x long:' + str(len(events_by_region[region])))
				return
	print('while loop broken, events done')

def validate():
	for region in new_default_regions:
		client_cfn = boto3.client('cloudformation', aws_access_key_id=new_account_key, aws_secret_access_key=new_account_secret_key, region_name=region)
		stack_status = client_cfn.describe_stacks(StackName=cfn_stack_name)['Stacks'][0]['StackStatus']
		client_sns_central.publish(
			    TopicArn=cfn_sns_topic_arn,
			    Message='The CloudFormation stack in the ' + region + ' region is no longer in the process of creating and now has status ' + stack_status,
			    Subject='AWS CloudFormation stack has status: ' + stack_status)

		# if stack_status == 'CREATE_COMPLETE':
		# 	print('stack complete ' + region)
		# 	client_sns_central.publish(
		# 	    TopicArn=cfn_sns_topic_arn,
		# 	    Message='stack create is complet in ' + region,
		# 	    Subject='CREATE_COMPLETE',
		# 	)
		# else: # stack has failed
		# 	message='Stack Creation in ' + region +  ' failed to complete'
		# 	subject='CREATE_FAILED'
		# 	print('stack fail')
		# 	break
		# 	# send notification to topic saying failure or timeout ##
		# if message != '': # create stack has failed in some way
		# 	client_sns_central.publish(
		# 	    TopicArn=cfn_sns_topic_arn,
		# 	    Message=message,
		# 	    Subject=subject)
		print('validated + message sent')

def get_resources():
	global stack_resource_list
	client_cfn = boto3.client('cloudformation', aws_access_key_id=new_account_key, aws_secret_access_key=new_account_secret_key, region_name=new_default_regions[0])
	resources = client_cfn.list_stack_resources(
		StackName=cfn_stack_name)
	resources = resources['StackResourceSummaries']
	for resource in resources:
		stack_resource_list += [str(resource['LogicalResourceId'])]
	num_resources = len(stack_resource_list)
	print('stack resource list is x long: ' + str(num_resources))

def log_events():
		##################################
		# build up start and end dictionaries
	for region in new_default_regions:
		print('event log time in ' + region)
		events_list_by_region = events_by_region[region]
		for event in events_list_by_region:
			is_resource = event['LogicalResourceId'] in stack_resource_list
			if event['ResourceStatus'] == 'CREATE_IN_PROGRESS' and is_resource:
				resource_start_dict[region][event['LogicalResourceId']] = str(event['Timestamp']) + ' UTC'
			elif event['ResourceStatus'] == 'CREATE_COMPLETE' and is_resource:
				resource_end_dict[region][event['LogicalResourceId']] = str(event['Timestamp']) + ' UTC'
		print('resource start dict in ' + region + ' is x long: ' + str(len(resource_start_dict[region])))
		print('resource end dict in ' + region + ' is x long: ' + str(len(resource_end_dict[region])))
# ############ DDB: account automation table ###################
def ddb_add_to_account_automation_table():
	global stack_resource_list
	table_item_dict = {
	transaction_id_column_name : {'S' : transaction_id},
	account_number_column_name : {'S' : new_account_number},
	acount_alias_column_name : {'S': new_account_alias},
	stack_region_column_name : {'S': str(new_default_regions)}
	}
	for region in new_default_regions:
		print(region)
		client_cfn = boto3.client('cloudformation', aws_access_key_id=new_account_key, aws_secret_access_key=new_account_secret_key, region_name=region)
		stack_description = client_cfn.describe_stacks(StackName=cfn_stack_name) 
		parameters_list = stack_description['Stacks'][0]['Parameters']
		for resource_item in stack_resource_list:
			table_item_dict[region + ': ' + resource_item + ' start'] = {'S': resource_start_dict[region][resource_item]}
			table_item_dict[region + ': ' + resource_item + ' end'] = {'S': resource_end_dict[region][resource_item]}
		for dict_item in parameters_list:
			key = dict_item['ParameterKey']
			value = dict_item['ParameterValue']
			table_item_dict[region + ': ' + key] = {'S': value}
	print(table_item_dict)
	client_ddb.put_item(
		TableName=account_automation_table_name,                                                      # must enter in table name
		Item=table_item_dict
	)
	print('act auto table put complete')

################# S3 Bucket Policies######################
##################################################################

def s3_update_bucket_policy(service):
	if service == 'cloudtrail':
		bucket_name = cloudtrail_bucket_name
		new_account_folder_arn = new_account_cloudtrail_folder_arn
	elif service == 'config':
		bucket_name = config_bucket_name
		new_account_folder_arn = new_account_config_folder_arn

	bucket_policy_json = client_s3.get_bucket_policy(
	    Bucket=bucket_name					
		)["Policy"]

	bucket_policy = json.loads(bucket_policy_json)		# convert from JSON to python dict
	resources = bucket_policy["Statement"][1]["Resource"]
	if type(resources) == list:		#this means it's a list, bc there are 2 or more resources
		bucket_policy["Statement"][1]["Resource"] = resources + [new_account_folder_arn]
		print('list type')
	elif type(resources) == unicode:
		bucket_policy["Statement"][1]["Resource"] = [resources] + [new_account_folder_arn]
		print('unicode type')
	bucket_policy_json = json.dumps(bucket_policy)			# convert to JSON
	client_s3.put_bucket_policy(
	    Bucket=bucket_name,								
	    Policy= bucket_policy_json
	)
	print('bucket policy updated ' + service)

def sns_create_topic_cloudtrail():
	for region in region_names_list:
		cloudtrail_sns_topic_arn = 'arn:aws:sns:' +  region + ':' + new_account_number + ':' + cloudtrail_sns_topic_name
		client_sns = boto3.client('sns', aws_access_key_id=new_account_key, aws_secret_access_key=new_account_secret_key, region_name=region)
		client_sns.create_topic(
		Name=cloudtrail_sns_topic_name, 
		)
		# add policy
		cloudtrail_sns_topic_policy["Statement"][0]["Resource"] = cloudtrail_sns_topic_arn
		cloudtrail_sns_topic_policy_json = json.dumps(cloudtrail_sns_topic_policy)	#convert to JSON format

		client_sns.set_topic_attributes(
    	TopicArn=cloudtrail_sns_topic_arn,
    	AttributeName='Policy',
    	AttributeValue=cloudtrail_sns_topic_policy_json
		)
		print('cloudtral sns topic created in ' + region)

def cloudtrail():
	for region in region_names_list:
		client_ct = boto3.client('cloudtrail', aws_access_key_id=new_account_key, aws_secret_access_key=new_account_secret_key, region_name=region)
		client_ct.create_trail(Name=cloudtrail_name,
	    S3BucketName=cloudtrail_bucket_name,		
	    # S3KeyPrefix=s3_prefix,				# not sure about this yet
	    SnsTopicName=cloudtrail_sns_topic_name,
	    IncludeGlobalServiceEvents=cloudtrail_global_dict[region],				
		)
		client_ct.start_logging(
	    Name=cloudtrail_name			
		)
		print('cloudtrail completed in ' + region)

def iam_create_config_role():
    client_iam_new.create_role(
        RoleName=config_role_name,
        AssumeRolePolicyDocument=json.dumps(config_role_trust_relationship)
        )
    client_iam_new.put_role_policy(
        RoleName=config_role_name,
        PolicyName=config_role_policy_name,
        PolicyDocument=json.dumps(config_role_policy)
        )
    print('config role created')
    timeout = time.time() + 30
    while True:
    	if timeout < time.time():
    		print('30 second config role timer')
    		break



def config():
    for region in region_names_list:
        client_config = boto3.client('config', aws_access_key_id=new_account_key, aws_secret_access_key=new_account_secret_key, region_name=region) 
        config_topic_arn = 'arn:aws:sns:' + region + ':' + central_account_number + ':' + config_sns_topic_name
        client_config.put_configuration_recorder(
	        ConfigurationRecorder={
	        'name': config_recorder_name,
	        'roleARN': config_role_arn
	        }
        )
        client_config.put_delivery_channel(
	        DeliveryChannel={
	        'name': config_delivery_channel_name,
	        's3BucketName': config_bucket_name,
	        #'s3KeyPrefix': 'laine-test',                                                
	        'snsTopicARN':  config_topic_arn                            
	        }
        )
        client_config.start_configuration_recorder(
	        ConfigurationRecorderName=config_recorder_name
        )
        print('config configured in ' + region)

support_case_enterprise_id = ''
def support_create_case_enterprise():
	support_case_enterprise_id = client_support.create_case(
		subject='Add to Enterprise Support',
        serviceCode='customer-account',
        severityCode='low',
        categoryCode='other-account-issues',
        communicationBody='Please add this account to Enterprise Support',
        ccEmailAddresses=
            support_email_addresses,
        language='en',
        issueType='customer-service',
    )
	print('support case opened')
## delete
def delete_support_case():
	client_support.resolve_case(
    	caseId=support_case_enterprise_id
	)
## SQS ##########################
def sqs_config_sns_subscribe():
    for region in region_names_list:
        client_sns = boto3.client('sns', aws_access_key_id=central_account_key, aws_secret_access_key=central_account_secret_key, region_name=region)                        
        config_sns_topic_arn = "arn:aws:sns:" + region + ":" + central_account_number + ":" + config_sns_topic_name
        response = client_sns.subscribe(
        TopicArn= config_sns_topic_arn,
        Protocol='sqs',
        Endpoint=sqs_queue_arn
        )
    print('sqs config sns subscribe all regions')

# cloudtrail first
def sqs_update_policy(sns_topic_service):
    if sns_topic_service == 'cloudtrail':
        sns_account_number = new_account_number
        sns_topic_name = cloudtrail_sns_topic_name
    elif sns_topic_service == 'config':
        sns_account_number = central_account_number
        sns_topic_name = config_sns_topic_name
    get_queue_attributes = client_sqs.get_queue_attributes(
    QueueUrl=sqs_queue_url,
    AttributeNames=[
        'Policy',
    ]
    )
    queue_policy = get_queue_attributes['Attributes']['Policy']
    queue_policy = json.loads(queue_policy)                         # convert to regular python dictionary
    for region in region_names_list:                                # add sns topic arns to source arn list
        sns_topic_arn = "arn:aws:sns:" + region + ":" + sns_account_number + ":" + sns_topic_name
        queue_policy["Statement"][0]["Condition"]["ArnEquals"]["aws:SourceArn"] = queue_policy["Statement"][0]["Condition"]["ArnEquals"]["aws:SourceArn"] + [sns_topic_arn]
    queue_policy = json.dumps(queue_policy)                         # convert back to JSON format
    client_sqs.set_queue_attributes(
    QueueUrl=sqs_queue_url,
    Attributes={
        'Policy': queue_policy
    }
    )
    print('sqs policy updated for ' + sns_topic_service)


token_dict = {}
def sqs_cloudtrail_sns_subscribe():
    for region in region_names_list:
        print('top of for loop')
        client_sns = boto3.client('sns', aws_access_key_id=new_account_key, aws_secret_access_key=new_account_secret_key, region_name=region)                        
        cloudtrail_sns_topic_arn = "arn:aws:sns:" + region + ":" + new_account_number + ":" + cloudtrail_sns_topic_name
        client_sns.subscribe(
        TopicArn= cloudtrail_sns_topic_arn,
        Protocol='sqs',
        Endpoint=sqs_queue_arn
        )
        print(region + ' is subscribed')
        while True:         # wait for message to arrive
            try:
                messages = client_sqs.receive_message(
                QueueUrl=sqs_queue_url,
                MaxNumberOfMessages=1,
                VisibilityTimeout=30,
                WaitTimeSeconds=0)["Messages"]
                break
            except KeyError:
                print('retry')
        # if not a subscription confirmation message then... try again? (and do not delete message)
        if json.loads(messages[0]["Body"])["Type"] == "SubscriptionConfirmation":       # possibly not necessary
            receipt_handle = messages[0]["ReceiptHandle"]
            print('receipt handle')
            token = str(json.loads(messages[0]["Body"])["Token"])
        else:
            print('non-subscription confirmation message delivered')
        token_dict[region] = token
        client_sqs.delete_message(
            QueueUrl=sqs_queue_url,
            ReceiptHandle=receipt_handle
        )
        print('message deleted')

def sqs_cloudtrail_sns_confirm_subscriptions():
    for region in region_names_list:
        token = token_dict[region]
        client_sns = boto3.client('sns', aws_access_key_id=new_account_key, aws_secret_access_key=new_account_secret_key, region_name=region)
        cloudtrail_sns_topic_arn = "arn:aws:sns:" + region + ":" + new_account_number + ":" + cloudtrail_sns_topic_name
        response = client_sns.confirm_subscription(
        	TopicArn=cloudtrail_sns_topic_arn,
        	Token=token,
        	AuthenticateOnUnsubscribe='true')
        print('sqs ct subscription confirmation in ' + region)
# sqs_update_policy('config')


## VPC S3 Endpoint ###
def vpc_create_endpoint():
	for region in new_default_regions:
		client_cfn = boto3.client('cloudformation', aws_access_key_id=new_account_key, aws_secret_access_key=new_account_secret_key, region_name=region)                              
		client_ec2 = boto3.client('ec2', aws_access_key_id=new_account_key, aws_secret_access_key=new_account_secret_key, region_name=region)
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
			ClientToken= new_account_number + password_generator() ## has to be new every time you do this
		)
		print('vpc endpoint created in ' + region)

def iam_saml_provider():
#grab metadata from the central account
	central_metadata = client_iam_central.get_saml_provider(
	    SAMLProviderArn=central_saml_provider_arn
	)
	central_saml_metadata = central_metadata['SAMLMetadataDocument']
	# create saml identity provider
	client_iam_new.create_saml_provider(
	    SAMLMetadataDocument=central_saml_metadata,
	    Name=new_saml_provider_name
	)
	print('iam saml provider created')
	# create saml role
	saml_assume_role_policy["Statement"][0]["Principal"]["Federated"] = 'arn:aws:iam::' + new_account_number + ':saml-provider/' + new_saml_provider_name
	client_iam_new.create_role(
	  RoleName=new_saml_role_name,
	  AssumeRolePolicyDocument=json.dumps(saml_assume_role_policy)
	)
	client_iam_new.put_role_policy(
	    RoleName=new_saml_role_name,
	    PolicyName=new_saml_role_policy_name,
	    PolicyDocument=json.dumps(new_saml_role_policy)
	)
	print('saml provider role created and attached')


def ses_email_requestor(): 
  client_ses.send_email(
    Source=ses_proj_automation_email,
    Destination={
        'ToAddresses': [
            creator_email,
        ],
        'CcAddresses': [
            ses_proj_automation_email,
        ]#,
        # 'BccAddresses': [
        #     'string',
        # ]
    },
    Message={
        'Subject': {
            'Data': 'Your AWS account has been provisioned'#,
            # 'Charset': 'string'
        },
        'Body': {
            'Text': {
                'Data': 'Your Amazon Web Services Account has been successfully provisioned. Your account number is ' + new_account_number + ', Your account email address is ' + project_email_address #,
                # 'Charset': 'string'
            },
            # 'Html': {
            #     'Data': 'string',
            #     'Charset': 'string'
            # }
        }
    },
    ReplyToAddresses=[
        reply_to_email,
    ],
    # ReturnPath=return_path_email,
    # SourceArn='',
    # ReturnPathArn=''  
)
  
def ses_email_mfa():
  client_ses.send_email(
    Source=ses_proj_automation_email,
    Destination={
        'ToAddresses': [
            ses_mfa_email,
        ],
        'CcAddresses': [
            ses_proj_automation_email,
        ]#,
#         'BccAddresses': [
#             'string',
#         ]
    },
    Message={
        'Subject': {
            'Data': 'MFA for AWS account'#,
#             'Charset': 'string'
        },
        'Body': {
            'Text': {
                'Data': 'Please have MFA enabled for the following account: ' + 'ACCOUNT NUMBER= ' + new_account_number 
                            + ', ACCOUNT EMAIL ADDRESS= ' + project_email_address 
                            + ', SERVICE NOW TRANSACTION ID= ' + transaction_id #,
#                 'Charset': 'string'
            }#,
#             'Html': {
#                 'Data': 'string',
#                 'Charset': 'string'
#             }
        }
    },
    ReplyToAddresses=[
        reply_to_email,
    ]#,
#     ReturnPath=return_path_email,
#     SourceArn='string',
#     ReturnPathArn='string'  
)





############ VARIABLES ############################################
##################################################################
def func_variables():
	for v in dir(variables):
		print(v + ' = variables.' + v)

account_automation_table_name = variables.account_automation_table_name
account_number_column_name = variables.account_number_column_name
acount_alias_column_name = variables.acount_alias_column_name
address = variables.address
app_name = variables.app_name
availability_zones = variables.availability_zones
aws_account_full_name = variables.aws_account_full_name
boto3 = variables.boto3
central_account_cloudtrail_folder_arn = variables.central_account_cloudtrail_folder_arn
central_account_config_folder_arn = variables.central_account_config_folder_arn
central_account_key = variables.central_account_key
central_account_name = variables.central_account_name
central_account_number = variables.central_account_number
central_account_secret_key = variables.central_account_secret_key
central_default_region = variables.central_default_region
central_saml_provider_arn = variables.central_saml_provider_arn
central_saml_provider_name = variables.central_saml_provider_name
cfn_key_pair_name = variables.cfn_key_pair_name
cfn_parameters_2az = variables.cfn_parameters_2az
cfn_parameters_3az = variables.cfn_parameters_3az
cfn_sns_topic_arn = variables.cfn_sns_topic_arn
cfn_sns_topic_name = variables.cfn_sns_topic_name
cfn_stack_name = variables.cfn_stack_name
city = variables.city
client_ddb = variables.client_ddb
client_iam_central = variables.client_iam_central
client_iam_new = variables.client_iam_new
client_s3 = variables.client_s3
client_ses = variables.client_ses
client_sns_central = variables.client_sns_central
client_sqs = variables.client_sqs
client_support = variables.client_support
cloudtrail_bucket_arn = variables.cloudtrail_bucket_arn
cloudtrail_bucket_name = variables.cloudtrail_bucket_name
cloudtrail_global_dict = variables.cloudtrail_global_dict
cloudtrail_name = variables.cloudtrail_name
cloudtrail_sns_policy_label = variables.cloudtrail_sns_policy_label
cloudtrail_sns_topic_name = variables.cloudtrail_sns_topic_name
company = variables.company
config_bucket_arn = variables.config_bucket_arn
config_bucket_name = variables.config_bucket_name
config_delivery_channel_name = variables.config_delivery_channel_name
config_recorder_name = variables.config_recorder_name
config_role_arn = variables.config_role_arn
config_role_name = variables.config_role_name
config_role_policy_name = variables.config_role_policy_name
config_sns_topic_name = variables.config_sns_topic_name
cost_center = variables.cost_center
creator_dept = variables.creator_dept
creator_email = variables.creator_email
creator_manager = variables.creator_manager
creator_name = variables.creator_name
credentials_table_name = variables.credentials_table_name
email_address_column_name = variables.email_address_column_name
environment = variables.environment
get_queue_url = variables.get_queue_url
iam_access_key_user = variables.iam_access_key_user
json = variables.json
long_project_name = variables.long_project_name
new_account_alias = variables.new_account_alias
new_account_cloudtrail_folder_arn = variables.new_account_cloudtrail_folder_arn
new_account_config_folder_arn = variables.new_account_config_folder_arn
new_account_key = variables.new_account_key
new_account_number = variables.new_account_number
new_account_secret_key = variables.new_account_secret_key
new_default_regions = variables.new_default_regions
new_saml_provider_arn = variables.new_saml_provider_arn
new_saml_provider_name = variables.new_saml_provider_name
new_saml_role_name = variables.new_saml_role_name
new_saml_role_policy_name = variables.new_saml_role_policy_name
password = variables.password
password_column_name = variables.password_column_name
password_generator = variables.password_generator
phone = variables.phone
postal_code = variables.postal_code
project_email_address = variables.project_email_address
random = variables.random
region_names_list = variables.region_names_list
reply_to_email = variables.reply_to_email
service_now_table_name = variables.service_now_table_name
ses_mfa_email = variables.ses_mfa_email
ses_proj_automation_email = variables.ses_proj_automation_email
short_project_name = variables.short_project_name
sqs_queue_arn = variables.sqs_queue_arn
sqs_queue_name = variables.sqs_queue_name
sqs_queue_url = variables.sqs_queue_url
stack_region_column_name = variables.stack_region_column_name
state = variables.state
string = variables.string
support_email_addresses = variables.support_email_addresses
template_url_2azs = variables.template_url_2azs
template_url_3azs = variables.template_url_3azs
time = variables.time
transaction_id = variables.transaction_id
transaction_id_column_name = variables.transaction_id_column_name
users = variables.users
webdriver = variables.webdriver

############## POLICIES ######################
def func_policies():
	for v in dir(mainpolicies):
		print(v + ' = mainpolicies.' + v)

amazon_ec2_full_access_role_policy = mainpolicies.amazon_ec2_full_access_role_policy
cloudtrail_sns_topic_policy = mainpolicies.cloudtrail_sns_topic_policy
config_role_policy = mainpolicies.config_role_policy
config_role_trust_relationship = mainpolicies.config_role_trust_relationship
config_sns_topic_policy = mainpolicies.config_sns_topic_policy
dummy_cloudtrail_bucket_policy = mainpolicies.dummy_cloudtrail_bucket_policy
dummy_config_bucket_policy = mainpolicies.dummy_config_bucket_policy
initial_bucket_policy_cloudtrail = mainpolicies.initial_bucket_policy_cloudtrail
initial_bucket_policy_config = mainpolicies.initial_bucket_policy_config
initial_queue_policy = mainpolicies.initial_queue_policy
new_saml_role_policy = mainpolicies.new_saml_role_policy
saml_assume_role_policy = mainpolicies.saml_assume_role_policy
sqs_queue_policy = mainpolicies.sqs_queue_policy
vpc_endpoint_policy = mainpolicies.vpc_endpoint_policy
############################################################################
############################################################################
############################################################################
############################################################################
############################################################################



# ddb_add_to_credentials_table()

# iam_password_policy()
# iam_create_alias()

# # iam_create_key_pair()
# cfn_create_and_validate_stack()

# ddb_add_to_account_automation_table()

# s3_update_bucket_policy('cloudtrail')
# s3_update_bucket_policy('config')

# sns_create_topic_cloudtrail()

# cloudtrail()

# iam_create_config_role()
# config()

# support_create_case_enterprise()

# sqs_config_sns_subscribe()
# sqs_update_policy('cloudtrail')
# sqs_cloudtrail_sns_subscribe()
# sqs_cloudtrail_sns_confirm_subscriptions()
# sqs_update_policy('config')

# vpc_create_endpoint()

# iam_saml_provider()











