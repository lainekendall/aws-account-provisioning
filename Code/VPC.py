import boto3, json, time

central_account_key = '************************'
central_account_secret_key = '*************************************'
new_account_key = '************************'
new_account_secret_key = '*********************************************'
central_account_number = '00000000000000000'
new_account_number = '000000000000000000'

stack_name = 'intern-test-stack'
stack_region = 'us-east-1'
vpc_endpoint_region = 'us-east-1'

client_cfn = boto3.client('cloudformation', aws_access_key_id=new_account_key, aws_secret_access_key=new_account_secret_key, region_name= stack_region)                              

vpc = client_cfn.describe_stack_resource(
    StackName=stack_name,
    LogicalResourceId='VPC'
)
vpc_id = vpc['StackResourceDetail']['PhysicalResourceId']


internal_route_table = client_cfn.describe_stack_resource(
    StackName=stack_name,
    LogicalResourceId='InternalRouteTable'
)
internal_route_table_id = internal_route_table['StackResourceDetail']['PhysicalResourceId']

internet_route_table = client_cfn.describe_stack_resource(
    StackName=stack_name,
    LogicalResourceId='InternetRouteTable'
)
internet_route_table_id = internet_route_table['StackResourceDetail']['PhysicalResourceId']



########################

client_ec2 = boto3.client('ec2', aws_access_key_id=new_account_key, aws_secret_access_key=new_account_secret_key, region_name=vpc_endpoint_region)

region_names_list = ['us-west-1', 'us-east-1', 'us-west-2', 
'eu-west-1', 'eu-central-1', 'ap-southeast-1', 'ap-northeast-1', 
'ap-southeast-2', 'sa-east-1']


def create_endpoint():
    client_ec2.create_vpc_endpoint(
        DryRun=False,
        VpcId=vpc_id,
        ServiceName='com.amazonaws.' + vpc_endpoint_region + '.s3', 
        PolicyDocument=json.dumps(vpc_policy),
        RouteTableIds=[
          internal_route_table_id,
              internet_route_table_id
            ],
            ClientToken= new_account_number + '_vpc_endpoint_new_token1' ## has to be new every time you do this
        )

vpc_policy = {
    "Statement": [
        {
            "Action": "*",
            "Effect": "Allow",
            "Resource": "*",
            "Principal": "*"
        }
    ]
}

