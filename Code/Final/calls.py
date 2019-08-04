# 1 CFN:
###############################

## SNS + LAMBDA + CFN
delete_sns_cfn()
delete_lambda_policy()

## CFN
delete_vpc_endpoint()
disable_ec2()
delete_stack()

## IAM + DDB
delete_credentials()
delete_parameters()
delete_password_policy()
delete_alias()
# delete_saml_provider()
delete_saml_role()
delete_config_role()

## S3 BUCKET POLICIES
delete_bucket_policy('cloudtrail')
delete_bucket_policy('config')

## SNS CT and Config
delete_sns_cloudtrail()
delete_sns_config_policy()

## CT + CONFIG
delete_cloudtrail()
delete_config()

delete_s3_act_auto()

###############################
# 2 VPC:
###############################

## SQS
delete_sqs_policy()
purge_queue()
delete_sqs_subscriptions_ct()
delete_sqs_subscriptions_config()

delete_vpc_endpoint()

delete_s3_act_auto()




