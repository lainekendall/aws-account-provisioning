import boto3

client_iam = boto3.client('iam')

response = client_iam.create_role(
    RoleName='Intern-config-role',
    AssumeRolePolicyDocument='{ "Version": "2012-10-17", "Statement": [ { "Sid": "", "Effect": "Allow", "Principal": { "Service": "config.amazonaws.com" }, "Action": "sts:AssumeRole" } ] }'
)

response = client_iam.put_role_policy(
    RoleName='Intern-config-role',
    PolicyName='Config-policy',
  PolicyDocument= '{ "Version": "2012-10-17", "Statement": [ { "Action": [ "appstream:Get*", "autoscaling:Describe*", "cloudformation:DescribeStacks", "cloudformation:DescribeStackEvents", "cloudformation:DescribeStackResource", "cloudformation:DescribeStackResources", "cloudformation:GetTemplate", "cloudformation:List*", "cloudfront:Get*", "cloudfront:List*", "cloudtrail:DescribeTrails", "cloudtrail:GetTrailStatus", "cloudwatch:Describe*", "cloudwatch:Get*", "cloudwatch:List*", "directconnect:Describe*", "dynamodb:GetItem", "dynamodb:BatchGetItem", "dynamodb:Query", "dynamodb:Scan", "dynamodb:DescribeTable", "dynamodb:ListTables", "ec2:Describe*", "elasticache:Describe*", "elasticbeanstalk:Check*", "elasticbeanstalk:Describe*", "elasticbeanstalk:List*", "elasticbeanstalk:RequestEnvironmentInfo", "elasticbeanstalk:RetrieveEnvironmentInfo", "elasticloadbalancing:Describe*", "elastictranscoder:Read*", "elastictranscoder:List*", "iam:List*", "iam:Get*", "kinesis:Describe*", "kinesis:Get*", "kinesis:List*", "opsworks:Describe*", "opsworks:Get*", "route53:Get*", "route53:List*", "redshift:Describe*", "redshift:ViewQueriesInConsole", "rds:Describe*", "rds:ListTagsForResource", "s3:Get*", "s3:List*", "sdb:GetAttributes", "sdb:List*", "sdb:Select*", "ses:Get*", "ses:List*", "sns:Get*", "sns:List*", "sqs:GetQueueAttributes", "sqs:ListQueues", "sqs:ReceiveMessage", "storagegateway:List*", "storagegateway:Describe*", "trustedadvisor:Describe*" ], "Effect": "Allow", "Resource": "*" }]}'																													
)


