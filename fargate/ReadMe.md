# General Notes

## Fargate Task Networking

### Container Networking:
In Fargate, when you launch multiple containers as part of a single task, they can also communicate with each other over the local loopback interface.

#### Local LoopBack Network Interface:
By making a networking request to this local interface, it bypasses the network interface hardware and instead the operating system just routes network calls from one process to the other directly.

### Fargate **awsvpc** mode:
Fargate uses a special container networking mode called awsvpc, which gives all the containers in a Task a shared elastic network interface (one ENI per Fargate Task) to use for communication and this ENI derives an IP address from the subnet it is part of. In this mode only ALB and NLB are supported.

####ENI:
If the ENI is in a public subnet (a subnet which has a route in its routing table to an Internet Gateway) then the ENI gets both a Public and Private IP Addresses. If the ENI is in a private subnet then the ENI only gets a Private IP address.

The Fargate tasks inside the Private subnet don’t have public IP addresses, only private IP addresses. Instead of an internet gateway, the route table for a Private subnet has a route to a network address translation (NAT) gateway which resides in the Public Subnet.


### Traffic Flow Patterns:

#### Inbound Flow: 
Internet Gateway --> ELB in Public Subnet (with target groups and listeners having Path based routing rules) --> Public Task -->  ELB in Private Subnet (with target groups and listeners having Path based routing rules) --> Private Task

#### Outbound Flow: 
Private Task --> NAT Gateway in Public Subnet --> Internet Gateway
Public Task --> Internet Gateway

#### Comms between Tasks within a Public or Private Subnet:
If tasks want to communicate directly with each other, they can use each other’s private IP address to send traffic directly from one to the other so that it stays inside the subnet.
Public Task1 --> Public Task2
Private Task1 --> Private Task2

#### Call from Public Task to a Private Task:
Public Task --> ELB in Private Subnet --> Private Task


