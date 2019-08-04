from selenium import webdriver
from selenium.webdriver.common.keys import Keys
import boto3, string, random, time

email = 'adsk-projectname@autodesk.com' #active directory integration
iam_access_key_user = 'intern-testaws'

central_account_key = '************************'
central_account_secret_key = '*************************************'
new_account_key = '************************'
new_account_secret_key = '*********************************************'
central_account_number = '00000000000000000'
new_account_number = '000000000000000000'

transaction_id = 'R10000345'        # change this (should be a function or a variable, not a pre-assigned string)
service_now_table_name = 'intern-test-SNtable'
transaction_id_column_name = 'Transaction ID'
full_name_column_name = 'Creator'
email_column_name = 'Email Address'
password_column_name = 'Password'

account_automation_table_name = 'intern-test-account-automation-table'      # stack parameters and events and their times
credentials_table_name = 'intern-test-credentials-table'

def password_generator():
    from random import sample
  symbol = string.punctuation
  lower = string.ascii_lowercase
  upper = string.ascii_uppercase
  numeric = string.digits
  seed = sample(lower, 1) + sample(upper, 1) + sample(numeric, 1) + sample(symbol, 1) +\
  sample(lower + upper + numeric + symbol, 16)
  return ''.join(sample(seed, 20))


client_ddb = boto3.client('dynamodb', aws_access_key_id=central_account_key, aws_secret_access_key=central_account_secret_key)

## PASSWORD ##
# generate password:
password = password_generator()

# put password in credentials DynamoDB table / secret server
def save_password():
  client_ddb.put_item(
    TableName=credentials_table_name,
    Item={
        transaction_id_column_name: {
            'S': transaction_id,
          },
        password_column_name: {
            'S': password
          }
        }
      )

## SELENIUM ##
# open up firefox
driver = webdriver.Firefox()

## open up firefox page to aws
driver.get('http://aws.amazon.com/console/')

## page 1
try_aws = driver.find_element_by_xpath("//a[@class='button btn-gold btn-block btn-large-cta btn-offset']")
try_aws.click()

## page 2
email_element = driver.find_element_by_xpath("//input[@id='ap_email']")
email_element.send_keys(email_address)

new_user = driver.find_element_by_xpath("//input[@id='ap_signin_create_radio']")
new_user.click()

sign_in = driver.find_element_by_xpath("//input[@id='signInSubmit-input']")
sign_in.click()

# page 3
# find the elements
name_element = driver.find_element_by_xpath("//input[@id='ap_customer_name']")
email_again_element = driver.find_element_by_xpath("//input[@id='ap_email_check']")
password_element = driver.find_element_by_xpath("//input[@id='ap_password']")
password_again_element = driver.find_element_by_xpath("//input[@id='ap_password_check']")
create_account = driver.find_element_by_xpath("//input[@id='continue-input']")

# enter in the values
name_element.send_keys(full_name)
email_again_element.send_keys(email)
password_element.send_keys(password)
password_again_element.send_keys(password)
create_account.click()

# page 4
company = 'Autodesk'
address = '111 McInnis Parkway'
city = 'San Rafael'
state = 'California'
postal_code = '94903'
phone = '415-507-5000'
security_check = 'RUCHUX'     # for testing purposes only

## fill in name, company name, country, address, city, state, postal code, phone number, security check, confirm the aws customer agreement and press next
name_element = driver_signup.find_element_by_xpath("//input[@name='fullName']")
name_element.send_keys(full_name)

company_element = driver_signup.find_element_by_xpath("//input[@name='company']")
company_element.send_keys(company)

country_element = driver_signup.find_element_by_xpath("//select[@class='control-select ng-pristine ng-valid']//option[232]")

address_element1 = driver_signup.find_element_by_xpath("//input[@name='addressLine1']")
address_element2 = driver_signup.find_element_by_xpath("//input[@name='addressLine2']")
address_element1.send_keys(address)
address_element2.send_keys("")

city_element = driver_signup.find_element_by_xpath("//input[@name='city']")
city_element.send_keys(city)

state_element = driver_signup.find_element_by_xpath("//input[@name='state']")
state_element.send_keys(state)

postal_code_element = driver_signup.find_element_by_xpath("//input[@name='postalCode']")
postal_code_element.send_keys(postal_code)

phone_element = driver_signup.find_element_by_xpath("//input[@name='phoneNumber']")
phone_element.send_keys(phone)

security_check_element = driver_signup.find_element_by_xpath("guess")
security_check_element.send_keys(security_check)

agreement = driver_signup.find_element_by_xpath("//input[@name='agreementAccepted']")
agreement.click()

continue_element = driver_signup.find_element_by_xpath("//span[@class='a-button-text']")
continue_element.click()

## credit card info ##

## identity verification info ##

# # page 5 (support plan) DO NOT test on personal account:
# enterprise_element = driver_signup.find_element_by_xpath("//input[@value='AWSSupportEnterprise']")
# enterprise_element.click()

# continue_element = driver_signup.find_element_by_xpath("//input[@value='AWSSupportEnterprise']")
# continue_element.click()



# page 1 management console
# driver_signin = webdriver.Firefox()
# driver_signin.get('http://aws.amazon.com/console/')
# aws_signin = driver_signin.find_element_by_xpath("//a[@class='button btn-gold btn-block btn-large-cta btn-offset']")
# aws_signin.click()


### Page 1 SIGN IN TO THE CONSOLE TO CREATE NEW ACCESS KEY ###


aws_signin = driver.find_element_by_xpath("//a[@class="aws-nav-button"]")
aws_signin.click()

iam_service = driver.find_element_by_xpath("//a[@data-service-id='iam']")
iam_service.click()

iam_users = driver.find_element_by_xpath("//li[@class='users']//a[@href='#users']")
iam_users.click()

create_new_users = driver.find_element_by_xpath("//button[@class='btn btn-primary create_user topMargin3']")
create_new_users.click()

insert_user = driver.find_element_by_xpath("//div[@class='createUsers']//li[1]//input")
insert_user.send_keys(iam_access_key_user)

generate_key = driver.find_element_by_xpath("//button[@class='btn btn-primary pointer next']")
generate_key.click()

show_credentials = driver.find_element_by_xpath("//a[@class='showCredentials pointer']")
show_credentials.click()

get_access_key = driver.find_element_by_xpath("//div[@class='userAttributes']//div[2]") #fixed path --> alternative? not the best way to ensure that we get the right values
new_account_key = get_access_key.text
get_secret_key = driver.find_element_by_xpath("//div[@class='userAttributes']//div[4]")
new_account_secret_key = get_secret_key.text

#quit the browser








