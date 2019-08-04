
## policies included in this document: ##         |does it have to be edited?
# config_role_policy                              | no
# config_role_trust_relationship                  | no
# initial_bucket_policy_cloudtrail                | yes (not used tho)
# initial_bucket_policy_config                    | yes (not used tho)
# sqs_queue_policy                                | yes (central info only)
# cloudtrail_sns_topic_policy                     | yes (new info added)
# config_sns_topic_policy                         | Yes (new info added)
# saml_assume_role_policy                         | yes (new info added)
# vpc_endpoint_policy                             | no
# amazon_ec2_full_access_role_policy              | no
# new_saml_role_policy                            | no (currently set to ec2full access)
# dummy_config_bucket_policy                      | no (for delete only)
# dummy_cloudtrail_bucket_policy                  | no (for delete only)

config_role_policy = {
  "Version": "2012-10-17",
  "Statement": [
    {
      "Action": [
        "appstream:Get*",
        "autoscaling:Describe*",
        "cloudformation:DescribeStacks",
        "cloudformation:DescribeStackEvents",
        "cloudformation:DescribeStackResource",
        "cloudformation:DescribeStackResources",
        "cloudformation:GetTemplate",
        "cloudformation:List*",
        "cloudfront:Get*",
        "cloudfront:List*",
        "cloudtrail:DescribeTrails",
        "cloudtrail:GetTrailStatus",
        "cloudwatch:Describe*",
        "cloudwatch:Get*",
        "cloudwatch:List*",
        "directconnect:Describe*",
        "dynamodb:GetItem",
        "dynamodb:BatchGetItem",
        "dynamodb:Query",
        "dynamodb:Scan",
        "dynamodb:DescribeTable",
        "dynamodb:ListTables",
        "ec2:Describe*",
        "elasticache:Describe*",
        "elasticbeanstalk:Check*",
        "elasticbeanstalk:Describe*",
        "elasticbeanstalk:List*",
        "elasticbeanstalk:RequestEnvironmentInfo",
        "elasticbeanstalk:RetrieveEnvironmentInfo",
        "elasticloadbalancing:Describe*",
        "elastictranscoder:Read*",
        "elastictranscoder:List*",
        "iam:List*",
        "iam:Get*",
        "kinesis:Describe*",
        "kinesis:Get*",
        "kinesis:List*",
        "opsworks:Describe*",
        "opsworks:Get*",
        "route53:Get*",
        "route53:List*",
        "redshift:Describe*",
        "redshift:ViewQueriesInConsole",
        "rds:Describe*",
        "rds:ListTagsForResource",
        "s3:Get*",
        "s3:List*",
        "sdb:GetAttributes",
        "sdb:List*",
        "sdb:Select*",
        "ses:Get*",
        "ses:List*",
        "sns:Get*",
        "sns:List*",
        "sqs:GetQueueAttributes",
        "sqs:ListQueues",
        "sqs:ReceiveMessage",
        "storagegateway:List*",
        "storagegateway:Describe*",
        "trustedadvisor:Describe*"
      ],
      "Effect": "Allow",
      "Resource": "*"
    }
  ]
}

config_role_trust_relationship = {
  "Version": "2012-10-17",
  "Statement": [
    {
      "Sid": "",
      "Effect": "Allow",
      "Principal": {
        "Service": "config.amazonaws.com"
      },
      "Action": "sts:AssumeRole"
    }
  ]
}



