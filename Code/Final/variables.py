import boto3, time, json, string, random
from selenium import webdriver
from selenium.webdriver.common.keys import Keys

######### DO NOT CHANGE (most likely) #########
##############################################################################
region_names_list = ['us-east-1', 'us-west-1', 'us-west-2', 
'eu-west-1', 'eu-central-1', 'ap-southeast-1', 'ap-northeast-1', 
'ap-southeast-2', 'sa-east-1']
cloudtrail_global_dict = {'us-east-1': True, 'us-west-2': False, 'us-west-1': False, 
'eu-west-1': False, 'eu-central-1': False, 'ap-southeast-1': False, 'ap-northeast-1': False, 
'ap-southeast-2': False, 'sa-east-1': False}


######### all variables that will be given to us from CENTRAL acount #########
##############################################################################
central_account_number = '964355697993'
central_account_name = 'eis-aws-account-automation'
central_account_key = 'AKIAJEMUZ33AYPHIJ37A'
central_account_secret_key = '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'
central_default_region = 'us-east-1'

## DDB tables ##
credentials_table_name = 'intern-test-credentials-table'
## credentials column names ##
account_number_column_name = 'Account Number'
transaction_id_column_name = 'Transaction ID'
email_address_column_name = 'Email'
password_column_name = 'Password'

account_automation_table_name = 'intern-test-account-automation-table'
# AA column names
acount_alias_column_name = 'Account Alias'
stack_region_column_name = 'CFN Stack Region(s)'


service_now_table_name = 'intern-test-no-space-service-now'

## S3 Buckets/urls ##
config_bucket_name = 'intern-test-config'
# config_bucket_arn = # ?? is this needed?
cloudtrail_bucket_name = 'intern-test-cloudtrail'
# cloudtrail_bucket_arn = # ??
template_url_2azs = 'https://s3-us-west-1.amazonaws.com/nltest1/core-2az.json'
template_url_3azs = 'https://s3-us-west-1.amazonaws.com/nltest1/core-3az.json'

## SNS Topics ##
config_sns_topic_name = 'intern-test-config-notifications' # exists in all regions
cfn_sns_topic_name = 'intern-test-cfn-stack-notifications' # same region(s) as cfn stack

## IAM ##
central_saml_provider_name = 'adsk-saml'        # to get metadata
# roles?? already existing?? #

## SQS ##
sqs_queue_name = 'intern-test-queue'

## Email these people ##
support_email_addresses = ['laine.kendall@autodesk.com']    # list of strings
ses_proj_automation_email = 'laine.kendall@autodesk.com' # 'eis.aws.support@autodesk.com'
ses_mfa_email = 'laine.kendall@autodesk.com'
reply_to_email = 'laine.kendall@autodesk.com'

########### from javascript file: #########
#####################################################################################################################################
# transaction_id = os.environ['LAMBDA_TRANS_ID']
# availability_zones = os.environ['LAMBDA_AZ']
# long_project_name = os.environ['LAMBDA_LONG_NAME']
# short_project_name = os.environ['LAMBDA_SHORT_NAME']
# environment = os.environ['LAMBDA_ENVIRONMENT']
# cost_center = os.environ['LAMBDA_COST_CENTER']
# users = os.environ['LAMBDA_USERS']     # list of usernames
# new_default_regions = os.environ['LAMBDA_DEFAULT_REGION']
# creator_name = os.environ['LAMBDA_CREATOR']
# creator_email = os.environ['LAMBDA_CREATOR_EMAIL']
# creator_dept = os.environ['LAMBDA_CREATOR_DEPT']
# creator_manager = os.environ['LAMBDA_CREATOR_MANAGER']

transaction_id = 'TRANS_ID'
availability_zones = '2'
long_project_name = 'LONG_NAME'
short_project_name = 'shortname'
environment = 'alpha'
cost_center = 'COST_CENTER'
users = 'USERS'     # list of usernames
new_default_regions = ['us-west-1', 'us-east-1']
creator_name = 'CREATOR'
creator_email = 'laine.kendall@autodesk.com'
creator_dept = 'CREATOR_DEPT'
creator_manager = 'CREATOR_MANAGER'

