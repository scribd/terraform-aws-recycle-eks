# Puts the instance in the standby mode
# there is immense possibility here we can read from cludwatch warnings, or based on some other metrics to identify the 
# instance automatically
# for now I am taking it as a input

import json
import boto3
import time

ec2_client = boto3.client('ec2')
asg_client = boto3.client('autoscaling')

def lambda_handler(event, context):
    id = 'i-04ce2004fa0d18454'
    print("Instance id is " + str(id))

    # Capture all the info about the instance so we can extract the ASG name later
    response = ec2_client.describe_instances(
        Filters=[
            {
                'Name': 'instance-id',
                'Values': [str(id)]
            },
        ],
    )

    # Get the ASG name from the response JSON
    #autoscaling_name = response['Reservations'][0]['Instances'][0]['Tags'][1]['Value']
    tags = response['Reservations'][0]['Instances'][0]['Tags']
    autoscaling_name = next(t["Value"] for t in tags if t["Key"] == "aws:autoscaling:groupName")
    print("Autoscaling name is - " + str(autoscaling_name))

    #Put the instance in standby
    response = asg_client.enter_standby(
        InstanceIds=[
            str(id),
        ],
        AutoScalingGroupName=str(autoscaling_name),
        ShouldDecrementDesiredCapacity=True
    )

    response = asg_client.describe_auto_scaling_instances(
        InstanceIds=[
            str(id),
        ]
    )
    while response['AutoScalingInstances'][0]['LifecycleState']!='Standby':
        time.sleep(10)
        response = asg_client.describe_auto_scaling_instances(
        InstanceIds=[
            str(id),
        ]
    )
        if response['AutoScalingInstances'][0]['LifecycleState']=='Standby':
            break
    return response['AutoScalingInstances'][0]['LifecycleState']