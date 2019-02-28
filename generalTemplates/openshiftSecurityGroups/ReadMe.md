# Security Groups for OpenShift Container Platform 

1. Four Roles - Master, Infrastructure, Nodes, Worker/Application Nodes
2. Choose the Inbound and Outbound CIDRs based on your deployment being an Internal Only cluster or External Only cluster 

## Reason for choosing - "AWS::EC2::SecurityGroupEgress and AWS::EC2::SecurityGroupIngress"

If you want to cross-reference two security groups in the ingress and egress rules of those security groups, use the AWS::EC2::SecurityGroupEgress and AWS::EC2::SecurityGroupIngress resources to define your rules. Do not use the embedded ingress and egress rules in the AWS::EC2::SecurityGroup. Doing so creates a circular dependency, which AWS CloudFormation doesn't allow.

![Alt text](output.png?raw=true "")
