
def cloudtrail():
	for region in region_names_list:
		client_ct = boto3.client('cloudtrail', aws_access_key_id=new_account_key, aws_secret_access_key=new_account_secret_key, region_name=region)
		client_ct.create_trail(Name=cloudtrail_name,
	    S3BucketName=cloudtrail_bucket_name,		
	    # S3KeyPrefix=s3_prefix,				# not sure about this yet
	    SnsTopicName=cloudtrail_sns_topic_name,
	    IncludeGlobalServiceEvents=cloudtrail_global_dict[region],				
		)
		client_ct.start_logging(
	    Name=cloudtrail_name			
		)
		print('cloudtrail completed in ' + region)

		
def config():
	for region in region_names_list:
		while True:
			try:
				client_config = boto3.client('config', aws_access_key_id=new_account_key, aws_secret_access_key=new_account_secret_key, region_name=region) 
				config_topic_arn = 'arn:aws:sns:' + region + ':' + central_account_number + ':' + config_sns_topic_name
				client_config.put_configuration_recorder(
				ConfigurationRecorder={
				'name': config_recorder_name,
				'roleARN': config_role_arn
				}
				)
				client_config.put_delivery_channel(
				DeliveryChannel={
				'name': config_delivery_channel_name,
				's3BucketName': config_bucket_name,
				#'s3KeyPrefix': 'laine-test',                                                
				'snsTopicARN': config_topic_arn                            
				}
				)
				client_config.start_configuration_recorder(
				ConfigurationRecorderName=config_recorder_name
				)
				break
			except botocore.exceptions.ClientError:
				print('role for config not created yet... try again')
		print('config configured in ' + region)