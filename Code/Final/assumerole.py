import boto3

client_sts = boto3.client('sts', aws_access_key_id="*********************", aws_secret_access_key="****************************")

payer_account_number = '0000000000000'
new_account_role_name = 'awsconfig-role' #'PayerAccountAccessRole'
new_account_role_arn = 'arn:aws:iam::' + new_account_number + ':role/' + new_account_role_name
# role will be in new account
response = client_sts.assume_role(
    RoleArn=new_account_role_arn,
    RoleSessionName='role-session-1',
    DurationSeconds=3600,
)

# client_iam.get_policy(
#     PolicyArn='string'
# )

# "StackId='arn:aws:cloudformation:us-east-1:************:stack/intern-test-stack-laine3/e62deaf0-4156-11e5-b2d7-50d501114c2c'"
# Timestamp='2015-08-13T01:02:48.086Z'\
# EventId='InternalSubnetAclAssociation2-CREATE_IN_PROGRESS-2015-08-13T01:02:48.086Z'\
# LogicalResourceId='InternalSubnetAclAssociation2'\
# Namespace='************'
# ResourceProperties='{\"SubnetId\":\"subnet-93c4f8e4\",\"NetworkAclId\":\"acl-f3e21697\"}\n'
# ResourceStatus='CREATE_IN_PROGRESS'
# ResourceStatusReason=''\
# ResourceType='AWS::EC2::SubnetNetworkAclAssociation'\
# StackName='intern-test-stack-laine3'\






