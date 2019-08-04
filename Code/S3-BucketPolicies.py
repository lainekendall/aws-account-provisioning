import boto3, json

central_account_key = '************************'
central_account_secret_key = '*************************************'
new_account_key = '************************'
new_account_secret_key = '*********************************************'
central_account_number = '00000000000000000'
new_account_number = '000000000000000000'

client_s3 = boto3.client('s3', aws_access_key_id=central_account_key, aws_secret_access_key=central_account_secret_key)
config_bucket_name = 'intern-test-config'
config_bucket_arn = 'arn:aws:s3:::' + config_bucket_name
cloudtrail_bucket_name = 'intern-test-cloudtrail'
cloudtrail_bucket_arn = 'arn:aws:s3:::' + cloudtrail_bucket_name

central_account_cloudtrail_folder_arn = cloudtrail_bucket_arn + '/AWSLogs/' + central_account_number + '/*'
central_account_config_folder_arn = config_bucket_arn + '/AWSLogs/' + central_account_number + '/*'
new_account_cloudtrail_folder_arn = cloudtrail_bucket_arn + '/AWSLogs/' + new_account_number + '/*'
new_account_config_folder_arn = config_bucket_arn + '/AWSLogs/' + new_account_number + '/*'



# done only once ever
def add_bucket_and_folder_to_policies():
	initial_bucket_policy_cloudtrail["Statement"][0]["Resource"] = cloudtrail_bucket_arn		# this relies on the policy's statments being in a specific order
	initial_bucket_policy_config["Statement"][0]["Resource"] = config_bucket_arn
	initial_bucket_policy_cloudtrail["Statement"][1]["Resource"] = central_account_cloudtrail_folder_arn		# this relies on the policy's statments being in a specific order
	initial_bucket_policy_config["Statement"][1]["Resource"] = [central_account_config_folder_arn, central_account_config_folder_arn]

# only done once
def put_initial_bucket_policy(service):		# either cloudtrail or config
	if service == 'cloudtrail':
		bucket_name = cloudtrail_bucket_name
		initial_bucket_policy = initial_bucket_policy_cloudtrail
	elif service == 'config':
		bucket_name = config_bucket_name
		initial_bucket_policy = initial_bucket_policy_config
	initial_bucket_policy_json = json.dumps(initial_bucket_policy)			# convert to JSON
	client_s3.put_bucket_policy(
	    Bucket=bucket_name,								
	    Policy= initial_bucket_policy_json
	)

def update_bucket_policy(service):
	if service == 'cloudtrail':
		print('cloudtrail')
		bucket_name = cloudtrail_bucket_name
		new_account_folder_arn = new_account_cloudtrail_folder_arn
	elif service == 'config':
		print('config')
		bucket_name = config_bucket_name
		new_account_folder_arn = new_account_config_folder_arn

	bucket_policy_json = client_s3.get_bucket_policy(
	    Bucket=bucket_name					
		)["Policy"]

	bucket_policy = json.loads(bucket_policy_json)		# convert to python dict
	resources = bucket_policy["Statement"][1]["Resource"]
	if type(resources) == list:		#this means it's a list, bc there are 2 or more resources
		bucket_policy["Statement"][1]["Resource"] = resources + [new_account_folder_arn]
		print('list type')
	elif type(resources) == unicode:
		bucket_policy["Statement"][1]["Resource"] = [resources] + [new_account_folder_arn]
		print('unicode type')
	bucket_policy_json = json.dumps(bucket_policy)			# convert to JSON
	client_s3.put_bucket_policy(
	    Bucket=bucket_name,								
	    Policy= bucket_policy_json
	)


## code: ##
# add_bucket_to_policies()
# put_initial_bucket_policy('cloudtrail')
# put_initial_bucket_policy('config')




initial_bucket_policy_cloudtrail = {
	"Version": "2012-10-17",
	"Statement": [
		{
			"Sid": "AWSCloudTrailAclCheck20131101",
			"Effect": "Allow",
			"Principal": {
				"AWS": [
					"arn:aws:iam::************:root",
					"arn:aws:iam::************:root",
					"arn:aws:iam::************:root",
					"arn:aws:iam::************:root",
					"arn:aws:iam::************:root",
					"arn:aws:iam::************:root",
					"arn:aws:iam::************:root",
					"arn:aws:iam::************:root",
					"arn:aws:iam::************:root"
				]
			},
			"Action": "s3:GetBucketAcl",
			"Resource": 'place holder'		# this is where the cloudtrail bucket arn goes
		},
		{
			"Sid": "AWSCloudTrailWrite20131101",
			"Effect": "Allow",
			"Principal": {
				"AWS": [
					"arn:aws:iam::************:root",
					"arn:aws:iam::************:root",
					"arn:aws:iam::************:root",
					"arn:aws:iam::************:root",
					"arn:aws:iam::************:root",
					"arn:aws:iam::************:root",
					"arn:aws:iam::************:root",
					"arn:aws:iam::************:root",
					"arn:aws:iam::************:root"
				]
			},
			"Action": "s3:PutObject",
			"Resource": [	# this is where the folder in the bucket goes (looks like: "arn:aws:s3:::nltest1/AWSLogs/************/*")
							# new one will be added everytime a new account is created
			],
			"Condition": {
				"StringEquals": {
					"s3:x-amz-acl": "bucket-owner-full-control"
				}
			}
		}
	]
}

initial_bucket_policy_config = {
	"Version": "2012-10-17",
	"Statement": [
		{
			"Sid": "AWSConfigBucketPermissionsCheck",
			"Effect": "Allow",
			"Principal": {
				"Service": "config.amazonaws.com"
			},
			"Action": "s3:GetBucketAcl",
			"Resource": 	'place holder' # this is where the config bucket arn goes (only one)
		},
		{
			"Sid": " AWSConfigBucketDelivery",
			"Effect": "Allow",
			"Principal": {
				"Service": "config.amazonaws.com"
			},
			"Action": "s3:PutObject",
			"Resource": [	# this is where the folder arn goes (new one added each time new account is created)
			],
			"Condition": {
				"StringEquals": {
					"s3:x-amz-acl": "bucket-owner-full-control"
				}
			}
		}
	]
}






