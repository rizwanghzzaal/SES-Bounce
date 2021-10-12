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
    subject = dic_data['mail']['commonHeaders']['subject']
    user_agent = dic_data['complaint']['userAgent']
    complaint_feedback_type = dic_data['complaint']['complaintFeedbackType']
    
    
    compiled_msg = str("*Complaint Email Event Occurred.*" + '\n\n' + "*Details!*" + '\n' + "*Notification Type:*  " + notification_type + '\n' +
     "*Email Subject:*  " + subject + '\n' + "*User Agent:*  " + user_agent + '\n'  "*Complaint FeedBack Type:*  " + complaint_feedback_type +'\n\n' + "*Complained Recipients:*" + '\n')
    
    
    complainedRecipients = dic_data['complaint']['complainedRecipients']
    
    # Iterate over list of dictonaries of Complained Emails
    for i in complainedRecipients:
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
    webhook_url = ssm.get_parameter(Name='webhookcomplaintemail', WithDecryption=True)
    
    
    resp = http.request('POST', webhook_url['Parameter']['Value'], body=encoded_msg)
    
    
    print({
        "message": event['Records'][0]['Sns']['Message'], 
        "status_code": resp.status, 
        "response": resp.data
    })
