#!/bin/bash

for f in `cat openstack-projects.txt`; do
 git clone https://github.com/stackforge/cookbook-$f.git $f
done