initial_bucket_policy_cloudtrail = {
	"Version": "2012-10-17",
	"Statement": [
		{
			"Sid": "AWSCloudTrailAclCheck20131101",
			"Effect": "Allow",
			"Principal": {
				"AWS": [
					"arn:aws:iam::************:root",
					"arn:aws:iam::************:root",
					"arn:aws:iam::************:root",
					"arn:aws:iam::************:root",
					"arn:aws:iam::************:root",
					"arn:aws:iam::************:root",
					"arn:aws:iam::************:root",
					"arn:aws:iam::************:root",
					"arn:aws:iam::************:root"
				]
			},
			"Action": "s3:GetBucketAcl",
			"Resource": 'place holder'		# this is where the cloudtrail bucket arn goes
		},
		{
			"Sid": "AWSCloudTrailWrite20131101",
			"Effect": "Allow",
			"Principal": {
				"AWS": [
					"arn:aws:iam::************:root",
					"arn:aws:iam::************:root",
					"arn:aws:iam::************:root",
					"arn:aws:iam::************:root",
					"arn:aws:iam::************:root",
					"arn:aws:iam::************:root",
					"arn:aws:iam::************:root",
					"arn:aws:iam::************:root",
					"arn:aws:iam::************:root"
				]
			},
			"Action": "s3:PutObject",
			"Resource": [	# this is where the folder in the bucket goes (looks like: "arn:aws:s3:::nltest1/AWSLogs/************/*")
							# new one will be added everytime a new account is created
			],
			"Condition": {
				"StringEquals": {
					"s3:x-amz-acl": "bucket-owner-full-control"
				}
			}
		}
	]
}

initial_bucket_policy_config = {
	"Version": "2012-10-17",
	"Statement": [
		{
			"Sid": "AWSConfigBucketPermissionsCheck",
			"Effect": "Allow",
			"Principal": {
				"Service": "config.amazonaws.com"
			},
			"Action": "s3:GetBucketAcl",
			"Resource": 	'place holder' # this is where the config bucket arn goes (only one)
		},
		{
			"Sid": " AWSConfigBucketDelivery",
			"Effect": "Allow",
			"Principal": {
				"Service": "config.amazonaws.com"
			},
			"Action": "s3:PutObject",
			"Resource": [	# this is where the folder arn goes (new one added each time new account is created)
			],
			"Condition": {
				"StringEquals": {
					"s3:x-amz-acl": "bucket-owner-full-control"
				}
			}
		}
	]
}
sqs_queue_policy = {
    "Version": "2012-10-17",
    "Id": "arn:aws:sqs:us-east-1:************:intern-test-queue/SQSDefaultPolicy",
    "Statement": [
    {
      "Sid": "Sid1436826838613",
      "Effect": "Allow",
      "Principal": {
        "AWS": "*"
      },
      "Action": "SQS:SendMessage",
      "Resource": "arn:aws:sqs:us-east-1:************:intern-test-queue",
      "Condition": {
        "ArnEquals": {
          "aws:SourceArn": [
          ]
        }
      }
    }
    ]
}

cloudtrail_sns_topic_policy = {	# this says that cloudtrail service is allowed to publish into whichever topic arns you put in resource
		"Version": "2012-10-17",
 
		"Statement": [
		{
   
		"Sid": "AWSCloudTrailSNSPolicy20140219",  
		"Effect": "Allow",
		# 'resource' here: its own topic arn
		"Principal": {
   		    	
			"AWS": [
				"arn:aws:iam::************:root",
				"arn:aws:iam::************:root",
				"arn:aws:iam::************:root",
				"arn:aws:iam::************:root",
				"arn:aws:iam::************:root",
				"arn:aws:iam::************:root",
				"arn:aws:iam::************:root",
				"arn:aws:iam::************:root",
				"arn:aws:iam::************:root"
				]  
			},
			"Action": "SNS:Publish",
		}
		]
}

config_sns_topic_policy = {			# this says that config is allowed to publish into the topic arn you put in resource (its own topic arn)
          "Id": "Policy1415489375392",
          "Statement": [
            {
              "Sid": "AWSConfigSNSPolicy20150201",
              "Action": [
                "SNS:Publish"
              ],				# new account info will NEVER go in here, once this is set it never changes
              "Effect": "Allow",
              # 'resource' here: its own topic arn
              "Principal": {
                "AWS": [
                  "arn:aws:iam::************:root",
                  "arn:aws:iam::************:root",
                  "arn:aws:iam::************:root",
                  "arn:aws:iam::************:root"
                ]
              }
            }
          ]
}

saml_assume_role_policy = {
  "Version": "2012-10-17",
  "Statement": [
    {
      "Sid": "",
      "Effect": "Allow",
      "Principal": {
        # "Federated": "arn:aws:iam::************:saml-provider/intern-test-provider"
      },
      "Action": "sts:AssumeRoleWithSAML",
      "Condition": {
        "StringEquals": {
          "SAML:aud": "https://signin.aws.amazon.com/saml"
        }
      }
    }
  ]
}

