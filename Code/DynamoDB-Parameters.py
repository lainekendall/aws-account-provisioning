import boto3, time
dynamodb_region = 'us-east-1'
stack_region = 'us-east-1'
 
central_account_key = '************************'
central_account_secret_key = '*************************************'
new_account_key = '************************'
new_account_secret_key = '*********************************************'
central_account_number = '00000000000000000'
new_account_number = '000000000000000000'

transaction_id = 'transaction id'
email_address = 'email address used to create account'
password = 'auto generated password'
stack_name = 'intern-test-stack'

client_iam = boto3.client('iam', aws_access_key_id=new_account_key, aws_secret_access_key=new_account_secret_key)
new_account_number = client_iam.get_user()['User']['Arn'][13:25]                # best/only way to get userID



client_cfn = boto3.client('cloudformation', aws_access_key_id=new_account_key, aws_secret_access_key=new_account_secret_key, region_name=stack_region) 
client_ddb = boto3.client('dynamodb', aws_access_key_id=central_account_key, aws_secret_access_key=central_account_secret_key, region_name=dynamodb_region)


account_automation_table_name = 'intern-test-account-automation-table'      # stack parameters and events and their times
credentials_table_name = 'intern-test-credentials-table'
service_now_table_name = 'intern-test-SNtable'

# testing purposes only
def create_table(table_name):
    client_ddb.create_table(
        AttributeDefinitions=[
            {
                'AttributeName': 'Transaction ID', 
                'AttributeType': 'S'
            },
            {
                'AttributeName': 'Account Number', 
                'AttributeType': 'S'
            }],
        TableName=table_name,  
        KeySchema=[
            {
                'AttributeName': 'Transaction ID',
                'KeyType': 'HASH'
            },
        ],
        GlobalSecondaryIndexes=[
            {
                'IndexName': 'Account-Number-Index',
                'KeySchema': [
                    {
                        'AttributeName': 'Account Number',
                        'KeyType': 'HASH'
                    },
                ],
                'Projection': {
                    'ProjectionType': 'ALL'             ## ?????
                },
                'ProvisionedThroughput': {
                    'ReadCapacityUnits': 1,              ## this adds to below provisioned throughput
                    'WriteCapacityUnits': 1             
                }
            },
        ],  
        ProvisionedThroughput={                     # ^^^
            'ReadCapacityUnits': 1,             ## this adds to above provisioned throughput
            'WriteCapacityUnits': 1
        }
    )
def add_to_table(table_name):
    stack_description = client_cfn.describe_stacks(StackName=stack_name) 
    parameters_list = stack_description['Stacks'][0]['Parameters']
    parameters_item_dict = {'Transaction ID' : {'S' : transaction_id}, 'Account Number' : {'S' : new_account_number}}
    if table_name == account_automation_table_name:
        for dict_item in parameters_list:
            key = dict_item['ParameterKey']
            value = dict_item['ParameterValue']
            parameters_item_dict[key] = {'S': value}
        client_ddb.put_item(
            TableName=account_automation_table_name,                                                      # must enter in table name
            Item=parameters_item_dict)
    elif table_name == credentials_table_name:
        client_ddb.put_item(
        TableName=credentials_table_name,                                                      # must enter in table name
        Item={
                'Transaction ID' : {'S' : transaction_id}, 
                'Account Number' : {'S' : new_account_number},
                'Email': {'S': email_address},
                'Password': {'S': password}
                }
        )   

## code: ##
# create_table(account_automation_table_name)
# create_table(credentials_table_name)

## must be some time between these two to allow for tables to create

# add_to_table(account_automation_table_name)
# add_to_table(credentials_table_name)







    
    
