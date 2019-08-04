import boto3, json

central_account_key = '************************'
central_account_secret_key = '*************************************'
new_account_key = '************************'
new_account_secret_key = '*********************************************'
central_account_number = '00000000000000000'
new_account_number = '000000000000000000'

cloudtrail_sns_topic_name = 'intern-test-cloudtrail-notifications'
cloudtrail_name = 'intern-training-trail-name'
s3_bucket_name = 'nltest1'						# (adsk-eis-cloudtrail)
s3_prefix = 'laine-test'
region = 'us-east-1'
topic_arn = 'arn:aws:sns:' +  region + ':' + account_number + ':' + cloudtrail_sns_topic_name

sns_topic_policy = {
 
	"Version": "2012-10-17",
 
	"Statement": [
	{
   
		"Sid": "AWSCloudTrailSNSPolicy20140219",  
		"Effect": "Allow",
   
		"Principal": {
   		    	
			"AWS": [
				"arn:aws:iam::000000000000:root",
				"arn:aws:iam::000000000000::root",
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


sns_topic_policy["Statement"][0]["Resource"] = topic_arn
sns_topic_policy = json.dumps(sns_topic_policy)









