import boto3, time
 
central_account_key = '************************'
central_account_secret_key = '*************************************'
new_account_key = '************************'
new_account_secret_key = '*********************************************'
central_account_number = '00000000000000000'
new_account_number = '000000000000000000'
key_pair_name = 'intern-test-key-pair'
app_name = 'interntestappname'			# must be all lowercase letters ONLY
environment = 'test'

central_sns_topic_region = 'us-east-1'		# has to be same as stack region?
central_sns_topic_name = 'intern-test-stack-notifications'			# sns topic to alert people on the status of the stack creation
stack_name = 'intern-test-stack'
stack_region = 'us-east-1'
# 2 AZs template
template_url = 'https://s3-us-west-1.amazonaws.com/nltest1/core-2az.json'
client_cfn = boto3.client('cloudformation', aws_access_key_id=new_account_key, aws_secret_access_key=new_account_secret_key, region_name=stack_region)
client_sns = boto3.client('sns', aws_access_key_id=central_account_key, aws_secret_access_key=central_account_secret_key, region_name=central_sns_topic_region)


# create stack in new account
# sns send out messages from central account
def cloudformation():
	response = client_cfn.create_stack(
	    StackName=stack_name,			# change this
	    TemplateURL=template_url, #or 3 AZ template
	    Parameters=[

			{'ParameterKey':'AppKeyName', 'ParameterValue': key_pair_name, 'UsePreviousValue':False},		# change this
			{'ParameterKey':'ApplicationSubnetCidrAZ1','ParameterValue':'10.43.10.128/26','UsePreviousValue': False},
			{'ParameterKey':'ApplicationSubnetCidrAZ2','ParameterValue':'10.43.10.192/26','UsePreviousValue': False},
			{'ParameterKey':'AppName','ParameterValue': app_name,'UsePreviousValue':False},			# change this
			{'ParameterKey':'BastionInstanceType','ParameterValue':'t2.micro','UsePreviousValue':False},
			{'ParameterKey':'CorporateCidrIp','ParameterValue':'10.0.0.0/8','UsePreviousValue': False},
			{'ParameterKey':'DatabaseSubnetCidrAZ1','ParameterValue':'10.43.11.192/27','UsePreviousValue': False},
			{'ParameterKey':'DatabaseSubnetCidrAZ2','ParameterValue':'10.43.11.224/27','UsePreviousValue': False},
			{'ParameterKey':'EnvironmentName','ParameterValue': environment, 'UsePreviousValue':False},		#possibly change this...?
			{'ParameterKey':'InternalLoadBalancerSubnetCidrAZ1','ParameterValue':'10.43.11.128/27','UsePreviousValue': False},
			{'ParameterKey':'InternalLoadBalancerSubnetCidrAZ2','ParameterValue':'10.43.11.160/27','UsePreviousValue': False},
			{'ParameterKey':'InternetLoadBalancerSubnetCidrAZ1','ParameterValue':'10.43.10.0/26','UsePreviousValue': False},
			{'ParameterKey':'InternetLoadBalancerSubnetCidrAZ2','ParameterValue':'10.43.10.64/26','UsePreviousValue': False},
			{'ParameterKey':'NATAMI','ParameterValue':'default','UsePreviousValue': False},
			{'ParameterKey':'NATInstanceType','ParameterValue':'t2.micro','UsePreviousValue': False},
			{'ParameterKey':'PresentationSubnetCidrAZ1','ParameterValue':'10.43.11.0/26','UsePreviousValue': False},
			{'ParameterKey':'PresentationSubnetCidrAZ2','ParameterValue':'10.43.11.64/26','UsePreviousValue': False},
			{'ParameterKey':'VPCCidr','ParameterValue':'10.43.10.0/23','UsePreviousValue': False}
			        
	    ],
	    DisableRollback=False,
	    TimeoutInMinutes=123,
	    
	    Capabilities=[
	        'CAPABILITY_IAM',
	    ]
	)


def validate():
	# 15 minute timer starts now:
	timeout = time.time() + 60*15
	while True:
		stack_events = client_cfn.describe_stack_events(StackName=stack_name)			# change this (dependent upon earlier code)
		resource_status = stack_events['StackEvents'][0]['ResourceStatus']
		resource_type = stack_events['StackEvents'][0]['ResourceType']
		# time_stamp = stack_events['StackEvents'][0]['Timestamp']
		if resource_type == 'AWS::CloudFormation::Stack': # this means the stack has either failed or completed
			if resource_status == 'CREATE_COMPLETE':
				message='Stack Creation complete'
				subject='CREATE_COMPLETE'
				print('complete')
				break
			if resource_status != 'CREATE_IN_PROGRESS': #the stack creation has failed
				message='Stack Creation failed to complete'
				subject='CREATE_FAILED'
				print('fail 1')
				break
		if resource_status == 'CREATE_FAILED': # if ANY event has failed that means they all will
			message='Stack Creation failed to complete'
			subject='CREATE_FAILED'
			print('fail 2')
			break
		if timeout < time.time(): # the creation is taking too long
			#send sns message saying timeout
			message='Stack Creation did not complete in 15 minutes'
			subject='Timeout'
			print('timeout')
			break
	return (message, subject)

def publish():
	central_sns_topic_arn = 'arn:aws:sns:' + central_sns_topic_region + ':' + central_account_number + ':' + central_sns_topic_name
	client_sns.publish(
	    TopicArn=central_sns_topic_arn,
	    Message=message,
	    Subject=subject,
	    # MessageStructure='string',
	    # MessageAttributes={
	    #     'String': {
	    #         'DataType': 'String',
	    #         # 'StringValue': 'string',
	    #         # 'BinaryValue': b'bytes'
	    #     }
	    # }
	)

## code: ##
# cloudformation()
# message, subject = validate()
# publish()	
