# Part 01: Create the VPC and Subnets

Before we run anything, we need a network to run it in. In this part we build that network with the AWS CLI.

By the end of this part you will have:

- A VPC called triage-vpc
- Two public subnets in two Availability Zones
- An internet gateway and a route table, so instances can reach the internet

Question: why two subnets in two Availability Zones, when one EC2 instance needs only one subnet?

Because later, Amazon EKS needs subnets in at least two Availability Zones. We build the network once, in a way that works for EC2 now and EKS later.

## Before you start

You need the AWS CLI installed and configured on your laptop. Windows users: run everything in Git Bash.

Check that the CLI works and is pointing at Mumbai:

```bash
export AWS_REGION=ap-south-1
export AWS_DEFAULT_REGION=ap-south-1
aws --version
aws sts get-caller-identity
```

You should see your account ID. If you see an error, run aws configure first.

## Step 1: Create the VPC

```bash
VPC_ID=$(aws ec2 create-vpc --cidr-block 10.0.0.0/16 \
  --tag-specifications 'ResourceType=vpc,Tags=[{Key=Name,Value=triage-vpc}]' \
  --query Vpc.VpcId --output text)
aws ec2 modify-vpc-attribute --vpc-id $VPC_ID --enable-dns-hostnames Value=true
echo "VPC: $VPC_ID"
```

Concept: DNS hostnames must be enabled for EKS. Without it, the worker nodes cannot register with the cluster.

## Step 2: Create and attach the internet gateway

```bash
IGW_ID=$(aws ec2 create-internet-gateway \
  --tag-specifications 'ResourceType=internet-gateway,Tags=[{Key=Name,Value=triage-igw}]' \
  --query InternetGateway.InternetGatewayId --output text)
aws ec2 attach-internet-gateway --internet-gateway-id $IGW_ID --vpc-id $VPC_ID
echo "Internet gateway: $IGW_ID"
```

## Step 3: Create two public subnets

```bash
SUBNET_A=$(aws ec2 create-subnet --vpc-id $VPC_ID --cidr-block 10.0.1.0/24 --availability-zone ap-south-1a \
  --tag-specifications 'ResourceType=subnet,Tags=[{Key=Name,Value=triage-public-a},{Key=kubernetes.io/role/elb,Value=1}]' \
  --query Subnet.SubnetId --output text)

SUBNET_B=$(aws ec2 create-subnet --vpc-id $VPC_ID --cidr-block 10.0.2.0/24 --availability-zone ap-south-1b \
  --tag-specifications 'ResourceType=subnet,Tags=[{Key=Name,Value=triage-public-b},{Key=kubernetes.io/role/elb,Value=1}]' \
  --query Subnet.SubnetId --output text)

aws ec2 modify-subnet-attribute --subnet-id $SUBNET_A --map-public-ip-on-launch
aws ec2 modify-subnet-attribute --subnet-id $SUBNET_B --map-public-ip-on-launch
echo "Subnet A: $SUBNET_A"
echo "Subnet B: $SUBNET_B"
```

Concept: the tag kubernetes.io/role/elb=1 tells EKS that it may create a public load balancer in these subnets. We will need that when we expose our service.

Concept: map-public-ip-on-launch gives every instance in these subnets a public IP automatically. Our EC2 workstation and the EKS nodes both need it.

## Step 4: Create the route table

```bash
RT_ID=$(aws ec2 create-route-table --vpc-id $VPC_ID \
  --tag-specifications 'ResourceType=route-table,Tags=[{Key=Name,Value=triage-public-rt}]' \
  --query RouteTable.RouteTableId --output text)
aws ec2 create-route --route-table-id $RT_ID --destination-cidr-block 0.0.0.0/0 --gateway-id $IGW_ID
aws ec2 associate-route-table --route-table-id $RT_ID --subnet-id $SUBNET_A
aws ec2 associate-route-table --route-table-id $RT_ID --subnet-id $SUBNET_B
```

The last three commands print a little JSON. That is normal.

Concept: a subnet is public only because its route table sends 0.0.0.0/0 to an internet gateway. That one route is the whole difference between public and private.

## Step 5: Save every ID

```bash
cat > ~/triage-lab.env <<EOT
export AWS_REGION=ap-south-1
export AWS_DEFAULT_REGION=ap-south-1
export VPC_ID=$VPC_ID
export IGW_ID=$IGW_ID
export SUBNET_A=$SUBNET_A
export SUBNET_B=$SUBNET_B
export RT_ID=$RT_ID
EOT
cat ~/triage-lab.env
```

Concept: this file is your memory for the lab. If your terminal closes, run source ~/triage-lab.env and continue. We also use it to clean up at the end. Write down the two subnet IDs, you need them in Part 03.

## Check it in the console

Open VPC in the AWS console, Mumbai region. You should see:

- Your VPCs: triage-vpc
- Subnets: triage-public-a and triage-public-b
- Internet gateways: triage-igw, attached
- Route tables: triage-public-rt, with a route 0.0.0.0/0 to the internet gateway

Concept: in a real company, the EKS nodes would sit in private subnets and only the load balancer would be public. We use public subnets to keep the lab simple.

Next: Part 02, launch the EC2 workstation.

## Stay connected

- YouTube: https://www.youtube.com/@BuildAutomateArchitect
- System Design playlist: https://www.youtube.com/playlist?list=PLeAHTLMwFYQ0
- Telegram: https://t.me/BuildAutomateArchitect
- Website: https://rahulchaubeyconsulting.com/
