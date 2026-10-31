# Part 01: Build Your AWS Workstation

Everything in this lab happens in AWS. Your laptop only needs the AWS CLI and an SSH client. By the end of this part you will have:

- Your own VPC with two public subnets
- An EC2 instance (your workstation) that you can SSH into
- An IAM role on that instance, so it can use AWS without any access keys stored on it

Concept: why two subnets in two Availability Zones? Amazon EKS needs subnets in at least two AZs. We build the network once, in a way that works for EC2 now and EKS later.

Region for the whole lab: ap-south-1 (Mumbai).

## Step 1: Create a key pair

In the AWS console, switch to Mumbai, then go to EC2, Key pairs, Create key pair.

- Name: triage-key
- Type: RSA
- Format: .ppk if you use PuTTY on Windows, .pem if you use ssh on Mac or Linux

Keep the file safe. AWS will not show it again.

## Step 2: Check the AWS CLI on your laptop

Windows users: run these in Git Bash.

```bash
export AWS_REGION=ap-south-1
export AWS_DEFAULT_REGION=ap-south-1
aws --version
aws sts get-caller-identity
aws ec2 describe-key-pairs --key-names triage-key --query 'KeyPairs[0].KeyName' --output text
```

The last command must print triage-key. If it does not, your key was created in another region.

## Step 3: Create the VPC network

```bash
VPC_ID=$(aws ec2 create-vpc --cidr-block 10.0.0.0/16 \
  --tag-specifications 'ResourceType=vpc,Tags=[{Key=Name,Value=triage-vpc}]' \
  --query Vpc.VpcId --output text)
aws ec2 modify-vpc-attribute --vpc-id $VPC_ID --enable-dns-hostnames Value=true

IGW_ID=$(aws ec2 create-internet-gateway \
  --tag-specifications 'ResourceType=internet-gateway,Tags=[{Key=Name,Value=triage-igw}]' \
  --query InternetGateway.InternetGatewayId --output text)
aws ec2 attach-internet-gateway --internet-gateway-id $IGW_ID --vpc-id $VPC_ID

SUBNET_A=$(aws ec2 create-subnet --vpc-id $VPC_ID --cidr-block 10.0.1.0/24 --availability-zone ap-south-1a \
  --tag-specifications 'ResourceType=subnet,Tags=[{Key=Name,Value=triage-public-a},{Key=kubernetes.io/role/elb,Value=1}]' \
  --query Subnet.SubnetId --output text)
SUBNET_B=$(aws ec2 create-subnet --vpc-id $VPC_ID --cidr-block 10.0.2.0/24 --availability-zone ap-south-1b \
  --tag-specifications 'ResourceType=subnet,Tags=[{Key=Name,Value=triage-public-b},{Key=kubernetes.io/role/elb,Value=1}]' \
  --query Subnet.SubnetId --output text)
aws ec2 modify-subnet-attribute --subnet-id $SUBNET_A --map-public-ip-on-launch
aws ec2 modify-subnet-attribute --subnet-id $SUBNET_B --map-public-ip-on-launch

RT_ID=$(aws ec2 create-route-table --vpc-id $VPC_ID \
  --tag-specifications 'ResourceType=route-table,Tags=[{Key=Name,Value=triage-public-rt}]' \
  --query RouteTable.RouteTableId --output text)
aws ec2 create-route --route-table-id $RT_ID --destination-cidr-block 0.0.0.0/0 --gateway-id $IGW_ID
aws ec2 associate-route-table --route-table-id $RT_ID --subnet-id $SUBNET_A
aws ec2 associate-route-table --route-table-id $RT_ID --subnet-id $SUBNET_B

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

Concept: the file ~/triage-lab.env saves every ID. If your terminal closes, run source ~/triage-lab.env and continue. We also use it for cleanup at the end.

Concept: the tag kubernetes.io/role/elb=1 tells EKS it may create a public load balancer in these subnets.

## Step 4: Security group and EC2 instance

```bash
source ~/triage-lab.env
export MSYS_NO_PATHCONV=1

