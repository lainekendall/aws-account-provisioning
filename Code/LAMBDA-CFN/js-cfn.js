

console.log('Loading function')
    
var exec = require('child_process').exec;
process.env['PATH'] = process.env['PATH'] + ':' + process.env['LAMBDA_TASK_ROOT']

exports.handler = function(event, context) {
    console.log(JSON.stringify(event,null,2));

    event.Records.forEach(function(record) {
    process.env['LAMBDA_SOURCE'] = record.Sns.TopicArn
    process.env['LAMBDA_MESSAGE'] = record.Sns.Message
    process.env['LAMBDA_SUBJECT'] = record.Sns.Subject
        console.log(record.Sns.Message);
        console.log(record.Sns.Subject);
    if(record.Sns.Subject == 'CreateLinkedAccount - Success') {
        console.log('entered into if statement')
        console.log('SNS Record: %j', record.Sns);
        exec('env/bin/python ./python-cfn.py', function(error, stdout) {
            console.log('Python returned: ' + stdout + '.');
            console.log(error)
            context.succeed(stdout);
        });
}
    else { context.succeed(); }
    });
}
