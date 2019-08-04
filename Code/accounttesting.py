import boto3, json, string
client_s3_central = boto3.client('s3', aws_access_key_id='*******************',
                  aws_secret_access_key='*******************************************')


client_s3_new = boto3.client('s3', aws_access_key_id='*********************',
                  aws_secret_access_key='**********************************************')


# central account
central = client_s3_central.list_buckets()

# new account
new = client_s3_new.list_buckets()


