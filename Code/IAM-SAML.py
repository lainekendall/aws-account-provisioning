import boto3, json

## code: ##
# central_saml_metadata = get_saml_metadata()
# create_saml_provider_and_role()

#credentials
central_account_key = '************************'
central_account_secret_key = '*************************************'
new_account_key = '************************'
new_account_secret_key = '*********************************************'
central_account_number = '00000000000000000'
new_account_number = '000000000000000000'

client_iam_new = boto3.client('iam', aws_access_key_id=new_account_key, aws_secret_access_key=new_account_secret_key)
client_iam_central = boto3.client('iam', aws_access_key_id=central_account_key, aws_secret_access_key=central_account_secret_key)
central_saml_provider_name = 'adsk-saml'
central_saml_provider_arn = 'arn:aws:iam::' + central_account_number + ':saml-provider/' + central_saml_provider_name

new_saml_provider_name = 'intern-test-saml-provider'
new_saml_role_name = 'intern-test-saml-role'
new_saml_role_policy_name = 'intern-test-saml-role-policy'
new_saml_provider_arn = 'arn:aws:iam::' + new_account_number + ':saml-provider/' + new_saml_provider_name



role = client_iam_new.get_role(
    RoleName='Training-NonPRD-Account-Admins'
)

a = client_iam_new.list_attached_role_policies(
    RoleName='Training-NonPRD-Account-Admins',
    # PathPrefix='string',
    # Marker='string',
    # MaxItems=123
)

role_policy = client_iam_new.get_role_policy(
    RoleName='Training-NonPRD-Account-Admins',
    PolicyName='Training-NonPRD-Account-Admins'
)


#grab metadata from the central account
def get_saml_metadata():
    central_metadata = client_iam_central.get_saml_provider(
        SAMLProviderArn=central_saml_provider_arn
    )
    return central_metadata['SAMLMetadataDocument']


def create_saml_provider_and_role():
    client_iam_new.create_saml_provider(
        SAMLMetadataDocument=central_saml_metadata,
        Name=new_saml_provider_name
    )

    client_iam_new.create_role(# Path='string',
      RoleName=new_saml_role_name,
      AssumeRolePolicyDocument=json.dumps(saml_assume_role_policy)
    )
    client_iam_new.put_role_policy(
        RoleName=new_saml_role_name,
        PolicyName=new_saml_role_policy_name,
        PolicyDocument=json.dumps(new_saml_role_policy)
    )

def delete_provider_and_role():
    client_iam_new.delete_role(
        RoleName=new_saml_role_name
    )
    client_iam_new.delete_saml_provider(
        SAMLProviderArn=new_saml_provider_arn
    )

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

saml_assume_role_policy["Statement"][0]["Principal"]["Federated"] = 'arn:aws:iam::' + new_account_number + ':saml-provider/' + new_saml_provider_name

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

