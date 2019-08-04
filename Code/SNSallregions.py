import boto3, json

## code: ##
# sns('cloudtrail')
# sns('config')

# configures sns topics for both cloudtrail and config, deletes topics
central_account_key = '************************'
central_account_secret_key = '*************************************'
new_account_key = '************************'
new_account_secret_key = '*********************************************'
central_account_number = '00000000000000000'
new_account_number = '000000000000000000'


cloudtrail_sns_topic_name = 'intern-test-cloudtrail-notifications'	# folder in bucket (after this will be foler name 'AWSLogs' then account #)
sns_policy_label = 'cloudtrail sns policy label'

config_sns_topic_name = 'intern-test-config-notifications'

region_names_list = ['us-east-1', 'us-west-1', 'us-west-2', 
'eu-west-1', 'eu-central-1', 'ap-southeast-1', 'ap-northeast-1', 
'ap-southeast-2', 'sa-east-1']



# for config this only happens once!!
def sns(service):
	if service == 'cloudtrail':		# sns = new
		sns_access_key = new_account_key
		sns_secret_access_key = new_account_secret_key
		topic_name = cloudtrail_sns_topic_name
		sns_account_number = new_account_number
		topic_policy = cloudtrail_sns_topic_policy
	elif service == 'config':		# sns = central
		sns_access_key = central_account_key
		sns_secret_access_key = central_account_secret_key
		topic_name = config_sns_topic_name
		sns_account_number = central_account_number
		topic_policy = config_sns_topic_policy
	# create topic
	for region in region_names_list:
		topic_arn = 'arn:aws:sns:' +  region + ':' + sns_account_number + ':' + topic_name
		client_sns = boto3.client('sns', aws_access_key_id=sns_access_key, aws_secret_access_key=sns_secret_access_key, region_name=region)
		client_sns.create_topic(
		Name=topic_name, 
		)
		# add policy
		topic_policy["Statement"][0]["Resource"] = topic_arn
		topic_policy_json = json.dumps(topic_policy)	#convert to JSON format

		client_sns.set_topic_attributes(
    	TopicArn=topic_arn,
    	AttributeName='Policy',
    	AttributeValue=topic_policy_json
		)

def delete_sns(service):
	if service == 'cloudtrail':		# sns = new
		sns_access_key = new_account_key
		sns_secret_access_key = new_account_secret_key
		topic_name = cloudtrail_sns_topic_name
		sns_account_number = new_account_number
		topic_policy = cloudtrail_sns_topic_policy
	elif service == 'config':		# sns = central
		sns_access_key = central_account_key
		sns_secret_access_key = central_account_secret_key
		topic_name = config_sns_topic_name
		sns_account_number = central_account_number
		topic_policy = config_sns_topic_policy
	for region in region_names_list:
		topic_arn = 'arn:aws:sns:' +  region + ':' + sns_account_number + ':' + topic_name
		client_sns = boto3.client('sns', aws_access_key_id=sns_access_key, aws_secret_access_key=sns_secret_access_key, region_name=region)
		client_sns.delete_topic(
		TopicArn=topic_arn, 
		)


cloudtrail_sns_topic_policy = {	# this says that cloudtrail service is allowed to publish into whichever topic arns you put in resource
		"Version": "2012-10-17",
 
		"Statement": [
		{
   
		"Sid": "AWSCloudTrailSNSPolicy20140219",  
		"Effect": "Allow",
		# 'resource' here: its own topic arn
		"Principal": {
   		    	
			"AWS": [
				"arn:aws:iam::000000000000:root",
				"arn:aws:iam::000000000000:root",
				"arn:aws:iam::000000000000:root",
				"arn:aws:iam::000000000000:root",
				"arn:aws:iam::000000000000:root",
				"arn:aws:iam::000000000000:root",
				"arn:aws:iam::000000000000:root",
				"arn:aws:iam::000000000000:root",
				"arn:aws:iam::000000000000:root"
				]  
			},
			"Action": "SNS:Publish",
		}
		]
		}

config_sns_topic_policy = {			# this says that config is allowed to publish into the topic arn you put in resource (its own topic arn)
          "Id": "Policy1415489375392",
          "Statement": [
            {
              "Sid": "AWSConfigSNSPolicy20150201",
              "Action": [
                "SNS:Publish"
              ],				# new account info will NEVER go in here, once this is set it never changes
              "Effect": "Allow",
              # 'resource' here: its own topic arn
              "Principal": {
                "AWS": [
                  "arn:aws:iam::000000000000:root",
                  "arn:aws:iam::000000000000:root",
                  "arn:aws:iam::000000000000:root",
                  "arn:aws:iam::000000000000:root"
                ]
              }
            }
          ]
        }


