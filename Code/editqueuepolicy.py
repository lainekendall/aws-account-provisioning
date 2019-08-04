import boto3
queue_policy = {
    "Version": "2012-10-17",
    "Id": "arn:aws:sqs:us-east-1:000000000000:intern-test-queue/SQSDefaultPolicy",
      "Statement": [
    {
      "Sid": "Sid1436826838613",
      "Effect": "Allow",
      "Principal": {
        "AWS": "*"
      },
      "Action": "SQS:SendMessage",
      "Resource": "arn:aws:sqs:us-east-1:000000000000:intern-test-queue",
      "Condition": {
        "ArnEquals": {
          "aws:SourceArn": [
            
          ]
        }
      }
    }
  ]
}
central_account_key = '************************'
central_account_secret_key = '*************************************'
new_account_key = '************************'
new_account_secret_key = '*********************************************'
central_account_number = '00000000000000000'
new_account_number = '000000000000000000'

# everything SQS is done in central account in default region
client_sqs = boto3.client('sqs', aws_access_key_id=central_account_key, aws_secret_access_key=central_account_secret_key)
queue_name = 'intern-test-queue'
queue_region = 'us-east-1'
queue_arn = "arn:aws:sqs:" + queue_region + ":" + central_account_number + ":" + queue_name
cloudtrail_sns_topic_name = 'intern-test-cloudtrail-notifications'

region_names_list = ['us-east-1', 'us-west-1', 'us-west-2', 
'eu-west-1', 'eu-central-1', 'ap-southeast-1', 'ap-northeast-1', 
'ap-southeast-2', 'sa-east-1']



for region in region_names_list:
    cloudtrail_sns_topic_arn = "arn:aws:sns:" + region + ":" + new_account_number + ":" + cloudtrail_sns_topic_name
    queue_policy["Statement"][0]["Condition"]["ArnEquals"]["aws:SourceArn"] += [cloudtrail_sns_topic_arn]  
















