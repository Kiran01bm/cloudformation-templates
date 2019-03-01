# Repo for OCP CF Templates which are HA i.e multi-zone deployments


## ec2WithSecGroups.yaml
1. This is for 3 zone deployment.
2. Validated on us-east-2
3. Update Bastion CIDR i.e inboundCIDRRangeIPv4 for Public vs Private Network Deployment
4. Micorsegmentation in the form on fine grained Role based SG's


## VM Storage
1. Root disk
2. Common disks - Docker, OpenShift Local Volumes, Logging
3. Master disks - etcd
4. Infrastructure and Worker Nodes - NA just common disks


## Validating CF Template (after producing from whatever means ex:troposphere/boto etc):
```
aws cloudformation validate-template --template-body file://ec2WithSecGroups.yaml
```

## Security Groups
### Core
![Alt text](core.png?raw=true "")
### Iaas
![Alt text](iaas.png?raw=true "")
### Logging ES
![Alt text](logging-es.png?raw=true "")