if type(new_default_regions) != list:
    new_default_regions = [new_default_regions]


########## for selenium ###########
#####################################################################################################################################


aws_account_full_name = 'eis-aws-account-automation'
project_email_address = 'aws.eis.' + short_project_name + '.' + environment + '@autodesk.com'
# passsword ###### must have functions before this
company = 'Autodesk'
address = '111 McInnis Parkway'
city = 'San Rafael'
state = 'California'
postal_code = '94903'
phone = '415-507-5000'


####### NAME THESE #####
######################################################################
config_role_name = 'intern-test-config-role'
config_role_policy_name = 'intern-test-config-role-policy'
config_delivery_channel_name = 'nltest1configdeli'
config_recorder_name = 'nltest1configrec'

cfn_stack_name = 'intern-test-stack-laine'

cloudtrail_sns_topic_name = 'laine-test-cloudtrail-notifications' # NEW: 'cloudtrail-notifications'
cloudtrail_name = 'intern-training-trail-name'					# NEW: adsk-eis-cloudtrail
cloudtrail_sns_policy_label = 'cloudtrail sns policy label'

new_saml_provider_name = 'intern-test-saml-provider'
new_saml_role_name = 'intern-test-saml-role'
new_saml_role_policy_name = 'intern-test-saml-role-policy'

iam_access_key_user = 'intern-testaws' # for selenium



##### CENTRAL ARNs and variable dependent ###### 
######################################################################
config_bucket_arn = 'arn:aws:s3:::' + config_bucket_name
cloudtrail_bucket_arn = 'arn:aws:s3:::' + cloudtrail_bucket_name
sqs_queue_arn = "arn:aws:sqs:" + central_default_region + ":" + central_account_number + ":" + sqs_queue_name
cfn_sns_topic_arn = 'arn:aws:sns:' + central_default_region + ':' + central_account_number + ':' + cfn_sns_topic_name
central_saml_provider_arn = 'arn:aws:iam::' + central_account_number + ':saml-provider/' + central_saml_provider_name

new_account_alias = 'adsk-eis-' + short_project_name
# this is all for policy stuff: #
central_account_cloudtrail_folder_arn = cloudtrail_bucket_arn + '/AWSLogs/' + central_account_number + '/*'
central_account_config_folder_arn = config_bucket_arn + '/AWSLogs/' + central_account_number + '/*'


###### ?????Q???? #######
app_name = short_project_name

def password_generator():
    from random import sample
    symbol = string.punctuation
    lower = string.ascii_lowercase
    upper = string.ascii_uppercase
    numeric = string.digits
    seed = sample(lower, 1) + sample(upper, 1) + sample(numeric, 1) + sample(symbol, 1) +\
    sample(lower + upper + numeric + symbol, 16)
    return ''.join(sample(seed, 20))

password = password_generator()

################ selenium must be done here ################################
################################################################################################
## get new access keys
new_account_key = 'AKIAJN2ULCJCKKOVOYSQ'
new_account_secret_key = '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'

#### CLIENTS ######
client_iam_new = boto3.client('iam', aws_access_key_id=new_account_key, aws_secret_access_key=new_account_secret_key)
client_iam_central = boto3.client('iam', aws_access_key_id=central_account_key, aws_secret_access_key=central_account_secret_key)
client_sns_central = boto3.client('sns', aws_access_key_id=central_account_key, aws_secret_access_key=central_account_secret_key, region_name=central_default_region)
client_ddb = boto3.client('dynamodb', aws_access_key_id=central_account_key, aws_secret_access_key=central_account_secret_key, region_name=central_default_region)
client_s3 = boto3.client('s3', aws_access_key_id=central_account_key, aws_secret_access_key=central_account_secret_key)
client_sqs = boto3.client('sqs', aws_access_key_id=central_account_key, aws_secret_access_key=central_account_secret_key, region_name=central_default_region)
client_support = boto3.client('support', aws_access_key_id=new_account_key, aws_secret_access_key=new_account_secret_key)
client_ses = boto3.client('ses', aws_access_key_id=central_account_key, aws_secret_access_key=central_account_secret_key, region_name=central_default_region)


