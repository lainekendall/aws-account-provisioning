import boto3
central_account_key = '*******************'
central_account_secret_key = '**************************************'
central_default_region = 'us-east-1'

client_lambda = boto3.client('lambda', aws_access_key_id=central_account_key, aws_secret_access_key=central_account_secret_key, region_name=central_default_region)


client_lambda.update_function_configuration(
    FunctionName='intern-hello',
    Role='arn:aws:iam::465714296386:role/role-name')
# can't have cross account roles used on lambda functions