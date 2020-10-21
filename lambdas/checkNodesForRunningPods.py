from kubernetes import client, config
import yaml
import boto3
import os.path
import base64
import string
import random
from botocore.signers import RequestSigner
import logging
import json
import time

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)
# Configure your cluster name and region here
KUBE_FILEPATH = '/tmp/kubeconfig'

def get_bearer_token(cluster_id, region):
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

        print(kube_content)
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

def pod_is_evictable(pod):
    if pod.metadata.annotations is not None: # and pod.metadata.annotations.get(MIRROR_POD_ANNOTATION_KEY):
        print("Skipping mirror pod {}/{}".format(pod.metadata.namespace, pod.metadata.name))
        return False
    if pod.metadata.owner_references is None:
        return True
    for ref in pod.metadata.owner_references:
        if ref.controller is not None and ref.controller:
            if ref.kind == CONTROLLER_KIND_DAEMON_SET:
                print("Skipping DaemonSet {}/{}".format(pod.metadata.namespace, pod.metadata.name))
                return False
    return True

def get_evictable_pods(api, node_name):
    field_selector = 'spec.nodeName=' + node_name
    pods = api.list_pod_for_all_namespaces(watch=False, field_selector=field_selector, include_uninitialized=True)
    return [pod for pod in pods.items if pod_is_evictable(pod)]
    #return [pod for pod in pods.items]

def count_running_pods(api, node_name):
    #print(node_name)
    pods = get_evictable_pods(api, node_name)
    #print(pods)
    return len(pods) 

def handler(event, context):
    time.sleep(10)
    token = get_bearer_token(event['cluster_name'],event['region'])
    # Configure
    config.load_kube_config(KUBE_FILEPATH)
    configuration = client.Configuration()
    configuration.api_key['authorization'] = token
    configuration.api_key_prefix['authorization'] = 'Bearer'
    # API
    api = client.ApiClient(configuration)
    v1 = client.CoreV1Api(api)

    # Get all the pods
    runningPodCount=count_running_pods(v1,node_name=event['node_name'])
    output_json = {"region": event['region'], "node_name" : event['node_name'] , "instance_id" : event['instance_id'],
                    "cluster_name": event['cluster_name'], "activePodCount": runningPodCount}
    return output_json

#######################
#     # Get Token
  
def local():
    REGION="us-east-2"
    NODE_NAME= "ip-10-226-44-234.us-east-2.compute.internal"
    CLUSTER_NAME= "kuntalb-cplat-local-airflow-v1"
    token = get_bearer_token(CLUSTER_NAME,REGION)
    # Configure
    config.load_kube_config(KUBE_FILEPATH)
    configuration = client.Configuration()
    configuration.api_key['authorization'] = token
    configuration.api_key_prefix['authorization'] = 'Bearer'
    # API
    api = client.ApiClient(configuration)
    v1 = client.CoreV1Api(api)

    # Get all the pods
    runningPodCount=count_running_pods(v1,node_name=NODE_NAME)
    #output_dict = {"activePodCount": runningPodCount}
    output_json = json.dumps({'activePodCount': runningPodCount})
    print(output_json)

if __name__ == "__main__":
    local()