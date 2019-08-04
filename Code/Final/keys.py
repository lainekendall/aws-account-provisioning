import time, datetime, json, string, random, os, sys # python pre-installed packages
import boto3, botocore # installed packages
import multiprocessing
from multiprocessing import Process, Manager

central_account_number = '964355697993'
central_account_key = 'AKIAJEMUZ33AYPHIJ37A'
central_account_secret_key = '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'
central_default_region = 'us-east-1'

new_role_name = 'intern-cross-create-linked'
new_account_number = '052362053110'
client_sts = boto3.client('sts', aws_access_key_id=central_account_key, aws_secret_access_key=central_account_secret_key, region_name=central_default_region)

def client_token_generator():
	""" Generates a random token for the VPC S3 endpoint """
	from random import sample
	lower = string.ascii_lowercase
	upper = string.ascii_uppercase
	seed = sample(lower, 6) + sample(upper, 6)
	return ''.join(sample(seed, 9))



new_role_arn = 'arn:aws:iam::' + new_account_number + ':role/' + new_role_name
assume_role_response = client_sts.assume_role(
    RoleArn=new_role_arn,
    RoleSessionName='role-session-' + client_token_generator(),
	DurationSeconds=3600)

new_account_key = assume_role_response['Credentials']['AccessKeyId']
new_account_secret_key = assume_role_response['Credentials']['SecretAccessKey']
new_session_token = assume_role_response['Credentials']['SessionToken']

session_new = boto3.session.Session(aws_access_key_id=new_account_key, aws_secret_access_key=new_account_secret_key, aws_session_token=new_session_token)
client_iam_new = session_new.client('iam', region_name='us-east-1')

new_user_name = 'intern-access-keys-role'
client_iam_new.create_user(
    # Path='string',
    UserName=new_user_name
)
client_iam_new.attach_user_policy(
    UserName=new_user_name,
    PolicyArn='arn:aws:iam::aws:policy/AdministratorAccess'
)
access_key = client_iam_new.create_access_key(
    UserName=new_user_name
)
new_account_key = access_key['AccessKey']['AccessKeyId']
new_account_secret_key = access_key['AccessKey']['SecretAccessKey']








