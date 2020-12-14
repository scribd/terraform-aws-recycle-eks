"""
lambda to check and report the count for a running pod
in a given instance id
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
# Configure your cluster name and region here
KUBE_FILEPATH = '/tmp/kubeconfig'
MIRROR_POD_ANNOTATION_KEY = "kubernetes.io/config.mirror"
CONTROLLER_KIND_DAEMON_SET = "DaemonSet"

def create_kube_config(eks, cluster_name):
    """Creates the Kubernetes config file required when instantiating the API client."""
    cluster_info = eks.describe_cluster(name=cluster_name)['cluster']
    certificate = cluster_info['certificateAuthority']['data']
    endpoint = cluster_info['endpoint']

    kube_config = {
        'apiVersion': 'v1',
        'clusters': [
            {
                'cluster':
                    {
                        'server': endpoint,
                        'certificate-authority-data': certificate
                    },
                'name': 'k8s'

            }],
        'contexts': [
            {
                'context':
                    {
                        'cluster': 'k8s',
                        'user': 'aws'
                    },
                'name': 'aws'
            }],
        'current-context': 'aws',
        'Kind': 'config',
        'users': [
            {
                'name': 'aws',
                'user': 'lambda'
            }]
    }

    with open(KUBE_FILEPATH, 'w') as kube_file_content:
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

    client = session.client('sts', region_name=region)
    service_id = client.meta.service_model.service_id

    signer = RequestSigner(
        service_id,
        region,
        'sts',
        'v4',
        session.get_credentials(),
        session.events
    )

    params = {
        'method': 'GET',
        'url': 'https://sts.{}.amazonaws.com/?Action=GetCallerIdentity&Version=2011-06-15'.format(region),
        'body': {},
        'headers': {
            'x-k8s-aws-id': cluster
        },
        'context': {}
    }

    signed_url = signer.generate_presigned_url(
        params,
        region_name=region,
        expires_in=STS_TOKEN_EXPIRES_IN,
        operation_name=''
    )

    base64_url = base64.urlsafe_b64encode(signed_url.encode('utf-8')).decode('utf-8')

    # need to remove base64 encoding padding:
    # https://github.com/kubernetes-sigs/aws-iam-authenticator/issues/202
    return 'k8s-aws-v1.' + re.sub(r'=*', '', base64_url)

def get_evictable_pods(api, node_name,label_selector):
    '''
    This method will ensure we are only waiting for pods that matters based on
    label_selector
    '''
    field_selector = 'spec.nodeName=' + node_name
    pods = api.list_pod_for_all_namespaces(watch=False, field_selector=field_selector,
        label_selector = label_selector, include_uninitialized=True)
    return [pod for pod in pods.items]

def count_running_pods(api, node_name,label_selector):
    '''
    Report count for total running pods based on the label
    '''
    pods = get_evictable_pods(api, node_name,label_selector)
    return len(pods)

def handler(event, context):
    '''
    Lambda handler, this function will call the
    private functions to get the running pod count based on the label selector provided
    '''
    eks = boto3.client('eks', region_name=event['region'])
    #loading Kube Config
    if not os.path.exists(KUBE_FILEPATH):
        create_kube_config(eks, event['cluster_name'])
    k8s.config.load_kube_config(KUBE_FILEPATH)
    configuration = k8s.client.Configuration()
    #getting the auth token
    token = get_bearer_token(event['cluster_name'],event['region'])
    configuration.api_key['authorization'] = token
    configuration.api_key_prefix['authorization'] = 'Bearer'
    # API
    api = k8s.client.ApiClient(configuration)
    core_v1_api = k8s.client.CoreV1Api(api)

    # Get all the pods
    running_pod_count=count_running_pods(core_v1_api,node_name=event['node_name'],
        label_selector=event['label_selector'])
    output_json = {"region": event['region'], "node_name" : event['node_name'] ,
                    "instance_id" : event['instance_id'], "cluster_name": event['cluster_name'],
                     "activePodCount": running_pod_count}
    return output_json