####### NEW ARNS ... and variables gotten from function calls, client calls, etc. #####
######################################################################
get_queue_url = client_sqs.get_queue_url(
    QueueName=sqs_queue_name,
    QueueOwnerAWSAccountId=central_account_number)
sqs_queue_url = get_queue_url['QueueUrl']
new_account_number = client_iam_new.get_user()['User']['Arn'][13:25]

config_role_arn = 'arn:aws:iam::' + new_account_number + ':role/' + config_role_name 
new_saml_provider_arn = 'arn:aws:iam::' + new_account_number + ':saml-provider/' + new_saml_provider_name
new_account_cloudtrail_folder_arn = cloudtrail_bucket_arn + '/AWSLogs/' + new_account_number + '/*'
new_account_config_folder_arn = config_bucket_arn + '/AWSLogs/' + new_account_number + '/*'


######### CFN Parameters #########
#####################################################################################################################
cfn_parameters_2az = [
    {'ParameterKey':'ApplicationSubnetCidrAZ1','ParameterValue':'10.43.10.128/26','UsePreviousValue': False},
    {'ParameterKey':'ApplicationSubnetCidrAZ2','ParameterValue':'10.43.10.192/26','UsePreviousValue': False},
    {'ParameterKey':'AppName','ParameterValue': app_name,'UsePreviousValue':False},         # change this
    {'ParameterKey':'BastionInstanceType','ParameterValue':'t2.micro','UsePreviousValue':False},
    {'ParameterKey':'CorporateCidrIp','ParameterValue':'10.0.0.0/8','UsePreviousValue': False},
    {'ParameterKey':'DatabaseSubnetCidrAZ1','ParameterValue':'10.43.11.192/27','UsePreviousValue': False},
    {'ParameterKey':'DatabaseSubnetCidrAZ2','ParameterValue':'10.43.11.224/27','UsePreviousValue': False},
    {'ParameterKey':'EnvironmentName','ParameterValue': environment, 'UsePreviousValue':False},     #possibly change this...?
    {'ParameterKey':'InternalLoadBalancerSubnetCidrAZ1','ParameterValue':'10.43.11.128/27','UsePreviousValue': False},
    {'ParameterKey':'InternalLoadBalancerSubnetCidrAZ2','ParameterValue':'10.43.11.160/27','UsePreviousValue': False},
    {'ParameterKey':'InternetLoadBalancerSubnetCidrAZ1','ParameterValue':'10.43.10.0/26','UsePreviousValue': False},
    {'ParameterKey':'InternetLoadBalancerSubnetCidrAZ2','ParameterValue':'10.43.10.64/26','UsePreviousValue': False},
    {'ParameterKey':'NATAMI','ParameterValue':'default','UsePreviousValue': False},
    {'ParameterKey':'NATInstanceType','ParameterValue':'t2.micro','UsePreviousValue': False},
    {'ParameterKey':'PresentationSubnetCidrAZ1','ParameterValue':'10.43.11.0/26','UsePreviousValue': False},
    {'ParameterKey':'PresentationSubnetCidrAZ2','ParameterValue':'10.43.11.64/26','UsePreviousValue': False},
    {'ParameterKey':'VPCCidr','ParameterValue':'10.43.10.0/23','UsePreviousValue': False}            
        ]
cfn_parameters_3az = cfn_parameters_2az[:]

cfn_parameters_3az += [{'ParameterKey': 'ApplicationSubnetCidrAZ3','ParameterValue':'10.43.11.0/26','UsePreviousValue': False}]
cfn_parameters_3az += [{'ParameterKey': 'DatabaseSubnetCidrAZ3','ParameterValue':'10.43.11.0/26','UsePreviousValue': False}]
cfn_parameters_3az += [{'ParameterKey': 'InternalLoadBalancerSubnetCidrAZ3','ParameterValue':'10.43.11.0/26','UsePreviousValue': False}]
cfn_parameters_3az += [{'ParameterKey': 'InternetLoadBalancerSubnetCidrAZ3','ParameterValue':'10.43.11.0/26','UsePreviousValue': False}]
cfn_parameters_3az += [{'ParameterKey': 'PresentationSubnetCidrAZ3','ParameterValue':'10.43.11.0/26','UsePreviousValue': False}]


