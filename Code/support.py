import boto3

client = boto3.client('support')

response = client.create_case(
    subject='Change Support Plan to Enterprise Support',
    serviceCode='billing',
    severityCode='low',
    categoryCode='other-billing-questions',
    communicationBody='This account needs to have enterprise support',
    ccEmailAddresses=[
        'laine.kendall@autodesk.com',																	# change this (who should be emailed?)
    ],
    language='en',
    issueType='customer-service',
)
