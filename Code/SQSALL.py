import boto3, json, time

central_account_key = '************************'
central_account_secret_key = '*************************************'
new_account_key = '************************'
new_account_secret_key = '*********************************************'
central_account_number = '00000000000000000'
new_account_number = '000000000000000000'

# # everything SQS is done in central account in default region
client_sqs = boto3.client('sqs', aws_access_key_id=central_account_key, aws_secret_access_key=central_account_secret_key)
queue_name = 'intern-test-queue'
queue_region = 'us-east-1'
queue_arn = "arn:aws:sqs:" + queue_region + ":" + central_account_number + ":" + queue_name
cloudtrail_sns_topic_name = 'intern-test-cloudtrail-notifications'
config_sns_topic_name = 'intern-test-config-notifications'

region_names_list = ['us-west-1', 'us-east-1', 'us-west-2', 
'eu-west-1', 'eu-central-1', 'ap-southeast-1', 'ap-northeast-1', 
'ap-southeast-2', 'sa-east-1']

get_queue_url = client_sqs.get_queue_url(
    QueueName=queue_name,
    QueueOwnerAWSAccountId=central_account_number)
queue_url = get_queue_url['QueueUrl']

initial_queue_policy = {
    "Version": "2012-10-17",
    "Id": "arn:aws:sqs:us-east-1:0000000000000:intern-test-queue/SQSDefaultPolicy",
    "Statement": [
    {
      "Sid": "Sid1436826838613",
      "Effect": "Allow",
      "Principal": {
        "AWS": "*"
      },
      "Action": "SQS:SendMessage",
      "Resource": "arn:aws:sqs:us-east-1:00000000000000:intern-test-queue",
      "Condition": {
        "ArnEquals": {
          "aws:SourceArn": [
          ]
        }
      }
    }
    ]
    }

initial_queue_policy = json.dumps(initial_queue_policy)

# STEP 0: put the intial policy in place (which basically says nothing)
def put_initial_policy():
    global initial_queue_policy
    client_sqs.set_queue_attributes(
    QueueUrl=queue_url,
    Attributes={
        'Policy': initial_queue_policy
    }
    )


# STEP 1
# policy should NOT be in place when this happens
def subscribe_config():
    for region in region_names_list:
        client_sns = boto3.client('sns', aws_access_key_id=central_account_key, aws_secret_access_key=central_account_secret_key, region_name=region)                        
        config_sns_topic_arn = "arn:aws:sns:" + region + ":" + central_account_number + ":" + config_sns_topic_name
        response = client_sns.subscribe(
        TopicArn= config_sns_topic_arn,
        Protocol='sqs',
        Endpoint=queue_arn
        )
        
# STEP 2: change queue policy to allow cloudtrail sns topics to send messages to queue

def update_policy(service):
    if service == 'cloudtrail':
        sns_account_number = new_account_number
        sns_topic_name = cloudtrail_sns_topic_name
    elif service == 'config':
        sns_account_number = central_account_number
        sns_topic_name = config_sns_topic_name
    get_queue_attributes = client_sqs.get_queue_attributes(
    QueueUrl=queue_url,
    AttributeNames=[
        'Policy',
    ]
    )
    queue_policy = get_queue_attributes['Attributes']['Policy']
    queue_policy = json.loads(queue_policy)                         # convert to regular python dictionary
    for region in region_names_list:                                # add sns topic arns to source arn list
        sns_topic_arn = "arn:aws:sns:" + region + ":" + sns_account_number + ":" + sns_topic_name
        queue_policy["Statement"][0]["Condition"]["ArnEquals"]["aws:SourceArn"] = queue_policy["Statement"][0]["Condition"]["ArnEquals"]["aws:SourceArn"] + [sns_topic_arn]
    queue_policy = json.dumps(queue_policy)                         # convert back to JSON format
    client_sqs.set_queue_attributes(
    QueueUrl=queue_url,
    Attributes={
        'Policy': queue_policy
    }
    )     
  
# STEPS 3-7: 
token_dict = {}
def subscribe_cloudtrail():
    for region in region_names_list:
        print('top of for loop')
        client_sns = boto3.client('sns', aws_access_key_id=new_account_key, aws_secret_access_key=new_account_secret_key, region_name=region)                        
        cloudtrail_sns_topic_arn = "arn:aws:sns:" + region + ":" + new_account_number + ":" + cloudtrail_sns_topic_name
        response = client_sns.subscribe(
        TopicArn= cloudtrail_sns_topic_arn,
        Protocol='sqs',
        Endpoint=queue_arn
        )
        print(region + 'is subscribed')
        while True:         # wait for message to arrive
            try:
                messages = client_sqs.receive_message(
                QueueUrl=queue_url,
                MaxNumberOfMessages=1,
                VisibilityTimeout=30,
                WaitTimeSeconds=0)["Messages"]
                break
            except KeyError:
                print('retry')
        # if not a subscription confirmation message then... try again? (and do not delete message)
        if json.loads(messages[0]["Body"])["Type"] == "SubscriptionConfirmation":       # possibly not necessary
            receipt_handle = messages[0]["ReceiptHandle"]
            print('receipt handle')
            token = str(json.loads(messages[0]["Body"])["Token"])
        else:
            print('non-subscription confirmation message delivered')
        token_dict[region] = token
        response = client_sqs.delete_message(
            QueueUrl=queue_url,
            ReceiptHandle=receipt_handle
        )
        print('message deleted')

#8) confirm subscriptions using dictionary
def confirm():
    for region in region_names_list:
        token = token_dict[region]
        client_sns = boto3.client('sns', aws_access_key_id=new_account_key, aws_secret_access_key=new_account_secret_key, region_name=region)
        cloudtrail_sns_topic_arn = "arn:aws:sns:" + region + ":" + new_account_number + ":" + cloudtrail_sns_topic_name
        client_sns.confirm_subscription(TopicArn=cloudtrail_sns_topic_arn,Token=token,AuthenticateOnUnsubscribe='true')
                

	
        
        
        
        
## code to enter: ##
# put_initial_policy()
# subscribe_config()
# update_policy('cloudtrail')
# subscribe_cloudtrail()
# confirm()
# update_policy('config')  









