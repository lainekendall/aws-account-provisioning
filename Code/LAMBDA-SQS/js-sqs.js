
console.log('Loading function')
    
var exec = require('child_process').exec;
process.env['PATH'] = process.env['PATH'] + ':' + process.env['LAMBDA_TASK_ROOT']

exports.handler = function(event, context) {
    console.log(JSON.stringify(event,null,2));
    process.env['LAMBDA_ACCOUNT_NUMBER'] = event.AccountNumber;

    exec('env/bin/python ./python-sqs.py', function(error, stdout) {
            console.log('Python returned: ' + stdout + '.');
            console.log(error)
            context.succeed(stdout);
        });
};
