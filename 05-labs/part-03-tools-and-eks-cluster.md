# Part 03: Install the Tools and Create the EKS Cluster

Our workstation is ready. Now we install the tools we need and create the Amazon EKS cluster where our service will run.

| Tool | Why we need it |
|---|---|
| Docker | Builds the image of our service |
| Git | Moves our code to and from GitHub |
| kubectl | Talks to the EKS cluster |
| eksctl | Creates the EKS cluster |

Run everything in this part on the EC2 workstation.

## Step 1: Install the tools

```bash
# Docker and Git
sudo dnf install -y docker git
sudo systemctl enable --now docker
sudo usermod -aG docker ec2-user

# kubectl
curl -sLO "https://dl.k8s.io/release/$(curl -sL https://dl.k8s.io/release/stable.txt)/bin/linux/amd64/kubectl"
sudo install -m 0755 kubectl /usr/local/bin/kubectl && rm kubectl

# eksctl
curl -sLO "https://github.com/eksctl-io/eksctl/releases/latest/download/eksctl_Linux_amd64.tar.gz"
tar -xzf eksctl_Linux_amd64.tar.gz -C /tmp && rm eksctl_Linux_amd64.tar.gz
sudo install -m 0755 /tmp/eksctl /usr/local/bin/eksctl && rm /tmp/eksctl
```

## Step 2: Log out and log back in

Type exit and connect again.

Question: why do we need to reconnect?

We added ec2-user to the docker group, but a running session keeps the groups it started with. A new login picks up the docker group, so you can run Docker without sudo.

## Step 3: Check every tool

```bash
groups
docker version --format 'Docker {{.Server.Version}}'
git --version
kubectl version --client
eksctl version
docker run --rm hello-world | head -2
```

groups must list docker, and the last command must print Hello from Docker!

If Docker says "permission denied while trying to connect to the Docker daemon socket", you did not reconnect. Type exit and log in again.

## Step 4: Write the cluster config

We tell eksctl to use OUR VPC and OUR two subnets, instead of creating a new network.

First, put your own subnet IDs in two variables. You saved them in Part 01 (SUBNET_A and SUBNET_B in triage-lab.env), or you can find them in the console under VPC, Subnets.

```bash
SUBNET_A=subnet-xxxxxxxxxxxxxxxxx   # triage-public-a, ap-south-1a
SUBNET_B=subnet-yyyyyyyyyyyyyyyyy   # triage-public-b, ap-south-1b
```

Then create the file:

```bash
mkdir -p ~/triage && cd ~/triage

cat > cluster.yaml <<EOF
apiVersion: eksctl.io/v1alpha5
kind: ClusterConfig

metadata:
  name: triage-cluster
  region: ap-south-1

vpc:
  subnets:
    public:
      ap-south-1a: { id: $SUBNET_A }
      ap-south-1b: { id: $SUBNET_B }

managedNodeGroups:
  - name: triage-nodes
    instanceType: t3.medium
    desiredCapacity: 2
    minSize: 2
    maxSize: 3
    volumeSize: 20
EOF

cat cluster.yaml
```

Check that the two subnet IDs in the output are real IDs and not empty.

Concept: what are we asking for?

- A control plane: the Kubernetes brain, run and managed by AWS
- A managed node group of 2 x t3.medium EC2 instances: the machines where our pods will run
- maxSize 3, so the group can grow by one node if needed

The same file, with placeholders, is in 04-code/eks/cluster.yaml.

## Step 5: Create the cluster in the background

```bash
nohup eksctl create cluster -f cluster.yaml > eks-create.log 2>&1 &
tail -f eks-create.log
```

This takes 15 to 20 minutes. eksctl creates CloudFormation stacks: first the control plane, then the node group. Press Ctrl+C to stop watching the log. That does not stop eksctl.

| Part of the command | What it does |
|---|---|
| nohup ... & | Runs eksctl in the background, and keeps it running even if your SSH session closes |
| > eks-create.log 2>&1 | Sends all output, including errors, to a log file |
| tail -f eks-create.log | Shows the log live. If you reconnect later, run it again |

Question: why not just run eksctl in the terminal?

If your SSH connection drops halfway, eksctl stops. AWS may finish the control plane, but the node group and your kubeconfig are never created. Then kubectl fails with "connection refused" on localhost:8080.

Tip: start the cluster early. Parts 04 to 07 do not need it, so you can build the service while the cluster comes up.

Concept: who can use this cluster? eksctl runs with the workstation IAM role, so that role becomes the cluster admin. eksctl also writes the kubeconfig file for you, so kubectl works straight away.

When it finishes, the last line is:

```
EKS cluster "triage-cluster" in "ap-south-1" region is ready
```

## Step 6: Check the cluster

```bash
kubectl get nodes
kubectl version
```

Expected: 2 nodes with STATUS Ready.

If kubectl says connection refused on localhost:8080, the cluster is not finished or eksctl stopped early. Check the end of eks-create.log.

Concept: kubectl and the cluster should be within one minor version of each other. We installed the newest kubectl, which can be several versions ahead of EKS. Install a kubectl that matches the server:

```bash
SERVER=$(kubectl version -o json | grep -o '"gitVersion": *"v[0-9.]*' | tail -1 | grep -o 'v[0-9.]*')
curl -sLO "https://dl.k8s.io/release/${SERVER}/bin/linux/amd64/kubectl"
sudo install -m 0755 kubectl /usr/local/bin/kubectl && rm kubectl
kubectl version
```

You can also see the cluster in the console: EKS, Clusters, triage-cluster, and the two nodes under EC2, Instances.

## What you built so far

- triage-vpc with two public subnets
- triage-workstation with Docker, Git, kubectl and eksctl, using an IAM role
- triage-cluster on Amazon EKS with 2 worker nodes

Next: Part 04, build the service.

## Stay connected

- YouTube: https://www.youtube.com/@BuildAutomateArchitect
- System Design playlist: https://www.youtube.com/playlist?list=PLeAHTLMwFYQ0
- Telegram: https://t.me/BuildAutomateArchitect
- Website: https://rahulchaubeyconsulting.com/
