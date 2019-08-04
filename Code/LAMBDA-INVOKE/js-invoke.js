

console.log('Loading function: Begin record')
    
var exec = require('child_process').exec;
process.env['PATH'] = process.env['PATH'] + ':' + process.env['LAMBDA_TASK_ROOT']

exports.handler = function(event, context) {
    console.log(JSON.stringify(event,null,2));

    event.Records.forEach(function(record) {
	process.env['LAMBDA_EVENT'] = record.eventName
    if(record.eventName == 'INSERT') {  
    process.env['LAMBDA_TRANS_ID'] = record.dynamodb.NewImage 
    process.env['LAMBDA_AZ'] = record.dynamodb.NewImage.AvailabilityZones.S  
    process.env['LAMBDA_LONG_NAME'] = record.dynamodb.NewImage.LongProjectName.S  
    process.env['LAMBDA_SHORT_NAME'] = record.dynamodb.NewImage.ShortProjectName.S  
    process.env['LAMBDA_ENVIRONMENT'] = record.dynamodb.NewImage.Environment.S  
    process.env['LAMBDA_COST_CENTER'] = record.dynamodb.NewImage.CostCenter.S  
    process.env['LAMBDA_USERS'] = record.dynamodb.NewImage.Users.S  
    process.env['LAMBDA_DEFAULT_REGION'] = record.dynamodb.NewImage.DefaultRegions.S      
    process.env['LAMBDA_CREATOR'] = record.dynamodb.NewImage.Creator.S  
    process.env['LAMBDA_CREATOR_EMAIL'] = record.dynamodb.NewImage.CreatorEmailAddress.S  
    process.env['LAMBDA_CREATOR_DEPT'] = record.dynamodb.NewImage.CreatorDepartment.S  
    process.env['LAMBDA_CREATOR_MANAGER'] = record.dynamodb.NewImage.CreatorManager.S
    process.env['LAMBDA_PROJ_EMAIL'] = record.dynamodb.NewImage.EmailAddress.S
        console.log(record.eventID);
        console.log(record.eventName);
        console.log('DynamoDB Record: %j', record.dynamodb);
        exec('env/bin/python ./python-invoke.py', function(error, stdout) {
            console.log('Python returned: ' + stdout + '.');
            console.log(error);
            context.succeed(stdout); // leave blank if python doesnt print // use done in real script, but add in error handling
        });         // context.done = repeat, context.succeeed = one time only
} 
    else { context.succeed(); }
    });
}
