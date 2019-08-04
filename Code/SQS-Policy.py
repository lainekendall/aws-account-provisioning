import boto3, json

central_account_key = 'AKIAIZPY3S3PSWSYC5EA'
central_account_secret_key = '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'
new_account_key = 'AKIAI6IOKMMJFAYYJ4CQ'
new_account_secret_key = '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'
central_account_number = '00000000000'
new_account_number = '052362053110'

# # everything SQS is done in central account in default region
client_sqs = boto3.client('sqs', aws_access_key_id=central_account_key, aws_secret_access_key=central_account_secret_key)
queue_name = 'intern-test-queue'
queue_region = 'us-east-1'
queue_arn = "arn:aws:sqs:" + queue_region + ":" + central_account_number + ":" + queue_name
cloudtrail_sns_topic_name = 'intern-test-cloudtrail-notifications'
config_sns_topic_name = 'intern-test-config-notifications'

region_names_list = ['us-east-1', 'us-west-1', 'us-west-2', 
'eu-west-1', 'eu-central-1', 'ap-southeast-1', 'ap-northeast-1', 
'ap-southeast-2', 'sa-east-1']


  
# if no queue yet, do this:
def create_queue(): 
    global initial_queue_policy
    client_sqs.create_queue(
    QueueName=queue_name,
    Attributes={
        'DelaySeconds': '0 seconds',
        'MaximumMessageSize' : '262144',
        'MessageRetentionPeriod': '345600',
        'Policy': initial_queue_policy,
        'ReceiveMessageWaitTimeSeconds': '0',
        'VisibilityTimeout': '30'
    }
    )

# change policy
def add_users():
    get_queue_attributes = client_sqs.get_queue_attributes(
    QueueUrl=queue_url,
    AttributeNames=[
        'Policy',
    ]
    )
    initial_queue_policy_json = get_queue_attributes['Attributes']['Policy']
    cloudtrail_queue_policy = json.loads(initial_queue_policy_json) 
    for region in region_names_list:
        cloudtrail_sns_topic_arn = "arn:aws:sns:" + region + ":" + new_account_number + ":" + cloudtrail_sns_topic_name
        cloudtrail_queue_policy["Statement"][0]["Condition"]["ArnEquals"]["aws:SourceArn"] = cloudtrail_queue_policy["Statement"][0]["Condition"]["ArnEquals"]["aws:SourceArn"] + [cloudtrail_sns_topic_arn]
    return cloudtrail_queue_policy

#update policy
def update_policy():
    global cloudtrail_queue_policy
    cloudtrail_queue_policy_json = json.dumps(cloudtrail_queue_policy)
    client_sqs.set_queue_attributes(
    QueueUrl=queue_url,
    Attributes={
        'Policy': cloudtrail_queue_policy_json
    }
    )   

## code to type in terminal:##
# create_queue() OR put_initial_policy() if queue already exists
# queue_policy = add_users()
# update_policy()

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




