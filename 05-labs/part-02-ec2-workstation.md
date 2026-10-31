# Part 02: Launch the EC2 Workstation

We will not install Python, Docker or Kubernetes on our laptops. All the work happens on an EC2 instance in AWS. This is our workstation for the whole lab.

Concept: EC2 is our workstation. EKS is where our application runs. Keep those two separate in your mind.

By the end of this part you will have:

- An IAM role that gives the workstation AWS permissions, with no access keys
- A key pair to log in
- An EC2 instance in triage-vpc that you can SSH into

Everything in this part is done in the AWS console, region Asia Pacific (Mumbai) ap-south-1.

## Step 1: Create the IAM role first

Question: our workstation will create an EKS cluster and push images to ECR. How does it get permission? Should we copy our access keys onto it?

No. Remember the Secrets page. Keys copied onto a machine can leak. Instead we attach an IAM role. AWS gives the machine short lived credentials automatically, and nothing secret is stored on disk.

1. Open IAM, Roles, Create role.
2. Trusted entity type: AWS service. Use case: EC2. Click Next.
3. Search for AdministratorAccess and tick it. Click Next.
4. Role name: triage-workstation-role. Click Create role.

Concept: AdministratorAccess is for this lab only, because the workstation creates the EKS cluster, its node group and its load balancer. In production you give a role only the permissions it needs. That is called least privilege.

Concept: we create the role BEFORE launching the instance and attach it at launch. If you attach a role to a running instance seconds after creating it, IAM may not be ready yet and the instance can end up with no credentials.

## Step 2: Create a key pair

1. Open EC2, Key pairs, Create key pair.
2. Name: triage-key
3. Key pair type: RSA
4. Private key file format: .ppk for PuTTY on Windows, .pem for ssh on Mac or Linux
5. Click Create key pair. The file downloads. Keep it safe, AWS will not show it again.

## Step 3: Launch the instance

Open EC2, Instances, Launch instances, and fill in:

| Field | Value |
|---|---|
| Name | triage-workstation |
| AMI | Amazon Linux 2023 |
| Architecture | 64-bit (x86) |
| Instance type | t3.medium |
| Key pair | triage-key |

Network settings, click Edit:

| Field | Value |
|---|---|
| VPC | triage-vpc |
| Subnet | triage-public-a |
| Auto-assign public IP | Enable |
| Firewall | Create security group |
| Security group name | triage-workstation-sg |
| Inbound rule | SSH, TCP 22, Source type: My IP |

Configure storage: 20 GiB, gp3.

Advanced details: IAM instance profile: triage-workstation-role.

Click Launch instance.

Concept: why x86 and not Arm? Our EKS nodes are x86. A Docker image built on an Arm machine fails on x86 nodes with "exec format error". Build where you run.

Concept: why t3.medium? Docker builds need memory. A t3.micro runs out of memory during the build.

Concept: SSH only from My IP. Port 22 open to the whole internet is how machines get attacked.

## Step 4: Connect

Copy the Public IPv4 address of the instance from the EC2 console.

PuTTY on Windows:

1. Session, Host Name: ec2-user@PUBLIC_IP, Port: 22
2. Connection, SSH, Auth, Credentials, Private key file: triage-key.ppk
3. Back to Session, type triage-workstation under Saved Sessions, click Save, then Open
4. Accept the host key prompt

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

If SSH times out, your home IP may have changed. In the console, open the security group triage-workstation-sg, Edit inbound rules, and set the SSH source to My IP again.

## Step 5: Prove the workstation uses the role

```bash
aws configure set region ap-south-1
aws sts get-caller-identity
```

Expected (your account and instance IDs will differ):

```
{
    "UserId": "AROA...:i-0abc...",
    "Account": "123456789012",
    "Arn": "arn:aws:sts::123456789012:assumed-role/triage-workstation-role/i-0abc..."
}
```

The key part is assumed-role/triage-workstation-role. The machine is using the role. There are no keys anywhere on it.

## Troubleshooting: Unable to locate credentials

If aws sts get-caller-identity says "Unable to locate credentials", ask the machine itself which role it has:

```bash
TOKEN=$(curl -s -X PUT "http://169.254.169.254/latest/api/token" -H "X-aws-ec2-metadata-token-ttl-seconds: 300")
curl -s -H "X-aws-ec2-metadata-token: $TOKEN" http://169.254.169.254/latest/meta-data/iam/security-credentials/
```

It should print triage-workstation-role. If it prints a 404 page, the role did not reach the instance. Fix it in the console:

1. EC2, Instances, select triage-workstation
2. Actions, Security, Modify IAM role, choose No IAM role, Update IAM role, confirm
3. Actions, Security, Modify IAM role, choose triage-workstation-role, Update IAM role
4. Wait 30 seconds and run aws sts get-caller-identity again

Concept: 169.254.169.254 is the instance metadata service. It is how an EC2 machine learns about itself, including the temporary credentials of its role.

Next: Part 03, install the tools and create the EKS cluster.

## Stay connected

- YouTube: https://www.youtube.com/@BuildAutomateArchitect
- System Design playlist: https://www.youtube.com/playlist?list=PLeAHTLMwFYQ0
- Telegram: https://t.me/BuildAutomateArchitect
- Website: https://rahulchaubeyconsulting.com/
