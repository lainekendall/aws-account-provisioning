import boto3

central_account_key = '************************'
central_account_secret_key = '*************************************'
central_account_number = '00000000000000000'
central_default_region = 'us-east-1'

client_lambda = boto3.client('lambda', aws_access_key_id=central_account_key, aws_secret_access_key=central_account_secret_key, region_name=central_default_region)
lambda_function_name = 'intern-test-sns-function'
lambda_function_arn = 'arn:aws:lambda:' + central_default_region + ':' + central_account_number + ':function:' + lambda_function_name
policy = client_lambda.get_policy(
    FunctionName=lambda_function_name
)

function = client_lambda.get_function(
    FunctionName=lambda_function_name
)


mappings = client_lambda.list_event_source_mappings(
    # EventSourceArn='string',
    FunctionName=lambda_function_name,
)
