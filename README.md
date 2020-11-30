# terraform-aws-recycle-eks

This module creates a terraform module to recycle EKS worker nodes. The high level functionalities are explained below,
 - Use a lamdba to take an instance id as an input, to put it in standby mode, also add one more instance to the pool, once that instance is fully "inservice" mode then only have this instance id to standby
 - Taint this "Standby" node in EKS using K8S API in Lambda to prevent new pods from getting scheduled into this node
 - Periodically use K8S API check for status of “stateful” pods on that node. Another Lambda will do that
 - Once all stateful pods have completed on the node, use K8S API in another Lambda to drain the standby node
 - Once the number of running pod reached 0, terminate that standby instance using AWS SDK.

## TODO:
 - The stateful pod checking logic can be made customizable to restrict the check to only pods created for a particular task tasks, for e.g., check for any pod with a specific tag set by the Airflow scheduler
 - Stop using anonymous role and find a way to map the role with a proper user
 - get_bearer_token() function used in all lambda. Refactor the code to use as a Python module.

There are two main components:

1. Lambdas
2. Step Function in AWS, to chain the Lambdas and pass on the parameters form one Lamda to another Lamda


## Usage

**Set up all supported AWS / Datadog integrations**

```
module "recycl-eks-worker-npde" {
  source = "git::git@github.com:scribd/terraform-aws-recycle-eks.git"
  name                   = "string"
  tags                            = {
    Environment = "dev"
    Terraform   = "true"
  }
  vpc_subnet_ids         = ["subnet-12345678", "subnet-87654321"]
  vpc_security_group_ids = ["sg-12345678"]
  aws_region             = "us-east-2"

}
```

## Development

Releases are cut using [semantic-release](https://github.com/semantic-release/semantic-release).

Please write commit messages following [Angular commit guidelines](https://github.com/angular/angular.js/blob/master/DEVELOPERS.md#-git-commit-guidelines)


### Release flow

Semantic-release is configured with the [default branch workflow](https://semantic-release.gitbook.io/semantic-release/usage/configuration#branches)

For this project, releases will be cut from master as features and bugs are developed.


### Maintainers
- [Kuntal](https://github.com/kuntalkumarbasu)

### Special Notes:
- There is an excellent module on [Gracefully drain Kubernetes pods from EKS worker nodes during autoscaling scale-in events](https://github.com/aws-samples/amazon-k8s-node-drainer). We followed some of the principles in the Lambdas.
- Orchestrating Amazon Kubernetes Service (EKS) from AWS Lambda](https://medium.com/@alejandro.millan.frias/managing-kubernetes-from-aws-lambda-7922c3546249) is another writeup that we used.

