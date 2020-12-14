"""
This module put unschedulable taint to an standby node
"""
import os.path
import base64
import logging
import re
import yaml
import boto3
import kubernetes as k8s
from botocore.signers import RequestSigner

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

KUBE_FILEPATH = "/tmp/kubeconfig"


def create_kube_config(eks, cluster_name):
    """Creates the Kubernetes config file required when instantiating the API client."""
    cluster_info = eks.describe_cluster(name=cluster_name)["cluster"]
    certificate = cluster_info["certificateAuthority"]["data"]
    endpoint = cluster_info["endpoint"]

    kube_config = {
        "apiVersion": "v1",
        "clusters": [
            {
                "cluster": {
                    "server": endpoint,
                    "certificate-authority-data": certificate,
                },
                "name": "k8s",
            }
        ],
        "contexts": [{"context": {"cluster": "k8s", "user": "aws"}, "name": "aws"}],
        "current-context": "aws",
        "Kind": "config",
        "users": [{"name": "aws", "user": "lambda"}],
    }

    with open(KUBE_FILEPATH, "w") as kube_file_content:
        yaml.dump(kube_config, kube_file_content, default_flow_style=False)


def get_bearer_token(cluster, region):
    """Creates the authentication to token required by AWS IAM Authenticator. This is
    done by creating a base64 encoded string which represents a HTTP call to the STS
    GetCallerIdentity Query Request
    (https://docs.aws.amazon.com/STS/latest/APIReference/API_GetCallerIdentity.html).
    The AWS IAM Authenticator decodes the base64 string and makes the request on behalf of the user.
    """
    STS_TOKEN_EXPIRES_IN = 60
    session = boto3.session.Session()

    client = session.client("sts", region_name=region)
    service_id = client.meta.service_model.service_id

    signer = RequestSigner(
        service_id, region, "sts", "v4", session.get_credentials(), session.events
    )

    params = {
        "method": "GET",
        "url": "https://sts.{}.amazonaws.com/?Action=GetCallerIdentity&Version=2011-06-15".format(
            region
        ),
        "body": {},
        "headers": {"x-k8s-aws-id": cluster},
        "context": {},
    }

    signed_url = signer.generate_presigned_url(
        params, region_name=region, expires_in=STS_TOKEN_EXPIRES_IN, operation_name=""
    )

    base64_url = base64.urlsafe_b64encode(signed_url.encode("utf-8")).decode("utf-8")

    # need to remove base64 encoding padding:
    # https://github.com/kubernetes-sigs/aws-iam-authenticator/issues/202
    return "k8s-aws-v1." + re.sub(r"=*", "", base64_url)


def taint_node(api, node_name):
    """
    taints a single node
    """
    patch_body = {
        "apiVersion": "v1",
        "kind": "Node",
        "metadata": {"name": node_name},
        "spec": {"unschedulable": True},
    }

    api.patch_node(node_name, patch_body)


def handler(event, context):
    """
    lambda handler function
    """
    eks = boto3.client("eks", region_name=event["region"])
    # creating kube config
    if not os.path.exists(KUBE_FILEPATH):
        create_kube_config(eks, event["cluster_name"])
    # loading Kube Config
    k8s.config.load_kube_config(KUBE_FILEPATH)
    configuration = k8s.client.Configuration()
    token = get_bearer_token(event["cluster_name"], event["region"])
    # getting Auth Token
    configuration.api_key["authorization"] = token
    configuration.api_key_prefix["authorization"] = "Bearer"
    # API
    api = k8s.client.ApiClient(configuration)
    core_v1_api = k8s.client.CoreV1Api(api)
    # Get all the pods
    taint_node(core_v1_api, node_name=event["node_name"])
    output_json = {
        "region": event["region"],
        "node_name": event["node_name"],
        "cluster_name": event["cluster_name"],
        "instance_id": event["instance_id"],
        "label_selector": event["label_selector"],
    }
    return output_json
