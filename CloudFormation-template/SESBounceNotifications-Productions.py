#!/usr/bin/python3.6
import urllib3
import json
import boto3


http = urllib3.PoolManager()
#Create a SSM Client to access parameter store
ssm = boto3.client('ssm')
def lambda_handler(event, context):
    
    
    data = event['Records'][0]['Sns']['Message']
    # load json format in dictonary format
    dic_data = json.loads(data)
    print("DATA TYPE:", type(dic_data))
    print("SNS Message:" + '\n')
    print(dic_data)


    # Parse Meaning full data from the dictonary of SNS message
    notification_type = dic_data['notificationType']
    bounce_type = dic_data['bounce']['bounceType']
    subject = dic_data['mail']['commonHeaders']['subject']
    
    compiled_msg = str("*Bounce Email Event Occurred.*" + '\n\n' + "*Details!*" + '\n' + "*Notification Type:*  " + notification_type + '\n' +
    "*Bounce Type:*  " + bounce_type + '\n' + "*Email Subject:*  " + subject + '\n\n' + "*Bounced Recipients:*" + '\n')
    
    
    bouncedRecipients = dic_data['bounce']['bouncedRecipients']
    
    # Iterate over list of dictonaries of Bounced Emails with error code
    for i in bouncedRecipients:
        for key, value in i.items():
            print("{} {}".format(key.upper(), value))
            compiled_msg = compiled_msg + '\t' + "*{}:* {}".format(key.upper(), value) + '\n'
        compiled_msg = compiled_msg + '\n'
        
        
    source = dic_data['mail']['source']
    source_arn = dic_data['mail']['sourceArn']
    source_ip = dic_data['mail']['sourceIp']
    destination = dic_data['mail']['destination']
    
    
    compiled_msg = compiled_msg + "*Source Email:*  " + source + '\n' + "*Source ARN:*  " + source_arn + '\n' + "*Source IP:*  " +  source_ip + '\n'
  
    msg = {
         "channel": "#YOURCHANNELHERE",
         "username": "LambdaNotifier",
         "text": compiled_msg,
         "icon_emoji": ""
    }
    
    
    encoded_msg = json.dumps(msg).encode('utf-8')
    
    #retrieve webhook url from parameter store
    webhook_url = ssm.get_parameter(Name='webhookbouncesemail', WithDecryption=True)
    
    
    resp = http.request('POST', webhook_url['Parameter']['Value'], body=encoded_msg)
    
    
    print({
        "message": event['Records'][0]['Sns']['Message'], 
        "status_code": resp.status, 
        "response": resp.data
    })
