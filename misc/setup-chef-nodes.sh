#!/bin/bash

knife bootstrap ucontroller --sudo -x grace -P huawei -N ub-controller-node -E multi-node
knife bootstrap unetwork --sudo -x grace -P huawei -N ub-network-node -E multi-node
knife bootstrap ucompute --sudo -x grace -P huawei -N ub-compute-node -E multi-node

knife node run_list add ub-controller-node "role[os-compute-single-controller-no-network]"
knife node run_list add ub-compute-node "role[os-compute-worker]"
knife node run_list add ub-network-node "role[os-network]"

