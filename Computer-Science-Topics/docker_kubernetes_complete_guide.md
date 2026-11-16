# Complete Guide to Docker, Containers, and Kubernetes
## A Comprehensive Tutorial from First Principles

**Created for:** Shamit - MS ECE student at University of Florida  
**Date:** January 30, 2026  
**Topic:** Complete walkthrough of Docker, containers, kernel concepts, and Kubernetes

---

## Table of Contents

1. [Introduction & Problem Statement](#1-introduction--problem-statement)
2. [Docker & Containerization Basics](#2-docker--containerization-basics)
3. [Understanding Runtime, Kernel, and Namespaces](#3-understanding-runtime-kernel-and-namespaces)
4. [How Different OS Work on Same Kernel](#4-how-different-os-work-on-same-kernel)
5. [Images vs Containers](#5-images-vs-containers)
6. [Data Persistence in Containers](#6-data-persistence-in-containers)
7. [Cross-Platform Containers (Windows vs Linux)](#7-cross-platform-containers)
8. [Kubernetes Overview](#8-kubernetes-overview)
9. [Practical Examples & Best Practices](#9-practical-examples--best-practices)
10. [Quick Reference Commands](#10-quick-reference-commands)

---

## 1. Introduction & Problem Statement

### The HiPerGator Conda Challenge

When running scripts on HiPerGator with conda environments:
- **Works on your account** but fails when shared
- User-specific paths (`/home/shamit/.conda/envs/`)
- Different system libraries across accounts
- Version mismatches (Python, CUDA, glibc)

**Example Failure:**
```
Your Setup:              Colleague's Setup:
Ubuntu 22.04            CentOS 7
glibc 2.35             glibc 2.17 ← TOO OLD
CUDA 11.8              CUDA 10.2  ← INCOMPATIBLE  
✓ Works                ✗ Fails
```

### The Docker Solution

Docker packages:
- Your code
- All dependencies
- Python interpreter
- System libraries
- OS files

Result: **Same environment everywhere**

---

## 2. Docker & Containerization Basics

### Core Concepts

**Image** = Blueprint/Template (read-only)
**Container** = Running instance of an image
**Dockerfile** = Recipe to build an image
**Registry** = Storage for images (Docker Hub)

### Example Dockerfile

```dockerfile
# Base image with CUDA
FROM nvidia/cuda:11.8.0-cudnn8-runtime-ubuntu22.04

WORKDIR /app

# Install Python
RUN apt-get update && apt-get install -y     python3.10     python3-pip     && rm -rf /var/lib/apt/lists/*

# Install Python packages
COPY requirements.txt .
RUN pip3 install --no-cache-dir -r requirements.txt

# Copy code
COPY . .

CMD ["python3", "train.py"]
```

### HiPerGator Workflow

**On HiPerGator (uses Singularity, not Docker directly):**

```bash
# Convert Docker image to Singularity
singularity pull ml-pipeline.sif docker://shamit/ml-pipeline:v1

# Run with SLURM
#!/bin/bash
#SBATCH --gpus=a100:1

module load singularity

singularity exec --nv ml-pipeline.sif     python3 train.py --data /blue/project/data
```

### Why Singularity on HiPerGator?

**Docker Security Issue:**
- Requires root daemon
- Users could access others' data
- Security risk on shared systems

**Singularity Solution:**
- Runs as your regular user
- No root daemon needed
- HPC-friendly (MPI, GPUs, InfiniBand)

---

## 3. Understanding Runtime, Kernel, and Namespaces

### What is "Runtime"?

**Runtime** = Complete execution environment

**Layers:**
```
Your Python Script       ← Top
    ↓
Python Packages (torch, numpy)
    ↓  
Python Interpreter (python3.10)
    ↓
System Libraries (libc, libcuda)
    ↓
Operating System (Ubuntu/CentOS)
    ↓
Kernel (Linux kernel)     ← Bottom
    ↓
Hardware (CPU, GPU, Disk)
```

**Conda:** Packages layers 1-2 (code + packages)  
**Docker:** Packages layers 1-5 (code + packages + Python + libs + OS)

### What is the Kernel?

**Kernel** = Core OS that directly controls hardware

Think of your quadruped robot project:
```cpp
// Your code
moveLeg(FRONT_LEFT, angle);

// Hardware only understands:
- GPIO voltage levels
- PWM duty cycles
- I2C bit sequences
```

**Someone translates between them!**

Similarly, the kernel translates between:
```python
# Your code
data = open('file.txt').read()

# Hardware operations:
- Move disk head to sector
- Read bytes via DMA
- Trigger interrupt
- Copy to memory buffer
```

### Kernel's Jobs

1. **Hardware Abstraction** - Talk to CPU, GPU, disk, network
2. **Resource Management** - Allocate CPU time, memory, I/O
3. **Process Scheduling** - Run 100 programs on 8 cores
4. **Security** - Enforce permissions, isolate processes

### Containers Share the Kernel

```
Virtual Machine (SLOW):
App → Guest Kernel → Hypervisor → Host Kernel → Hardware

Container (FAST):
App → Host Kernel → Hardware
```

**Same kernel, different isolated views (namespaces)**

### What is a Namespace?

**Namespace** = Isolated view of system resources

**Analogy:** VR goggles in the same room
- Same room (kernel)
- Each person sees different environment
- All controlled by same reality (kernel)

**Types:**

**1. PID Namespace** - Process isolation
```bash
# Outside container
$ ps aux
shamit  1234  python train.py
alice   9012  python her_job.py
bob     3456  matlab

# Inside container  
$ ps aux
root    1     python train.py  ← Only sees own processes
```

**2. Mount Namespace** - Filesystem isolation
```bash
# HiPerGator filesystem
/home/shamit/
/home/alice/  ← Alice's files
/home/bob/    ← Bob's files

# Container's view
/home/shamit/  ← Only your files visible
# Alice and Bob's files INVISIBLE
```

**3. Network Namespace** - Network isolation
- Separate IP addresses
- Isolated ports
- Independent routing

### What is Mounting?

**Mounting** = Making one location visible in another

**Without mounting:**
```bash
$ singularity exec image.sif ls /blue/project
Error: No such file or directory
```

**With mounting:**
```bash
$ singularity exec --bind /blue:/blue image.sif ls /blue/project
file1.txt  file2.txt  ← Now visible!
```

**Key:** No copying! Same file, just visible from container.

```python
# Inside container
with open('/blue/project/results.txt', 'w') as f:
    f.write('data')

# Outside container (after exit)
$ cat /blue/project/results.txt
data  ← Still there!
```

### Container = Isolated View

```
Container Filesystem:
/
├── bin/      ← From image (container's files)
├── lib/      ← From image  
├── app/      ← From image (your code)
├── blue/     ← Mounted from HiPerGator ✓
└── home/shamit/  ← Mounted from HiPerGator ✓

Alice's /home/alice/ → INVISIBLE
Bob's files → INVISIBLE
```

---

## 4. How Different OS Work on Same Kernel

### The Big Reveal

**"Ubuntu" is actually TWO things:**

1. **Linux Kernel** (talks to hardware)
2. **Ubuntu Userspace** (bash, apt, libraries, utilities)

**Containers only include the userspace!**

```
Ubuntu Container:
┌──────────────────────┐
│ Ubuntu Userspace     │
│ - /bin/bash          │
│ - /usr/bin/apt       │
│ - /lib/libc.so.6     │
└──────────────────────┘
        ↓ uses
  Host's Linux Kernel

CentOS Container:
┌──────────────────────┐
│ CentOS Userspace     │
│ - /bin/bash          │
│ - /usr/bin/yum       │
│ - /lib64/libc.so.6   │
└──────────────────────┘
        ↓ uses
  SAME Linux Kernel!
```

### The Syscall Interface

All Linux programs talk to kernel via **system calls (syscalls)**:

```c
// Ubuntu's libc
FILE* fopen(path, mode) {
    // Ubuntu-specific code
    // ...
    syscall(SYS_open, path, flags);  ← Standard syscall
}

// CentOS's libc  
FILE* fopen(path, mode) {
    // CentOS-specific code
    // ...
    syscall(SYS_open, path, flags);  ← SAME syscall!
}
```

**Both call the same kernel syscall!**

```
SYS_read = 0
SYS_write = 1  
SYS_open = 2
SYS_close = 3
... (~300 total)
```

### Complete Flow Example

```python
# Python in Ubuntu container
with open('/data/file.txt', 'r') as f:
    data = f.read()
```

**Journey:**
```
1. Python interpreter (Ubuntu's)
2. Calls Python's open()
3. Python calls libc's fopen()
4. Ubuntu's libc calls: syscall(SYS_open, "/data/file.txt", O_RDONLY)
5. CPU switches to kernel mode
6. HiPerGator's kernel (might be CentOS-based!)
7. Kernel: "Syscall #2? That's open(). I'll open the file."
8. Returns file descriptor
9. Back to Ubuntu's libc
10. Back to Python
11. Data returned
```

**Kernel doesn't care it's Ubuntu userspace!**

### What's Actually Different?

**Ubuntu container:**
```
/bin/bash              (Ubuntu's version)
/usr/bin/apt           (package manager)
/lib/x86_64-linux-gnu/libc.so.6  (glibc 2.35)
/etc/os-release        (says "Ubuntu")
```

**CentOS container:**
```
/bin/bash              (CentOS's version)
/usr/bin/yum           (package manager)
/lib64/libc.so.6       (glibc 2.28)
/etc/os-release        (says "CentOS")
```

**Different files, but all make same syscalls!**

### Conda vs Docker

**Conda:**
```
"Here's a recipe - cook it with your kitchen"
Different kitchens → Different results
Missing ingredients → Fails
```

**Docker:**
```
"Here's a complete meal in a container"
Just heat it anywhere
Self-contained ✓
```

---

## 5. Images vs Containers

### Class vs Object Analogy

```python
# Image = Class
class PythonEnv:
    def __init__(self):
        self.os = "Ubuntu 22.04"
        self.python = "3.10"
        self.packages = ["torch", "numpy"]

# Container = Instance
container1 = PythonEnv()  # Instance 1
container2 = PythonEnv()  # Instance 2
container3 = PythonEnv()  # Instance 3

# Same class, independent instances
```

### Technical Differences

| Aspect | Image | Container |
|--------|-------|-----------|
| State | Static, read-only | Dynamic, running |
| Filesystem | Immutable layers | Image + writable layer |
| Processes | None | Has running processes |
| Lifespan | Permanent | Temporary |
| Count | One template | Many instances |

### Lifecycle

```bash
# 1. BUILD IMAGE
$ docker build -t myapp:v1 .
Image created: 300 MB file

# 2. RUN CONTAINER (instance 1)
$ docker run -d myapp:v1
Container abc123 created and running

# 3. RUN MORE CONTAINERS
$ docker run -d myapp:v1
Container def456 created

$ docker run -d myapp:v1
Container ghi789 created

# Same image → 3 independent containers

# 4. STOP CONTAINERS
$ docker stop abc123 def456 ghi789
Containers stopped (but exist)

# 5. REMOVE CONTAINERS
$ docker rm abc123 def456 ghi789
Containers deleted, image remains

# 6. REMOVE IMAGE
$ docker rmi myapp:v1
Everything gone
```

### What is "Building"?

**Building** = Creating the layered filesystem

```dockerfile
FROM ubuntu:22.04        # Layer 1: Ubuntu base (80 MB)
RUN apt-get install python  # Layer 2: +Python (200 MB)
COPY requirements.txt .     # Layer 3: +requirements (1 KB)
RUN pip install -r requirements.txt  # Layer 4: +packages (180 MB)
COPY code.py .             # Layer 5: +code (40 MB)
```

**Result:** 501 MB image file (all layers stacked)

### What is "Executing"?

```bash
$ singularity exec image.sif python train.py
```

**What happens:**
```
1. Read image.sif from disk
2. Create new namespace
3. Mount image filesystem (read-only)
4. Mount HiPerGator dirs (/home, /blue)
5. Create writable layer (/tmp)
6. Run python train.py
7. Process completes
8. Destroy namespace & writable layer
9. Mounted dirs persist ✓
```

### Copy-on-Write Efficiency

**Naive (wasteful):**
```
Image: 3 GB
Container 1: Full copy (3 GB)
Container 2: Full copy (3 GB)
Container 3: Full copy (3 GB)
Total: 9 GB ✗
```

**Actual (efficient):**
```
Image: 3 GB (shared, read-only)
Container 1: Changes only (10 MB)
Container 2: Changes only (15 MB)
Container 3: Changes only (8 MB)
Total: 3.033 GB ✓
```

---

## 6. Data Persistence in Containers

### The Critical Rule

**Writable layer = TEMPORARY (destroyed when container stops)**  
**Mounted directories = PERSISTENT (on host filesystem)**

### What Gets Destroyed vs Persists

```python
# Inside container

# ✗ LOST FOREVER
with open('/tmp/cache.txt', 'w') as f:
    f.write('temp data')

with open('/app/results.txt', 'w') as f:
    f.write('results')

# ✓ PERSISTS
with open('/blue/project/model.pth', 'wb') as f:
    torch.save(model, f)

with open('/home/shamit/output.csv', 'w') as f:
    f.write('final results')
```

**After container exits:**
```bash
$ cat /tmp/cache.txt
Error: No such file ✗

$ cat /app/results.txt  
Error: No such file ✗

$ cat /blue/project/model.pth
[Binary data] ✓ Still there!

$ cat /home/shamit/output.csv
final results ✓ Still there!
```

### Proper SLURM Script

```bash
#!/bin/bash
#SBATCH --job-name=training
#SBATCH --gpus=a100:1

module load singularity

DATA_DIR=/blue/shamit/datasets
OUTPUT_DIR=/blue/shamit/results

singularity exec     --nv     --bind ${DATA_DIR}:/data     --bind ${OUTPUT_DIR}:/output     pytorch.sif     python train.py         --data /data/train.csv         --output /output/model.pth

# Results saved to /blue/shamit/results/model.pth ✓
```

### Singularity Auto-Mounts

Singularity automatically mounts (Docker doesn't!):
- `/home/$USER` (your home directory)
- `$PWD` (current directory)
- `/tmp`, `/proc`, `/sys`, `/dev`

**NOT auto-mounted:**
- `/blue/` (must use --bind)
- `/orange/` (must use --bind)

---

## 7. Cross-Platform Containers

### The Fundamental Incompatibility

**Windows containers CANNOT run on Linux kernel!**

**Linux syscalls:**
```c
syscall(SYS_open, "/file.txt", O_RDONLY);  // Syscall #2
syscall(SYS_read, fd, buffer, size);       // Syscall #0
```

**Windows syscalls (completely different!):**
```c
NtOpenFile(&handle, access, ...);
NtReadFile(handle, event, ...);
```

**Incompatible!**

```
Windows binary:
├── cmd.exe (PE/COFF format)
├── kernel32.dll
└── Calls: NtOpenFile() ← Linux kernel doesn't understand!

Linux binary:
├── bash (ELF format)
├── libc.so
└── Calls: open() ← Works on Linux kernel ✓
```

### Docker Desktop's Secret

**On Windows/Mac, Docker Desktop runs a hidden Linux VM:**

```
Windows Laptop:
┌────────────────────────┐
│ Windows 11             │
│                        │
│ ┌────────────────────┐ │
│ │ Linux VM (WSL2)    │ │
│ │ Linux Kernel       │ │
│ │ ┌────────────────┐ │ │
│ │ │Linux Container│  │ │
│ │ └────────────────┘ │ │
│ └────────────────────┘ │
│                        │
│ Windows Container      │
│ (runs on NT kernel)    │
└────────────────────────┘
```

**Your Workflow:**
```
You (Windows):
Build Linux image → Sent to Linux VM → Stored in VM

Friend (Mac):
Pull your image → Mac's Linux VM → Runs identically

HiPerGator (Linux):
Pull your image → Native Linux → Runs natively (fastest!)
```

### Platform Detection

```bash
# Multi-platform images
docker pull python:3.10

# Docker checks your platform:
Linux/amd64 → Downloads Linux version
Windows/amd64 → Downloads Windows version
```

### HiPerGator = Linux Only

```
HiPerGator can run:
✓ Ubuntu containers
✓ CentOS containers
✓ Alpine containers
✓ Any Linux containers

Cannot run:
✗ Windows containers
✗ macOS containers
```

---

## 8. Kubernetes Overview

### What Problem Does It Solve?

**SLURM** = Batch jobs (run and complete)  
**Kubernetes** = Long-running services (web APIs, databases)

**Challenges Kubernetes Solves:**
1. Auto-restart crashed containers
2. Auto-scale based on load (1→100 replicas)
3. Load balance across replicas
4. Zero-downtime rolling updates
5. Health monitoring
6. Service discovery
7. Resource limits

### Core Concepts

**1. Cluster** = Group of machines
```
Control Plane (brain)
├── API Server
├── Scheduler  
├── Controller Manager
└── etcd (database)

Worker Nodes (muscle)
├── Node 1 (8 CPU, 32GB RAM, 2 GPU)
├── Node 2 (8 CPU, 32GB RAM, 2 GPU)
└── Node 3 (8 CPU, 32GB RAM, 2 GPU)
```

**2. Pod** = One or more containers
```
Pod:
├── Container 1: App server
├── Container 2: Logging sidecar
├── Shared network (same IP)
└── Shared volumes
```

**3. Deployment** = Manages multiple Pods
```yaml
replicas: 5  # Run 5 identical Pods

Kubernetes ensures:
- Always 5 running
- Restarts failures
- Distributes across nodes
```

**4. Service** = Stable network endpoint
```
Service IP: 10.0.2.100 (never changes)
    ↓ Load balances to:
├── Pod 1: 10.0.1.5
├── Pod 2: 10.0.1.6
├── Pod 3: 10.0.1.7
├── Pod 4: 10.0.1.8
└── Pod 5: 10.0.1.9
```

### Example: ML Model API

**Deployment:**
```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: model-server
spec:
  replicas: 10
  template:
    spec:
      containers:
      - name: server
        image: shamit/model-server:v1
        resources:
          requests:
            nvidia.com/gpu: "1"
        livenessProbe:
          httpGet:
            path: /health
            port: 5000
```

**Service:**
```yaml
apiVersion: v1
kind: Service
metadata:
  name: model-service
spec:
  type: LoadBalancer
  ports:
  - port: 80
    targetPort: 5000
  selector:
    app: model-server
```

**What Kubernetes Does:**
```
1. Creates 10 Pods across cluster
2. Assigns 1 GPU to each
3. Monitors health every 10s
4. Restarts unhealthy Pods
5. Load balances traffic
6. Scales automatically (optional)
7. Rolling updates with zero downtime
```

### Auto-Scaling

```yaml
apiVersion: autoscaling/v2
kind: HorizontalPodAutoscaler
spec:
  minReplicas: 10
  maxReplicas: 50
  metrics:
  - type: Resource
    resource:
      name: cpu
      target:
        averageUtilization: 70
```

**Behavior:**
```
Traffic surge → CPU at 85% → Scale to 15 Pods
Still high → Scale to 20 Pods
Stabilizes at 68% → Done

Traffic drops → CPU at 40% → Scale down to 12 Pods
```

### Rolling Updates

```bash
# Update to new model version
kubectl set image deployment/model-server   server=shamit/model-server:v2
```

**Process:**
```
Start: 10 Pods running v1

Step 1: Create 1 Pod with v2
Step 2: Wait for health check
Step 3: Add to load balancer
Step 4: Remove 1 Pod with v1
Repeat...

End: 10 Pods running v2

Zero downtime! ✓
```

### Kubernetes vs SLURM

| Feature | SLURM | Kubernetes |
|---------|-------|------------|
| Use case | Batch jobs | Services |
| Lifecycle | Run→Complete | Always running |
| Restart | Manual | Automatic |
| Scaling | Manual | Automatic |
| Load balancing | No | Yes |
| Health checks | Basic | Advanced |
| Updates | Resubmit | Rolling |

---

## 9. Practical Examples & Best Practices

### Example 1: Medical Imaging Pipeline

```dockerfile
FROM pytorch/pytorch:2.0.1-cuda11.7-cudnn8-runtime

WORKDIR /workspace

RUN pip install --no-cache-dir     monai==1.2.0     SimpleITK==2.2.1     nibabel==5.1.0

COPY models/ /workspace/models/
COPY process.py .

CMD ["python", "process.py"]
```

**SLURM script:**
```bash
#!/bin/bash
#SBATCH --gpus=a100:2
#SBATCH --mem=64gb

module load singularity

singularity exec     --nv     --bind /blue/cmil/datasets:/data     --bind /blue/cmil/results:/output     medical-imaging.sif     python process.py         --input /data/mri_scans         --output /output/segmentations         --batch-size 16
```

### Best Practices

**1. Keep images small:**
```dockerfile
# Good: Single layer, clean cache
RUN apt-get update && apt-get install -y     python3     git     && rm -rf /var/lib/apt/lists/*
```

**2. Use .dockerignore:**
```
.git
*.pyc
__pycache__
.venv
*.log
```

**3. Version everything:**
```dockerfile
FROM python:3.10.12
RUN pip install torch==2.0.1 numpy==1.24.3
```

**4. Don't run as root:**
```dockerfile
RUN useradd -m appuser
USER appuser
```

**5. Multi-stage builds:**
```dockerfile
# Build stage
FROM python:3.10 AS builder
RUN pip install --user -r requirements.txt

# Runtime stage
FROM python:3.10-slim
COPY --from=builder /root/.local /root/.local
COPY . .
```

---

## 10. Quick Reference Commands

### Docker

```bash
# Build
docker build -t myimage:tag .

# Run
docker run myimage:tag
docker run -it myimage:tag bash  # Interactive
docker run -d myimage:tag  # Background
docker run --rm myimage:tag  # Auto-remove
docker run -v /host:/container myimage:tag  # Mount
docker run -p 8080:80 myimage:tag  # Port
docker run --gpus all myimage:tag  # GPU

# Manage
docker ps  # Running containers
docker ps -a  # All containers
docker images  # List images
docker logs container_id
docker exec -it container_id bash
docker stop container_id
docker rm container_id
docker rmi image:tag

# Cleanup
docker system prune
```

### Singularity

```bash
# Build
singularity pull image.sif docker://user/repo:tag
singularity build image.sif Singularity.def

# Run  
singularity exec image.sif command
singularity exec --nv image.sif command  # GPU
singularity exec --bind /host:/container image.sif command
singularity shell image.sif  # Interactive

# Inspect
singularity inspect image.sif
```

### Kubernetes

```bash
# Deploy
kubectl apply -f config.yaml

# Get
kubectl get pods
kubectl get deployments
kubectl get services

# Logs
kubectl logs pod-name
kubectl logs -f pod-name  # Follow

# Execute
kubectl exec -it pod-name -- bash

# Scale
kubectl scale deployment name --replicas=5

# Update
kubectl set image deployment/name container=image:tag
kubectl rollout status deployment/name
kubectl rollout undo deployment/name  # Rollback

# Delete
kubectl delete pod pod-name
kubectl delete deployment name
```

---

## Key Takeaways

1. **Containers package everything:** code + dependencies + OS libraries (not kernel)
2. **Images are blueprints, containers are instances** (class vs object)
3. **Always mount external storage** for persistent results
4. **Different OS userspace works on same kernel** via syscalls
5. **Singularity = Docker for HPC** (no root, user-friendly)
6. **Kubernetes orchestrates** containers for production services

---

## Next Steps

1. **Practice:** Convert one HiPerGator script to Docker
2. **Build:** Create a Dockerfile for your ML pipeline
3. **Test:** Run on HiPerGator with Singularity
4. **Share:** Push image to Docker Hub for reproducibility
5. **Advanced:** Explore Kubernetes for deploying models

---

## Resources

- Docker Docs: https://docs.docker.com
- Singularity Docs: https://sylabs.io/docs/
- Kubernetes Docs: https://kubernetes.io/docs/
- HiPerGator Containers: https://help.rc.ufl.edu/doc/Singularity

---

**End of Guide**

*This document contains the complete conversation covering Docker fundamentals, kernel concepts, containerization theory, and Kubernetes orchestration from first principles.*
