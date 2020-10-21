from kubernetes import client, config
import yaml
import boto3
import os.path
import base64
import string
import random
from botocore.signers import RequestSigner

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)
# Configure your cluster name and region here
KUBE_FILEPATH = '/tmp/kubeconfig'
CLUSTER_NAME = 'hackweek-2020-local-eks-cluster'
REGION = 'us-east-2'
NODE_NAME='ip-10-226-87-16.us-east-2.compute.internal'


if not os.path.exists(KUBE_FILEPATH):
    
    kube_content = dict()
    # Get data from EKS API
    eks_api = boto3.client('eks',region_name=REGION)
    cluster_info = eks_api.describe_cluster(name=CLUSTER_NAME)
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
        'name':CLUSTER_NAME
                
        }]

    kube_content['contexts'] = [
        {
        'context':
            {
            'cluster':CLUSTER_NAME,
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

def get_bearer_token(cluster_id, region):
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

def local_handler():
    #nodelist =[]
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
    #ret1= v1.list_node()
    ret = v1.list_node() #("default")
    for i in ret.items:
        #nodelist.append
        print("%s\t%s" % (i.metadata.creation_timestamp, i.metadata.name))
def handler(event, context):


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
    ret = v1.list_pod_for_all_namespaces() #("default")

    for i in ret.items:
        print("%s\t%s\t%s" % (i.status.pod_ip, i.metadata.namespace, i.metadata.name))
if __name__ == "__main__":
    local_handler()