initial_queue_policy = {
  "Version": "2012-10-17",
  "Id": "arn:aws:sqs:us-east-1:************:intern-test-queue/SQSDefaultPolicy",
  "Statement": [
    {
      "Sid": "Sid1436826838613",
      "Effect": "Allow",
      "Principal": {
        "AWS": "*"
      },
      "Action": "SQS:SendMessage",
      "Resource": "arn:aws:sqs:us-east-1:************:intern-test-queue",
      "Condition": {
        "ArnEquals": {
          "aws:SourceArn": [
            
          ]
        }
      }
    }
  ]
}

vpc_endpoint_policy = {
    "Statement": [
        {
            "Action": "*",
            "Effect": "Allow",
            "Resource": "*",
            "Principal": "*"
        }
    ]
}

amazon_ec2_full_access_role_policy = {
  "Version": "2012-10-17",
  "Statement": [
    {
      "Action": "ec2:*",
      "Effect": "Allow",
      "Resource": "*"
    },
    {
      "Effect": "Allow",
      "Action": "elasticloadbalancing:*",
      "Resource": "*"
    },
    {
      "Effect": "Allow",
      "Action": "cloudwatch:*",
      "Resource": "*"
    },
    {
      "Effect": "Allow",
      "Action": "autoscaling:*",
      "Resource": "*"
    }
  ]
}
new_saml_role_policy = amazon_ec2_full_access_role_policy


dummy_config_bucket_policy = {
  "Version": "2012-10-17",
  "Statement": [
    {
      "Sid": "AWSConfigBucketPermissionsCheck",
      "Effect": "Allow",
      "Principal": {
        "Service": "config.amazonaws.com"
      },
      "Action": "s3:GetBucketAcl",
      "Resource": "arn:aws:s3:::intern-test-config"
    },
    {
      "Sid": " AWSConfigBucketDelivery",
      "Effect": "Allow",
      "Principal": {
        "Service": "config.amazonaws.com"
      },
      "Action": "s3:PutObject",
      "Resource": [
        "arn:aws:s3:::intern-test-config/AWSLogs/111111111111/*",
        "arn:aws:s3:::intern-test-config/AWSLogs/************/*"
      ],
      "Condition": {
        "StringEquals": {
          "s3:x-amz-acl": "bucket-owner-full-control"
        }
      }
    }
  ]
}

dummy_cloudtrail_bucket_policy = {
  "Version": "2012-10-17",
  "Statement": [
    {
      "Sid": "AWSCloudTrailAclCheck20131101",
      "Effect": "Allow",
      "Principal": {
        "AWS": [
          "arn:aws:iam::************:root",
          "arn:aws:iam::************:root",
          "arn:aws:iam::************:root",
          "arn:aws:iam::************:root",
          "arn:aws:iam::************:root",
          "arn:aws:iam::************:root",
          "arn:aws:iam::************:root",
          "arn:aws:iam::************:root",
          "arn:aws:iam::************:root"
        ]
      },
      "Action": "s3:GetBucketAcl",
      "Resource": "arn:aws:s3:::intern-test-cloudtrail"
    },
    {
      "Sid": "AWSCloudTrailWrite20131101",
      "Effect": "Allow",
      "Principal": {
        "AWS": [
          "arn:aws:iam::************:root",
          "arn:aws:iam::************:root",
          "arn:aws:iam::************:root",
          "arn:aws:iam::************:root",
          "arn:aws:iam::************:root",
          "arn:aws:iam::************:root",
          "arn:aws:iam::************:root",
          "arn:aws:iam::************:root",
          "arn:aws:iam::************:root"
        ]
      },
      "Action": "s3:PutObject",
      "Resource": "arn:aws:s3:::intern-test-cloudtrail/AWSLogs/************/*",
      "Condition": {
        "StringEquals": {
          "s3:x-amz-acl": "bucket-owner-full-control"
        }
      }
    }
  ]
}
