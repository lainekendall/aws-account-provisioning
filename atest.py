import os
import sys
import boto3
import string, random, json

new_account_key = '**********************'
new_account_secret_key = '*****************************'
new_default_regions = ['us-west-1', 'us-east-1']
cfn_stack_name = 'intern-test-stack-laine'
vpc_endpoint_policy = {
    "Statement": [
        {
            "Action": "*",
            "Effect": "Allow",
            "Resource": "*",
            "Principal": "*"
        }
    ]
}

def password_generator():
	""" Generates a random password for the new account """
	from random import sample
	symbol = string.punctuation
	lower = string.ascii_lowercase
	upper = string.ascii_uppercase
	numeric = string.digits
	seed = sample(lower, 1) + sample(upper, 1) + sample(numeric, 1) + sample(symbol, 1) +\
	sample(lower + upper + numeric + symbol, 16)
	return ''.join(sample(seed, 20))

print( os.environ['LAMBDA_ARGUMENT'])
print( os.environ['LAMBDA_SOURCE'])
print( os.environ['LAMBDA_DATA'])
print( os.environ['LAMBDA_MESSAGE'])
print "Hello World and Beyond"

print(type(os.environ['LAMBDA_MESSAGE']))
message = os.environ['LAMBDA_MESSAGE']
resource_type_start_index = string.find(message, 'ResourceType')
resource_type = message[resource_type_start_index:]
resource_type_end_index = string.find(resource_type, '\n')
resource_type = resource_type[14:resource_type_end_index-1]

resource_status_start_index = string.find(message, 'ResourceStatus')
resource_status = message[resource_status_start_index:]
resource_status_end_index = string.find(resource_status, '\n')
resource_status = resource_status[16:resource_status_end_index-1]
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
			ClientToken=password_generator() ## has to be new every time you do this
		)
		print('vpc endpoint created in ' + region)

if resource_type == 'AWS::CloudFormation::Stack' and resource_status == 'CREATE_COMPLETE':
	# do everything
	print('stack is done now')
	vpc_create_endpoint()

print('with vpc endpoint')
print(resource_status)
print(resource_type)
print('yes done!!')

