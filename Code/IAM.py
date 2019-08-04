import boto3
import boto3, time

client_iam = boto3.client('iam')
client_ddb = boto3.client('dynamodb')

response = client_iam.update_account_password_policy(
    MinimumPasswordLength=8,
    RequireSymbols=True,
    RequireNumbers=True,
    RequireUppercaseCharacters=True,
    RequireLowercaseCharacters=True,
    AllowUsersToChangePassword=True,
    MaxPasswordAge=90,
    HardExpiry=False, 
)


response = client_iam.create_account_alias(
    AccountAlias='testalias3'			# change this
)

# add alias name and URL to dynamodb
response = client_ddb.put_item(
    TableName='TestFinal',														# must enter in original table name used 
    Item={																	#all of this is specific to table (check dynamodb codeshare)
        'Parameter': {
            'S': 'Account Alias',												# 'S' means string, do not change this
            },																					# 'Parameter' and 'Value' specific to table created, might be changed, dependent on intial table created 
    		'Value': {
      			'S': 'testalias3'										# this is same as in create_account_alias up above
            }
    }
)

response = client_ddb.put_item(
    TableName='TestFinal',														# must enter in original table name used 
    Item={																	#all of this is specific to table (check dynamodb codeshare)
        'Parameter': {
            'S': 'IAM users sign-in link',												# 'S' means string, do not change this
            },																					# 'Parameter' and 'Value' specific to table created, might be changed, dependent on intial table created 
    		'Value': {
      			'S': 'https://testalias3.signin.aws.amazon.com/console'				# change the middle of this
            }
    }
)


# response = client_iam.delete_account_alias(
#     AccountAlias='testalias'
# )











