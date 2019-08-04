import boto3

central_account_key = '************************'
central_account_secret_key = '*************************************'
central_account_number = '00000000000000000'

# # everything SQS is done in central account in default region
client_sqs = boto3.client('sqs', aws_access_key_id=central_account_key, aws_secret_access_key=central_account_secret_key, region_name='us-east-1')
queue_name = 'intern-test-queue'
queue_arn = "arn:aws:sqs:" + queue_region + ":" + central_account_number + ":" + queue_name

region_names_list = ['us-west-1', 'us-east-1', 'us-west-2', 
'eu-west-1', 'eu-central-1', 'ap-southeast-1', 'ap-northeast-1', 
'ap-southeast-2', 'sa-east-1']

get_queue_url = client_sqs.get_queue_url(
    QueueName=queue_name,
    QueueOwnerAWSAccountId=central_account_number)
queue_url = get_queue_url['QueueUrl']

client_sqs.send_message(
    QueueUrl=queue_url,
    MessageBody='test message from lambda',
    DelaySeconds=0)







