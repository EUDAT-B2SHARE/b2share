#!/bin/bash

b2share db destroy --yes-i-know
b2share index destroy --yes-i-know
b2share db create 
b2share index init
b2share schemas init
b2share demo load_config -f
b2share demo load_data
b2share demo import_v1_data -v -d IoiST2yAgsmLKjygtUm2NFGaMKK82IcnLidZWnOsHV1PcLJzeSqQOqL6B8hr /tmp/b2sharev1
