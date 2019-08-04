
def config_parallelprocess(region):
	""" Configures config service in all regions """
	print('config_parallelprocess start in ' + region)
	# while True:
	# 	try:
	# 		client_config = boto3.client('config', aws_access_key_id=new_account_key, aws_secret_access_key=new_account_secret_key, region_name=region) 
	# 		client_config.describe_delivery_channels()
	# 		break
	# 	except botocore.exceptions.ClientError:
	# 		print('config session failure')
	# 		pass
	client_config = session_new.client('config', region_name=region)
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
	    'snsTopicARN':  config_topic_arn                            
	    }
	)
	client_config.start_configuration_recorder(
	    ConfigurationRecorderName=config_recorder_name
	)
	print('config configured in ' + region)

def multiprocess_map(func, lst): #pass region_names_list into the list
	print('multi process started with ' + str(func) + ' : ' + str(lst))
	pool = multiprocessing.Pool()
	print('multi process finished')
	return pool.map(func, lst)

def cloudtrail_and_config(): #took 9 - 14 secs to complete
	print(' begin cloudtrail_and_config')
	procs = []
	#time_it(procs.append,Process(target=multiprocess_map, args=(sns_create_topic_cloudtrail_parallelprocess,region_names_list)))
	procs.append(Process(target=multiprocess_map, args=(cloudtrail_parallelprocess, region_names_list)))
	procs.append(Process(target=multiprocess_map, args=(config_parallelprocess, region_names_list)))
	print('after procs, before map')
	map(lambda x: x.start(), procs)
	print('after start map, before join map')
	map(lambda x: x.join(), procs)
	print('region_names_list=' + str(region_names_list))
	print('end cloudtrail_and_config')

def cloudtrail_parallelprocess(region):
	print('cloudtrail_parallelprocess start in ' + region)
	""" Turns on cloudtrail service in all regions referencing SNS topic in the new account as well as the S3 bucket in the central account """
	# while True:
	# 	try:
	# 		client_ct = boto3.client('cloudtrail', aws_access_key_id=new_account_key, aws_secret_access_key=new_account_secret_key, region_name=region)
	# 		client_ct.describe_trails()
	# 		break
	# 	except botocore.exceptions.ClientError:
	# 		print('ct session failure')
	# 		pass
	client_ct = session_new.client('cloudtrail', region_name=region)
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
