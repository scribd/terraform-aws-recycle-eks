#!/bin/bash
#
# This script validates all of our resources to make sure they compile and are
# formatted correctly

set -xe

for m in $(ls modules); do
    echo ">> Checking formatting style for module ${m}"
    terraform fmt --check=true --diff "modules/${m}"
done

echo ">> Checking formatting style for main code base"
terraform fmt --check=true --diff

echo ">> Validating"
terraform validate
