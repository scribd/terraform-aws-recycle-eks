# Puts the instance in the standby mode
# there is immense possibility here we can read from cludwatch warnings, or based on some other metrics to identify the 
# instance automatically
# for now I am taking it as a input

import json
import boto3
import time
import string

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
    region=response['Reservations'][0]['Instances'][0]['Placement']['AvailabilityZone'][0:9]
    NODE_NAME=response['Reservations'][0]['Instances'][0]['PrivateDnsName']
    print(region)
    print(NODE_NAME)
    tags = response['Reservations'][0]['Instances'][0]['Tags']
    autoscaling_name = next(t["Value"] for t in tags if t["Key"] == "aws:autoscaling:groupName")
    print("Autoscaling name is - " + str(autoscaling_name))

    #Put the instance in standby
    response = asg_client.enter_standby(
        InstanceIds=[
            str(id),
        ],
        AutoScalingGroupName=str(autoscaling_name),
        ShouldDecrementDesiredCapacity=False
    )

    response = asg_client.describe_auto_scaling_instances(
        InstanceIds=[
            str(id),
        ]
    )
    while response['AutoScalingInstances'][0]['LifecycleState']!='Standby':
        time.sleep(15)
        response = asg_client.describe_auto_scaling_instances(
        InstanceIds=[
            str(id),
        ]
    )
        if response['AutoScalingInstances'][0]['LifecycleState']=='Standby':
            break
    output_json = {"region": region, "node_name" : NODE_NAME , "autoscaling_name" : autoscaling_name, "state": response['AutoScalingInstances'][0]['LifecycleState']}
    return output_json