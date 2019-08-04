package example;

import com.amazonaws.services.lambda.runtime.Context;
import com.amazonaws.services.lambda.runtime.LambdaLogger;
import com.amazonaws.auth.BasicAWSCredentials;


import com.amazonaws.services.accounts.AWSAccountsService;
import com.amazonaws.services.accounts.AWSAccountsServiceAsync;
import com.amazonaws.services.accounts.AWSAccountsServiceAsyncClient;
import com.amazonaws.services.accounts.AWSAccountsServiceAsyncClient;
import com.amazonaws.services.accounts.AWSAccountsServiceClient;
import com.amazonaws.services.accounts.AmazonAccountsService;
import com.amazonaws.services.accounts.AmazonAccountsServiceAsync;
import com.amazonaws.services.accounts.AmazonAccountsServiceAsyncClient;
import com.amazonaws.services.accounts.AmazonAccountsServiceAsyncClient;
import com.amazonaws.services.accounts.AmazonAccountsServiceClient;
import com.amazonaws.services.accounts.model.Address;
import com.amazonaws.services.accounts.model.MailingAddress;
import com.amazonaws.services.accounts.model.CreateLinkedAccountRequest;
import com.amazonaws.services.accounts.model.CreateLinkedAccountResult;



public class Hello {
	public static class RequestClass {
        String projectEmailAddress;

        public String getProjectEmailAddress() {
            return projectEmailAddress;
        }

        public void setProjectEmailAddress(String projectEmailAddress) {
            this.projectEmailAddress = projectEmailAddress;
        }

        public RequestClass(String projectEmailAddress) {
            this.projectEmailAddress = projectEmailAddress;
        }

        public RequestClass() {
        }
    }

    public static class ResponseClass {
        String email;

        public String getEmail() {
            return email;
        }

        public void setEmail(String email) {
            this.email = email;
        }

        public ResponseClass(String email) {
            this.email = email;
        }

        public ResponseClass() {
        }

    }
    public static ResponseClass myHandler(RequestClass request, Context context){
    	LambdaLogger logger = context.getLogger();
        // Write log to CloudWatch using LambdaLogger.
        logger.log("This is a log from our create link lambda function: ");
        
        // System.out also generates log in CloudWatch but 
        System.out.println(request);
        
        System.err.println(request.projectEmailAddress);
		//All undeclared parameters are String objects that are 
		//initialized before this example
		//First we instantiate an object to hold our IAM user credentials
		// real payer account:
		BasicAWSCredentials creds = new BasicAWSCredentials("AKIAIDIEEDJWZOQJ6O6Q", "xVso+/o68Rcs+YJlTBV6jKDrlHM8ah2+B6TFcyNL");
		// test central account:
		// BasicAWSCredentials creds = new BasicAWSCredentials("AKIAJEMUZ33AYPHIJ37A", "qGKlewfsi9SudQyPVOCDxygilWNy46Uwd3/d6Moq");
		// fake credentials
		// BasicAWSCredentials creds = new BasicAWSCredentials("AKIAJEMUZ33AYPHIJ37Q", "qGKlewfsi9SudQyPVOCDxygilWNy46Uwd3/d6Moq");

		//Now we create our handle to the service and give it the credentials
		//we want to use
		AmazonAccountsServiceClient aas = new AmazonAccountsServiceClient(creds);
		aas.setServiceNameIntern("AWSAccountsService");
		//Now we need to create the parameters we are going to call the API with

		//We instantiate a MailingAddress object and set the data in it
		MailingAddress mailingAddress = new MailingAddress();
		//You can also call .setAddressLine2 and .setAddressLine3 if you need to
		mailingAddress.setAddressLine1("111 McInnis Parkway");
		mailingAddress.setCity("San Rafael");
		mailingAddress.setStateOrRegion("CA");
		mailingAddress.setCountryCode("US");
		//Remember that the postal code must be the full code (5+4)
		mailingAddress.setPostalCode("94903-2700");
			
		//Now we instantiate our contact address which includes the
		//mailing address, our name, and our contact phone number
		Address address = new Address();
		address.setFirstName("eis-aws-account-automation");
		address.setLastName(""); // ??
		address.setMailingAddress(mailingAddress);
		address.setPhoneNumber("415-507-5000");
			
		//Now let"s create the request we are going to pass to the service
		CreateLinkedAccountRequest ClaRequest = new CreateLinkedAccountRequest();
		//And populate the data in that request
		ClaRequest.setAddress(address);
		ClaRequest.setEmail(request.projectEmailAddress); // get from DDB
		//Remember that the service"s account needs permission to post to this topic
		ClaRequest.setSnsArn("arn:aws:sns:us-east-1:359896532639:linkedaccountcreation-notifications");
		//ClaRequest.setSnsArn("arn:aws:sns:us-east-1:964355697993:intern-create-linked");
		// ClaRequest.setRoleName("ROLE_NAME");

		//And finally let"s make the call to the service.  This will throw
		//an exception if the API is not successful, otherwise you can
		//assume success
		aas.createLinkedAccount(ClaRequest);

		return new ResponseClass(request.projectEmailAddress);

	}
}





