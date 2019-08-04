import boto3, time


central_account_key = '************************'
central_account_secret_key = '*************************************'
new_account_key = '************************'
new_account_secret_key = '*********************************************'
central_account_number = '00000000000000000'
new_account_number = '000000000000000000'

service_now_table_name = 'intern-service-now'

## values extracted from the form: ##		change all this:
transaction_id = 'service now test transid hi laine4'
availability_zones = '2'
long_project_name = 'intern project'
short_project_name = 'intproj'
environment = 'alpha'
cost_center = '3000300030'
users = 'laine, nicharee'			# list of usernames
default_region = str(['us-east-1', 'us-west-1'])
creator_name = 'Laine Kendall'
creator_email = 'laine.kendall@autodesk.com'
creator_dept = 'creator dept'
creator_manager = 'creator mgmt'
project_email_address = 'test-email-service-now4@autodesk.com'

######### columns: ###
transaction_id_column_name = 'TransactionID'
service_now_primary_key = 'EmailAddress'
az_column_name = 'AvailabilityZones'
project_name_long_column_name = 'LongProjectName'
project_name_short_column_name = 'ShortProjectName'
environment_column_name = 'Environment'
cost_center_column_name = 'CostCenter'
users_column_name = 'Users'
default_region_column_name = 'DefaultRegions'

creator_name_column_name = 'Creator'
creator_email_column_name = 'CreatorEmailAddress'
creator_dept_column_name = 'CreatorDepartment'
creator_manager_column_name = 'CreatorManager'

#################################################

client_ddb = boto3.client('dynamodb', aws_access_key_id=central_account_key, aws_secret_access_key=central_account_secret_key, region_name='us-east-1')
client_ddb.put_item(
        TableName=service_now_table_name,                                                      # must enter in table name
        Item={
                transaction_id_column_name : {'S' : transaction_id}, 
                service_now_primary_key : {'S' : project_email_address}, 
                az_column_name : {'S' : availability_zones},
                project_name_long_column_name: {'S': long_project_name},
                project_name_short_column_name: {'S': short_project_name},
                environment_column_name: {'S': environment},
                cost_center_column_name: {'S': cost_center},
                users_column_name: {'S': users},
                default_region_column_name: {'S': default_region},
                creator_name_column_name: {'S': creator_name},
                creator_email_column_name: {'S': creator_email},
                creator_dept_column_name: {'S': creator_dept},
                creator_manager_column_name: {'S': creator_manager}
                }
        )   

# ssh -i service-now-mid-servercopy.pem ec2-user@54.88.140.253

# curl -O https://s3-us-west-1.amazonaws.com/nltest1/alan-put.py

