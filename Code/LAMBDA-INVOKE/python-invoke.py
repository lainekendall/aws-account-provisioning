import os
import sys
import boto3, json

print('lambda invoke start')
central_account_key = '*******************'
central_account_secret_key = '**************************************'
central_default_region = 'us-east-1'

project_email_address = os.environ['LAMBDA_PROJ_EMAIL']

client_lambda = boto3.client('lambda', aws_access_key_id=central_account_key, aws_secret_access_key=central_account_secret_key, region_name=central_default_region)

print(project_email_address)

info_json = {'projectEmailAddress': project_email_address}
lambda_create_linked_func_name = 'aa-cla'

client_lambda.invoke(
    FunctionName=lambda_create_linked_func_name,
    InvocationType='Event', # |'RequestResponse'|'DryRun',
    # LogType='Tail',
    # ClientContext=project_email_address,
    Payload=json.dumps(info_json)
)

print('lambda invoke success')











