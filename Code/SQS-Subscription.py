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

region_names_list = ['us-west-1']#, 'us-east-1', 'us-west-2', 
# 'eu-west-1', 'eu-central-1', 'ap-southeast-1', 'ap-northeast-1', 
# 'ap-southeast-2', 'sa-east-1']

# #retrieve queue url
get_queue_url = client_sqs.get_queue_url(
    QueueName=queue_name,
    QueueOwnerAWSAccountId=central_account_number)
queue_url = get_queue_url['QueueUrl']


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


# from new account
def subscribe_and_confirm_cloudtrail():
    for region in region_names_list:
        client_sns = boto3.client('sns', aws_access_key_id=new_account_key, aws_secret_access_key=new_account_secret_key, region_name=region)                        
        cloudtrail_sns_topic_arn = "arn:aws:sns:" + region + ":" + new_account_number + ":" + cloudtrail_sns_topic_name
        response = client_sns.subscribe(
        TopicArn= cloudtrail_sns_topic_arn,
        Protocol='sqs',
        Endpoint=queue_arn
        )
        while True:
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
            client_sns.confirm_subscription(
                TopicArn=sns_topic_arn,
                Token=token,
                AuthenticateOnUnsubscribe='true')
        # return receipt_handle

# def delete():
#     global receipt_handle
        response = client_sqs.delete_message(
            QueueUrl=queue_url,
            ReceiptHandle=receipt_handle
        )
        print('message deleted')

## code to run: ##
# subscribe()
# receipt_handle = confirm()
# delete


    

    
