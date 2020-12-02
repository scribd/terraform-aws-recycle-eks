"""
This module put unschedulable taint to an standby node
"""
import os.path
import base64
import logging
import yaml
import boto3
from botocore.signers import RequestSigner
from kubernetes import client, config

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

KUBE_FILEPATH = '/tmp/kubeconfig'

def get_bearer_token(cluster_id, region):
    '''
    created the bearer token
    '''
    if not os.path.exists(KUBE_FILEPATH):
        kube_content = dict()
        # Get data from EKS API
        eks_api = boto3.client('eks',region_name=region)
        cluster_info = eks_api.describe_cluster(name=cluster_id)
        certificate = cluster_info['cluster']['certificateAuthority']['data']
        endpoint = cluster_info['cluster']['endpoint']
        # Generating kubeconfig
        kube_content = dict()
        kube_content['apiVersion'] = 'v1'
        kube_content['clusters'] = [
            {
            'cluster':
                {
                'server': endpoint,
                'certificate-authority-data': certificate
                },
            'name':cluster_id
            }]
        kube_content['contexts'] = [
            {
            'context':
                {
                'cluster':cluster_id,
                'user':'aws'
                },
            'name':'aws'
            }]
        kube_content['current-context'] = 'aws'
        kube_content['Kind'] = 'config'
        kube_content['users'] = [
        {
        'name':'aws',
        'user':'lambda'
        }]
        # Write kubeconfig
        with open(KUBE_FILEPATH, 'w') as outfile:
            yaml.dump(kube_content, outfile, default_flow_style=False)
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
            'x-k8s-aws-id': cluster_id
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


def taint_node(api, node_name):
    '''
    taints a single node
    '''
    patch_body = {
        'apiVersion': 'v1',
        'kind': 'Node',
        'metadata': {
            'name': node_name
        },
        'spec': {
            'unschedulable': True
        }
    }

    return api.patch_node(node_name, patch_body)

def handler(event, context):
    '''
    lambda handler function
    '''
    token = get_bearer_token(event['cluster_name'],event['region'])
    config.load_kube_config(KUBE_FILEPATH)
    configuration = client.Configuration()
    configuration.api_key['authorization'] = token
    configuration.api_key_prefix['authorization'] = 'Bearer'
    # API
    api = client.ApiClient(configuration)
    v1 = client.CoreV1Api(api)
    # Get all the pods
    response=taint_node(v1,node_name=event['node_name'])
    output_json = {"region": event['region'], "node_name" : event['node_name'] ,
                    "cluster_name": event['cluster_name'], "instance_id" : event['instance_id'],
                    "label_selector" : event['label_selector']}
    return output_json
