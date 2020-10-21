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
    print(event)
    instance_id = event['instance_id']
    cluster_name= event['cluster_name']
    print("cluster_name is " + str(cluster_name))

    # Capture all the info about the instance so we can extract the ASG name later
    response = ec2_client.describe_instances(
        Filters=[
            {
                'Name': 'instance-id',
                'Values': [str(instance_id)]
            },
        ],
    )

    # Get the ASG name from the response JSON
    region=response['Reservations'][0]['Instances'][0]['Placement']['AvailabilityZone'][0:9]
    NODE_NAME=response['Reservations'][0]['Instances'][0]['PrivateDnsName']
    tags = response['Reservations'][0]['Instances'][0]['Tags']
    autoscaling_name = next(t["Value"] for t in tags if t["Key"] == "aws:autoscaling:groupName")

    #Put the instance in standby
    response = asg_client.enter_standby(
        InstanceIds=[
            str(instance_id),
        ],
        AutoScalingGroupName=str(autoscaling_name),
        ShouldDecrementDesiredCapacity=False
    )

    response = asg_client.describe_auto_scaling_instances(
        InstanceIds=[
            str(instance_id),
        ]
    )
    while response['AutoScalingInstances'][0]['LifecycleState']!='Standby':
        time.sleep(5)
        response = asg_client.describe_auto_scaling_instances(
        InstanceIds=[
            str(instance_id),
        ]
    )
        if response['AutoScalingInstances'][0]['LifecycleState']=='Standby':
            break
    output_json = {"region": region, "node_name" : NODE_NAME ,
                    "autoscaling_name" : autoscaling_name, "state": response['AutoScalingInstances'][0]['LifecycleState'], 
                    "cluster_name": cluster_name}
    return output_json