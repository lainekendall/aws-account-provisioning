
################ CloudFormation: create and validate stack, notify correct people if failed ##############################
message, subject = '', ''
stack_resource_list = []
resource_start_dict = {} #stores the starting timestamp of each resource
resource_end_dict = {} #stores the finishing timestamp of each resource
events_by_region = {}
stack_timeout = 0

def cfn_create_stack():
	""" Creates a CloudFormation stack in each specified region for the new account """
	global message, subject, stack_timeout	#only need for lists and strings
	if availability_zones == '2':
		template_url = template_url_2azs
		cfn_parameters = cfn_parameters_2az
	else:
		# add necessary parameters for third availability zone
		template_url = template_url_3azs
		cfn_parameters = cfn_parameters_3az
	for region in new_default_regions:
		# create the dictionaries:
		resource_start_dict[region] = {}
		resource_end_dict[region] = {}
		events_by_region[region] = []
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
	""" Extracts stack events in each region and store them in 'events_list_by_region' dictionary """
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
	""" Validates the stack in each region """
  
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
	""" Extracts LogicalResourceId attribute of each resource in a specified stack and stores it in 'stack_resource_list' dictionary """
  
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
	""" Extracts the timestamps (the time the resource creation is initiated and the time the resource creation is completed)
  		of each stack resource in each region and stores them in 'resource_start_dict' and 'resource_end_dict' dictionaries correspondingly """
  
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
	client_ddb.put_item(
		TableName=account_automation_table_name,                                                      # must enter in table name
		Item=table_item_dict
	)
	print('act auto table put complete')












