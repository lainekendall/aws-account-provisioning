import boto3, json

# creates iam role, configures config, deletes config
central_account_key = '************************'
central_account_secret_key = '*************************************'
new_account_key = '************************'
new_account_secret_key = '*********************************************'
central_account_number = '00000000000000000'
new_account_number = '000000000000000000'

config_sns_topic_name = 'intern-test-config-notifications'

config_role_policy_name = 'intern-test-config-role-policy'
config_bucket_name = 'intern-test-config'
config_delivery_channel_name = 'nltest1configdeli'
config_recorder_name = 'nltest1configrec'

config_role_name = 'intern-test-config-role'
config_policy_name = 'Config-policy'
central_account_number = '00000000000'
new_account_number = '052362053110'                                                                                         
new_account_role = 'arn:aws:iam::' + new_account_number + ':role/' + config_role_name 


region_names_list = ['us-east-1', 'us-west-1', 'us-west-2', 
'eu-west-1', 'eu-central-1', 'ap-southeast-1', 'ap-northeast-1', 
'ap-southeast-2', 'sa-east-1']
  

# in new account
def iam_create_role():
    client_iam = boto3.client('iam', aws_access_key_id=new_account_key, aws_secret_access_key=new_account_secret_key)
    client_iam.create_role(
        RoleName=config_role_name,
        AssumeRolePolicyDocument=json.dumps(config_role_trust_relationship)
        )
    client_iam.put_role_policy(
        RoleName=config_role_name,
        PolicyName=config_role_policy_name,
        PolicyDocument= config_role_policy_json
        )
def delete_role():
    client_iam = boto3.client('iam', aws_access_key_id=new_account_key, aws_secret_access_key=new_account_secret_key)
    client_iam.delete_role(
    RoleName=config_role_name
)

# in new account
def config():
    for region in region_names_list:
        client_config = boto3.client('config', aws_access_key_id=new_account_key, aws_secret_access_key=new_account_secret_key, region_name=region) 
        config_topic_arn = 'arn:aws:sns:' + region + ':' + central_account_number + ':' + config_sns_topic_name
        response = client_config.put_configuration_recorder(
        ConfigurationRecorder={
        'name': config_recorder_name,
        'roleARN': new_account_role
        }
        )
        client_config.put_delivery_channel(
        DeliveryChannel={
        'name': config_delivery_channel_name,
        's3BucketName': config_bucket_name,
        #'s3KeyPrefix': 'laine-test',                                                
        'snsTopicARN':  config_topic_arn                            #not sure if we needed it -- have to configure it in every region
        }
        )
        client_config.start_configuration_recorder(
        ConfigurationRecorderName=config_recorder_name                        # same as above in put_configuration_recorder name
        )
    
    
def delete_config():
    for region in region_names_list:
        client_config = boto3.client('config', aws_access_key_id=new_account_key, aws_secret_access_key=new_account_secret_key, region_name=region) 
        client_config.stop_configuration_recorder(
        ConfigurationRecorderName=config_recorder_name
        )
        client_config.delete_delivery_channel(
        DeliveryChannelName= config_delivery_channel_name
        )
  
# this is a general doc and does NOT have to be edited ever
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


# this is a general policy and does NOT have to be edited ever
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

config_role_policy_json = json.dumps(config_role_policy)

  
  

  
  
  
  
  


