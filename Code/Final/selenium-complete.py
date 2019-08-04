aws_account_full_name = 'eis-aws-account-automation'

company = 'Autodesk'
address = '111 McInnis Parkway'
city = 'San Rafael'
state = 'California'
postal_code = '94903'
phone = '415-507-5000'

credit_card_number = '4342562221502451'
credit_card_name = 'Laine Kendall'
expiration_month = 12
expiration_year = 2017
current_year = datetime.datetime.now().year	# this is to find the credit card expiration year element on the page


def password_generator():
	""" Generates a random password for the new account """
	from random import sample
	symbol = string.punctuation
	lower = string.ascii_lowercase
	upper = string.ascii_uppercase
	numeric = string.digits
	seed = sample(lower, 1) + sample(upper, 1) + sample(numeric, 1) + sample(symbol, 1) +\
	sample(lower + upper + numeric + symbol, 16)
	return ''.join(sample(seed, 20))

password = password_generator()

def selenium_create_account():		# 30 seconds
	global driver
	## SELENIUM: account creation ##
	# open up firefox
	driver = webdriver.Firefox()
	driver.get('http://aws.amazon.com/console/')
## page 1
	while True:
		try:
			try_aws = driver.find_element_by_xpath("//a[@class='button btn-gold btn-block btn-large-cta btn-offset']")
			break
		except selenium.common.exceptions.NoSuchElementException:
			pass
	try_aws.click()

# page 2
	while True:
		try:
			email_element = driver.find_element_by_xpath("//input[@id='ap_email']")
			new_user = driver.find_element_by_xpath("//input[@id='ap_signin_create_radio']")
			sign_in = driver.find_element_by_xpath("//input[@id='signInSubmit-input']")
			break
		except selenium.common.exceptions.NoSuchElementException:
			pass
	email_element.send_keys(project_email_address)
	new_user.click()
	sign_in.click()

# page 3: name, email x2, password x2
	while True:
		try:
			name_element = driver.find_element_by_xpath("//input[@id='ap_customer_name']")
			email_again_element = driver.find_element_by_xpath("//input[@id='ap_email_check']")
			password_element = driver.find_element_by_xpath("//input[@id='ap_password']")
			password_again_element = driver.find_element_by_xpath("//input[@id='ap_password_check']")
			create_account = driver.find_element_by_xpath("//input[@id='continue-input']")
			break
		except selenium.common.exceptions.NoSuchElementException:
			pass
	name_element.send_keys(aws_account_full_name)
	email_again_element.send_keys(project_email_address)
	password_element.send_keys(password)
	password_again_element.send_keys(password)
	create_account.click()

# page 4: name, company, country, address, city, state, postal code, captchka, confirm
	while True:
		try:
			name_element = driver.find_element_by_xpath("//input[@name='fullName']")
			company_element = driver.find_element_by_xpath("//input[@name='company']")
			address_element1 = driver.find_element_by_xpath("//input[@name='addressLine1']")
			address_element2 = driver.find_element_by_xpath("//input[@name='addressLine2']")
			city_element = driver.find_element_by_xpath("//input[@name='city']")
			state_element = driver.find_element_by_xpath("//input[@name='state']")
			postal_code_element = driver.find_element_by_xpath("//input[@name='postalCode']")
			phone_element = driver.find_element_by_xpath("//input[@name='phoneNumber']")
			captcha_element = driver.find_element_by_xpath("//input[@name='guess']")
			agreement = driver.find_element_by_xpath("//input[@name='agreementAccepted']")
			continue_element = driver.find_element_by_xpath("//span[@class='a-button-text']")
			break
		except selenium.common.exceptions.NoSuchElementException:
			pass
	name_element.send_keys(aws_account_full_name)
	company_element.send_keys(company)
	address_element1.send_keys(address)
	city_element.send_keys(city)
	state_element.send_keys(state)
	postal_code_element.send_keys(postal_code)
	phone_element.send_keys(phone)
	captcha_element.send_keys('123456')	# can be any random sequence of characters
	agreement.click()
	continue_element.click()

	# page 5: credit card info
	while True:
		try:
			cc_number = driver.find_element_by_xpath("//input[@name='addCreditCardNumber']")
			cc_name = driver.find_element_by_xpath("//input[@name='accountHolderName']")
			expiration_month_select = driver.find_element_by_xpath("//select[@name='expirationMonth']")
			expiration_month_option = driver.find_element_by_xpath("//select[@name='expirationMonth']/option[@value='" + str(expiration_month-1) + "']")
			expiration_year_select = driver.find_element_by_xpath("//select[@name='expirationYear']")
			expiration_year_option = driver.find_element_by_xpath("//select[@name='expirationYear']/option[@value='" + str(expiration_year-current_year) + "']")
			continue_element = driver.find_element_by_xpath("//span[@class='a-button-text']")
			break
		except selenium.common.exceptions.NoSuchElementException:
			pass
	cc_number.send_keys(credit_card_number)
	cc_name.send_keys(credit_card_name)
	expiration_month_select.click()
	expiration_month_option.click()
	expiration_year_select.click()
	expiration_year_option.click()
	continue_element.click()

