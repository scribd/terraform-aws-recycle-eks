"""Puts the instance in the standby mode
there is immense possibility here we can read from cludwatch warnings,
or based on some other metrics to identify the
instance automatically
for now I am taking it as a input
"""
import time
import boto3

ec2_client = boto3.client("ec2")
asg_client = boto3.client("autoscaling")


def lambda_handler(event, context):
    """
    default lambda handler, this is the function that takes
    instance id as in input to put it in standby state. Using autoscaling api to
    automatically add a new instance to the group while putting the old instance to standby state.
    The old instance will get into "Standby" state only when the
    new instance is in fully "Inservice" state
    """
    instance_id = event["instance_id"]
    cluster_name = event["cluster_name"]
    label_selector = event["label_selector"]
    # Capture all the info about the instance so we can extract the ASG name later
    response = ec2_client.describe_instances(
        Filters=[
            {"Name": "instance-id", "Values": [instance_id]},
        ],
    )

    # Get the ASG name from the response JSON
    instancedetails = response["Reservations"][0]["Instances"][0]
    region = instancedetails["Placement"]["AvailabilityZone"][0:9]
    node_name = instancedetails["PrivateDnsName"]
    tags = instancedetails["Tags"]
    autoscaling_name = next(
        t["Value"] for t in tags if t["Key"] == "aws:autoscaling:groupName"
    )

    # Put the instance in standby
    response = asg_client.enter_standby(
        InstanceIds=[
            instance_id,
        ],
        AutoScalingGroupName=autoscaling_name,
        ShouldDecrementDesiredCapacity=False,
    )

    response = asg_client.describe_auto_scaling_instances(
        InstanceIds=[
            instance_id,
        ]
    )
    # Giving a sleep as it takes some time to get the new node into inservice mode.
    # TODO: Check for new node in service before proceeding
    print(" Waiting for 300 Sec")
    time.sleep(300)
    while response["AutoScalingInstances"][0]["LifecycleState"] != "Standby":
        # after the initial 300 Sec we are reducing sleep to 5 sec for subsequent checks
        print("The node is yet to be in standby state. Waiting for 5 Sec")
        time.sleep(5)
        response = asg_client.describe_auto_scaling_instances(
            InstanceIds=[
                instance_id,
            ]
        )
        if response["AutoScalingInstances"][0]["LifecycleState"] == "Standby":
            break
    output_json = {
        "region": region,
        "node_name": node_name,
        "instance_id": instance_id,
        "cluster_name": cluster_name,
        "label_selector": label_selector,
    }
    return output_json
