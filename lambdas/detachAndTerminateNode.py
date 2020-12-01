import json
import boto3
import time

ec2_client = boto3.client('ec2')
asg_client = boto3.client('autoscaling')

def lambda_handler(event, context):
    instance_id = event['instance_id']
    # Capture all the info about the instance so we can extract the ASG name later
    response = ec2_client.describe_instances(
        Filters=[
            {
                'Name': 'instance-id',
                'Values': [instance_id]
            },
        ],
    )

    # Get the ASG name from the response JSON
    tags = response['Reservations'][0]['Instances'][0]['Tags']
    autoscaling_name = next(t["Value"] for t in tags if t["Key"] == "aws:autoscaling:groupName")

    #Put the instance in standby
    response = asg_client.exit_standby(
        InstanceIds=[
            instance_id,
        ],
        AutoScalingGroupName=autoscaling_name
    )

    response = asg_client.describe_auto_scaling_instances(
        InstanceIds=[
            instance_id,
        ]
    )
    while response['AutoScalingInstances'][0]['LifecycleState']!='InService':
        time.sleep(5)
        response = asg_client.describe_auto_scaling_instances(
        InstanceIds=[
            instance_id,
        ]
    )
        if response['AutoScalingInstances'][0]['LifecycleState']=='InService':
            break
   # Detach the instance
    response = asg_client.detach_instances(
        InstanceIds=[
            instance_id,
        ],
        AutoScalingGroupName=autoscaling_name,
        ShouldDecrementDesiredCapacity=True
    )

    response = ec2_client.describe_instances(
        Filters=[
            {
                'Name': 'instance-id',
                'Values': [instance_id]
            },
        ],
    )

    while response['Reservations'][0]['Instances'][0]['Tags']==autoscaling_name:
        # sleep added to reduce the number of api calls for checking the status
        time.sleep(10)
        response = ec2_client.describe_instances(
        Filters=[
            {
                'Name': 'instance-id',
                'Values': [instance_id]
            },
        ],
    )
        if response['Reservations'][0]['Instances'][0]['Tags']!=autoscaling_name:
            break

#if the node is detqched then stop the instance

    response = ec2_client.stop_instances(
        InstanceIds=[
            instance_id,
        ],
    )