MY_IP=$(curl -s https://checkip.amazonaws.com)

SG_ID=$(aws ec2 create-security-group --group-name triage-workstation-sg \
  --description "SSH from my IP only" --vpc-id $VPC_ID \
  --query GroupId --output text)
aws ec2 authorize-security-group-ingress --group-id $SG_ID \
  --protocol tcp --port 22 --cidr ${MY_IP}/32

AMI_ID=$(aws ssm get-parameters \
  --names /aws/service/ami-amazon-linux-latest/al2023-ami-kernel-default-x86_64 \
  --query 'Parameters[0].Value' --output text)

INSTANCE_ID=$(aws ec2 run-instances --image-id $AMI_ID --instance-type t3.medium \
  --key-name triage-key --subnet-id $SUBNET_A --security-group-ids $SG_ID \
  --block-device-mappings 'DeviceName=/dev/xvda,Ebs={VolumeSize=20,VolumeType=gp3}' \
  --tag-specifications 'ResourceType=instance,Tags=[{Key=Name,Value=triage-workstation}]' \
  --query 'Instances[0].InstanceId' --output text)
aws ec2 wait instance-running --instance-ids $INSTANCE_ID

PUBLIC_IP=$(aws ec2 describe-instances --instance-ids $INSTANCE_ID \
  --query 'Reservations[0].Instances[0].PublicIpAddress' --output text)

cat >> ~/triage-lab.env <<EOT
export MSYS_NO_PATHCONV=1
export SG_ID=$SG_ID
export INSTANCE_ID=$INSTANCE_ID
export PUBLIC_IP=$PUBLIC_IP
EOT
echo "Connect to: ec2-user@$PUBLIC_IP"
```

Concept: MSYS_NO_PATHCONV=1 is only for Git Bash on Windows. Without it, Git Bash rewrites values like /aws/service/... into Windows paths and the command fails.

Concept: why x86 and t3.medium? x86 matches the EKS nodes, so the Docker image we build runs there without an "exec format error". t3.medium has enough memory for Docker builds.

## Step 5: Connect to the workstation

PuTTY on Windows:

1. Host Name: ec2-user@PUBLIC_IP, Port 22
2. Connection, SSH, Auth, Credentials, Private key file: triage-key.ppk
3. Save the session and click Open

Mac or Linux:

```bash
chmod 400 triage-key.pem
ssh -i triage-key.pem ec2-user@PUBLIC_IP
```

Check:

```bash
cat /etc/os-release | head -2
uname -m
whoami
```

Expected:

```
NAME="Amazon Linux"
VERSION="2023"
x86_64
ec2-user
```

If SSH times out later, your home IP may have changed. Allow the new IP from your laptop:

```bash
source ~/triage-lab.env
aws ec2 authorize-security-group-ingress --group-id $SG_ID --protocol tcp --port 22 --cidr $(curl -s https://checkip.amazonaws.com)/32
```

## Step 6: Give the workstation an IAM role

Question first: how should this EC2 machine get AWS permissions? Should we copy our access keys onto it?

No. Remember page 07, Secrets. Keys on a machine can leak. Instead we attach an IAM role. AWS hands the machine short lived credentials automatically, and nothing secret is stored on disk.

From your laptop:

```bash
source ~/triage-lab.env

cat > trust.json <<'EOT'
{
  "Version": "2012-10-17",
  "Statement": [{
    "Effect": "Allow",
    "Principal": { "Service": "ec2.amazonaws.com" },
    "Action": "sts:AssumeRole"
  }]
}
EOT

aws iam create-role --role-name triage-workstation-role \
  --assume-role-policy-document file://trust.json --query Role.Arn --output text
aws iam attach-role-policy --role-name triage-workstation-role \
  --policy-arn arn:aws:iam::aws:policy/AdministratorAccess

aws iam create-instance-profile --instance-profile-name triage-workstation-profile \
  --query InstanceProfile.Arn --output text
aws iam add-role-to-instance-profile --instance-profile-name triage-workstation-profile \
  --role-name triage-workstation-role

sleep 15
aws ec2 associate-iam-instance-profile --instance-id $INSTANCE_ID \
  --iam-instance-profile Name=triage-workstation-profile \
  --query IamInstanceProfileAssociation.State --output text
```

Concept: AdministratorAccess is for this lab only, because the workstation will create the EKS cluster and load balancers. In production you give a role only the permissions it needs. That is called least privilege.

On the workstation:

```bash
aws configure set region ap-south-1
aws sts get-caller-identity
```

You should see assumed-role/triage-workstation-role in the Arn. That is your machine using the role, with no keys anywhere.

## What you built

- triage-vpc with two public subnets in ap-south-1a and ap-south-1b
- triage-workstation, an EC2 instance you can SSH into
- triage-workstation-role, so the workstation can use AWS without keys

Next: Part 02, install the tools and start the EKS cluster.

## Stay connected

- YouTube: https://www.youtube.com/@BuildAutomateArchitect
- System Design playlist: https://www.youtube.com/playlist?list=PLeAHTLMwFYQ0
- Telegram: https://t.me/BuildAutomateArchitect
- Website: https://rahulchaubeyconsulting.com/