# page 1 management console
# driver_signin = webdriver.Firefox()
# driver_signin.get('http://aws.amazon.com/console/')
# aws_signin = driver_signin.find_element_by_xpath("//a[@class='button btn-gold btn-block btn-large-cta btn-offset']")
# aws_signin.click()
### Page 1 SIGN IN TO THE CONSOLE TO CREATE NEW ACCESS KEY ###
def selenium_get_access_keys():
	global new_account_key, new_account_secret_key
	# aws_signin = driver.find_element_by_xpath("//a[@class='aws-nav-button']")
	# aws_signin.click()

# page 1: console home
	while True:
		try:
			iam_service = driver.find_element_by_xpath("//a[@data-service-id='iam']")
			break
		except selenium.common.exceptions.NoSuchElementException:
			pass
	iam_service.click()

# page 2: IAM home
	while True:
		try:
			iam_users = driver.find_element_by_xpath("//li[@class='users']/a[@href='#users']")
			break
		except selenium.common.exceptions.NoSuchElementException:
			pass
	iam_users.click()

# page 3: IAM Users
	while True:
		try:
			create_new_users = driver.find_element_by_xpath("//button[@class='btn btn-primary create_user topMargin3']")
			break
		except selenium.common.exceptions.NoSuchElementException:
			pass
	create_new_users.click()
# page 4: enter in user names
	while True:
		try:
			insert_user = driver.find_element_by_xpath("//div[@class='createUsers']/div[1]/ol/li[1]/input")
			create_user = driver.find_element_by_xpath("//button[@class='btn btn-primary pointer next']")
			break
		except selenium.common.exceptions.NoSuchElementException:
			pass
	insert_user.send_keys(iam_access_key_user)
	create_user.click()
# page 5: credentials
	while True:
		try:
			show_credentials = driver.find_element_by_xpath("//a[@class='showCredentials pointer']")
			show_credentials.click()
			get_access_key = driver.find_element_by_xpath("//div[@class='userAttributes']//div[2]") #fixed path --> alternative? not the best way to ensure that we get the right values
			get_secret_key = driver.find_element_by_xpath("//div[@class='userAttributes']//div[4]")
			new_account_key = str(get_access_key.text)
			new_account_secret_key = str(get_secret_key.text)
			close_element = driver.find_element_by_xpath("//a[@class='pointer btn_close']/strong")
			close_element.click()
			close_again = driver.find_element_by_xpath("//a[@id='closeWindow']/strong")
			break
		except selenium.common.exceptions.NoSuchElementException:
			pass
	close_again.click()

# page 6: all users page
	user_xpath = "//td[@title='" + iam_access_key_user + "']/div"
	while True:
		try:
			user = driver.find_element_by_xpath(user_xpath)
			break
		except selenium.common.exceptions.NoSuchElementException:
			pass
	user.click()
# page 7: new user page
	while True:
		try:
			attach_policy = driver.find_element_by_xpath("//button[@id='attachManagedPolicy']")
			break
		except selenium.common.exceptions.NoSuchElementException:
			pass
	attach_policy.click()
# page 8: policies page
	while True:
		try:
			# search = driver.find_element_by_xpath("//div[@class='header_row']/input[@class='span4 search_input']")
			# search.send_keys('AdministratorAccess')
			# search.send_keys(Keys.RETURN)
			admin_access = driver.find_element_by_xpath("//input[@data-id='arn:aws:iam::aws:policy/AdministratorAccess']")
			admin_access.click()
			attach_policy_submit = driver.find_element_by_xpath("//button[@class='btn btn-primary submit']")
			break
		except (selenium.common.exceptions.NoSuchElementException, selenium.common.exceptions.StaleElementReferenceException):
			pass
	attach_policy_submit.click()
	driver.quit()