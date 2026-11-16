# Comprehensive Kubernetes Guide

## Table of Contents
1. [What is Kubernetes](#what-is-kubernetes)
2. [Core Concepts & Architecture](#core-concepts--architecture)
3. [Key Resources/Objects](#key-resourcesobjects)
4. [Essential kubectl Commands](#essential-kubectl-commands)
5. [YAML Manifests](#yaml-manifests)
6. [Networking](#networking)
7. [Scaling & Self-Healing](#scaling--self-healing)
8. [Real-World Patterns](#real-world-patterns)
9. [Best Practices](#best-practices)
10. [Common Troubleshooting](#common-troubleshooting)

---

## What is Kubernetes

### Overview
Kubernetes (K8s) is an open-source container orchestration platform originally developed by Google. It automates the deployment, scaling, and management of containerized applications across clusters of machines.

### Problems It Solves

**Before Kubernetes:**
- Manual deployment of containers across multiple servers
- No automated failover when containers crash
- Difficult to scale applications up or down
- Complex networking between containers on different hosts
- No standardized way to manage configuration and secrets
- Resource utilization inefficiencies

**With Kubernetes:**
- **Automated Deployment**: Deploy applications declaratively with desired state
- **Self-Healing**: Automatically restarts failed containers, replaces nodes
- **Horizontal Scaling**: Scale applications up/down automatically or manually
- **Service Discovery & Load Balancing**: Built-in DNS and load balancing
- **Rolling Updates & Rollbacks**: Zero-downtime deployments
- **Resource Optimization**: Efficient bin-packing based on resource requirements
- **Configuration Management**: Centralized config and secrets management
- **Storage Orchestration**: Automatically mount storage systems

### When to Use Kubernetes

**Good Use Cases:**
- Microservices architectures
- Applications requiring high availability
- Workloads that need auto-scaling
- Multi-cloud or hybrid cloud deployments
- Teams practicing DevOps/GitOps

**May Be Overkill For:**
- Simple single-server applications
- Small teams with basic deployment needs
- Monolithic applications without scaling requirements

---

## Core Concepts & Architecture

### High-Level Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                      KUBERNETES CLUSTER                      │
├─────────────────────────────────────────────────────────────┤
│                                                               │
│  ┌──────────────────────────────────────────────────────┐   │
│  │              CONTROL PLANE (Master)                  │   │
│  ├──────────────────────────────────────────────────────┤   │
│  │  ┌──────────┐  ┌──────┐  ┌───────────┐  ┌─────────┐│   │
│  │  │   API    │  │ etcd │  │ Scheduler │  │Controller││   │
│  │  │  Server  │  │      │  │           │  │ Manager  ││   │
│  │  └──────────┘  └──────┘  └───────────┘  └─────────┘│   │
│  └──────────────────────────────────────────────────────┘   │
│                           │                                   │
│                           │ (manages)                         │
│                           ▼                                   │
│  ┌────────────────────────────────────────────────────────┐ │
│  │                    WORKER NODES                        │ │
│  ├────────────────────────────────────────────────────────┤ │
│  │  ┌──────────────┐    ┌──────────────┐   ┌──────────┐ │ │
│  │  │   Node 1     │    │   Node 2     │   │  Node N  │ │ │
│  │  ├──────────────┤    ├──────────────┤   ├──────────┤ │ │
│  │  │ kubelet      │    │ kubelet      │   │ kubelet  │ │ │
│  │  │ kube-proxy   │    │ kube-proxy   │   │kube-proxy│ │ │
│  │  │ runtime      │    │ runtime      │   │ runtime  │ │ │
│  │  ├──────────────┤    ├──────────────┤   ├──────────┤ │ │
│  │  │  ┌────┐      │    │  ┌────┐      │   │ ┌────┐  │ │ │
│  │  │  │Pod1│ ┌──┐ │    │  │Pod3│      │   │ │Pod5│  │ │ │
│  │  │  └────┘ │P2│ │    │  └────┘ ┌──┐ │   │ └────┘  │ │ │
│  │  │         └──┘ │    │         │P4│ │   │         │ │ │
│  │  │              │    │         └──┘ │   │         │ │ │
│  │  └──────────────┘    └──────────────┘   └──────────┘ │ │
│  └────────────────────────────────────────────────────────┘ │
└─────────────────────────────────────────────────────────────┘
```

### Control Plane Components

#### 1. API Server (kube-apiserver)
- **Role**: Front-end for the Kubernetes control plane
- **Functions**:
  - Exposes the Kubernetes API (RESTful interface)
  - All components communicate through it
  - Authentication, authorization, admission control
  - Validates and processes API requests
- **Analogy**: The "reception desk" of Kubernetes

#### 2. etcd
- **Role**: Distributed key-value store
- **Functions**:
  - Stores all cluster data (configuration, state, metadata)
  - Single source of truth for the cluster
  - Provides consistency and high availability
- **Important**: If etcd is lost, the entire cluster state is lost
- **Analogy**: The "database" of Kubernetes

#### 3. Scheduler (kube-scheduler)
- **Role**: Assigns Pods to Nodes
- **Functions**:
  - Watches for newly created Pods with no assigned node
  - Selects optimal node based on:
    - Resource requirements (CPU, memory)
    - Hardware/software/policy constraints
    - Affinity/anti-affinity specifications
    - Data locality
- **Analogy**: The "HR manager" placing employees in offices

#### 4. Controller Manager (kube-controller-manager)
- **Role**: Runs controller processes
- **Functions**:
  - Node Controller: Monitors node health
  - Replication Controller: Maintains correct number of pods
  - Endpoints Controller: Populates endpoint objects
  - Service Account Controller: Creates default accounts
- **Analogy**: The "manager" ensuring desired state matches actual state

#### 5. Cloud Controller Manager
- **Role**: Integrates with cloud provider APIs
- **Functions**:
  - Node management (cloud-specific)
  - Route management
  - Load balancer management
  - Volume management

### Node Components

#### 1. kubelet
- **Role**: Agent running on each node
- **Functions**:
  - Registers node with API server
  - Watches for Pod assignments to its node
  - Ensures containers described in PodSpecs are running and healthy
  - Reports node and pod status back to control plane
  - Executes liveness/readiness probes
- **Analogy**: The "site manager" at each location

#### 2. kube-proxy
- **Role**: Network proxy running on each node
- **Functions**:
  - Maintains network rules for Pod communication
  - Implements Service abstraction
  - Handles load balancing across Pod replicas
  - Can use iptables, IPVS, or userspace mode
- **Analogy**: The "receptionist" routing calls to the right extension

#### 3. Container Runtime
- **Role**: Software responsible for running containers
- **Examples**:
  - containerd (most common)
  - CRI-O
  - Docker (via dockershim, deprecated in 1.24+)
- **Functions**:
  - Pulling images from registries
  - Running containers
  - Managing container lifecycle

### Fundamental Abstractions

#### Cluster
- A set of machines (nodes) running containerized applications
- Consists of at least one control plane and one or more worker nodes

#### Node
- A worker machine in Kubernetes (VM or physical)
- Each node contains the services necessary to run Pods
- Managed by the control plane

#### Pod
- **The smallest deployable unit in Kubernetes**
- Represents a single instance of a running process
- Can contain one or more containers (usually one)
- Containers in a Pod:
  - Share network namespace (same IP address)
  - Share storage volumes
  - Are scheduled together on the same node
  - Have a shared lifecycle

```
┌─────────────────────────────────┐
│           POD                   │
├─────────────────────────────────┤
│  IP: 10.244.1.5                 │
│                                 │
│  ┌──────────────────────────┐  │
│  │   Main Container         │  │
│  │   (nginx:1.19)           │  │
│  └──────────────────────────┘  │
│                                 │
│  ┌──────────────────────────┐  │
│  │   Sidecar Container      │  │
│  │   (log-collector)        │  │
│  └──────────────────────────┘  │
│                                 │
│  Shared Volumes: [logs, data]  │
└─────────────────────────────────┘
```

---

## Key Resources/Objects

### 1. Pods

#### What Are Pods?
Pods are the atomic unit of scheduling in Kubernetes. They represent one or more tightly coupled containers that should run together.

#### When to Use Multiple Containers in a Pod
- Sidecar pattern (logging, monitoring)
- Ambassador pattern (proxy)
- Adapter pattern (normalize output)

#### Pod Lifecycle States
- **Pending**: Pod accepted but container(s) not created yet
- **Running**: At least one container is running
- **Succeeded**: All containers terminated successfully
- **Failed**: All containers terminated, at least one failed
- **Unknown**: Pod state cannot be determined

#### Example Pod YAML

```yaml
apiVersion: v1
kind: Pod
metadata:
  name: nginx-pod
  labels:
    app: nginx
    environment: production
spec:
  containers:
  - name: nginx
    image: nginx:1.21
    ports:
    - containerPort: 80
    resources:
      requests:
        memory: "64Mi"
        cpu: "250m"
      limits:
        memory: "128Mi"
        cpu: "500m"
    env:
    - name: ENVIRONMENT
      value: "production"
```

### 2. Deployments

#### What Are Deployments?
Deployments provide declarative updates for Pods and ReplicaSets. They are the standard way to deploy stateless applications.

#### Key Features
- **Replica Management**: Ensures specified number of pod replicas running
- **Rolling Updates**: Gradual update with zero downtime
- **Rollback**: Easy revert to previous versions
- **Scaling**: Scale replicas up or down
- **Self-Healing**: Automatically replaces failed pods

#### Deployment Strategy Types
1. **RollingUpdate** (default): Gradually replaces old pods with new ones
2. **Recreate**: Terminates all old pods before creating new ones

#### Example Deployment

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: nginx-deployment
  labels:
    app: nginx
spec:
  replicas: 3
  strategy:
    type: RollingUpdate
    rollingUpdate:
      maxSurge: 1        # Max pods above desired count during update
      maxUnavailable: 1   # Max pods unavailable during update
  selector:
    matchLabels:
      app: nginx
  template:
    metadata:
      labels:
        app: nginx
    spec:
      containers:
      - name: nginx
        image: nginx:1.21
        ports:
        - containerPort: 80
        resources:
          requests:
            memory: "64Mi"
            cpu: "250m"
          limits:
            memory: "128Mi"
            cpu: "500m"
        livenessProbe:
          httpGet:
            path: /
            port: 80
          initialDelaySeconds: 30
          periodSeconds: 10
        readinessProbe:
          httpGet:
            path: /
            port: 80
          initialDelaySeconds: 5
          periodSeconds: 5
```

#### Deployment Workflow

```
User creates Deployment
        ↓
Deployment creates ReplicaSet
        ↓
ReplicaSet creates Pods
        ↓
Scheduler assigns Pods to Nodes
        ↓
kubelet starts containers
```

### 3. Services

#### What Are Services?
Services provide a stable network endpoint to access a set of Pods. Since Pods are ephemeral and their IPs change, Services provide consistent access.

#### Service Types

##### ClusterIP (Default)
- Exposes service on a cluster-internal IP
- Only accessible within the cluster
- Use for internal microservice communication

```yaml
apiVersion: v1
kind: Service
metadata:
  name: backend-service
spec:
  type: ClusterIP
  selector:
    app: backend
  ports:
  - protocol: TCP
    port: 80        # Service port
    targetPort: 8080  # Container port
```

##### NodePort
- Exposes service on each Node's IP at a static port
- Accessible from outside cluster via `<NodeIP>:<NodePort>`
- Port range: 30000-32767

```yaml
apiVersion: v1
kind: Service
metadata:
  name: frontend-service
spec:
  type: NodePort
  selector:
    app: frontend
  ports:
  - protocol: TCP
    port: 80
    targetPort: 8080
    nodePort: 30080  # Optional, K8s assigns if not specified
```

##### LoadBalancer
- Exposes service externally using cloud provider's load balancer
- Automatically creates NodePort and ClusterIP services
- Only works on cloud platforms (AWS, GCP, Azure)

```yaml
apiVersion: v1
kind: Service
metadata:
  name: web-service
spec:
  type: LoadBalancer
  selector:
    app: web
  ports:
  - protocol: TCP
    port: 80
    targetPort: 8080
```

##### ExternalName
- Maps service to a DNS name
- No proxying, returns CNAME record
- Use for accessing external services

```yaml
apiVersion: v1
kind: Service
metadata:
  name: external-database
spec:
  type: ExternalName
  externalName: db.example.com
```

#### Service Discovery Flow

```
┌──────────┐        ┌─────────────┐        ┌──────────┐
│  Client  │───────>│   Service   │───────>│  Pod 1   │
│   Pod    │        │ (ClusterIP) │        ├──────────┤
└──────────┘        └─────────────┘    ┌──>│  Pod 2   │
                           │            │   ├──────────┤
                           └────────────┘   │  Pod 3   │
                      (Load balances)       └──────────┘
```

### 4. ConfigMaps and Secrets

#### ConfigMaps
Store non-sensitive configuration data as key-value pairs.

**Use Cases:**
- Application configuration files
- Command-line arguments
- Environment variables
- Configuration data

```yaml
apiVersion: v1
kind: ConfigMap
metadata:
  name: app-config
data:
  # Simple key-value
  database_url: "postgres://db:5432/myapp"
  log_level: "info"

  # File-like content
  app.properties: |
    server.port=8080
    server.host=0.0.0.0
    cache.enabled=true
```

**Using ConfigMap in Pod:**

```yaml
apiVersion: v1
kind: Pod
metadata:
  name: app-pod
spec:
  containers:
  - name: app
    image: myapp:1.0

    # As environment variables
    env:
    - name: DATABASE_URL
      valueFrom:
        configMapKeyRef:
          name: app-config
          key: database_url

    # As volume mount
    volumeMounts:
    - name: config-volume
      mountPath: /etc/config

  volumes:
  - name: config-volume
    configMap:
      name: app-config
```

#### Secrets
Store sensitive data (passwords, tokens, keys) in base64-encoded format.

**Types:**
- **Opaque**: Arbitrary user-defined data (default)
- **kubernetes.io/service-account-token**: Service account token
- **kubernetes.io/dockerconfigjson**: Docker registry credentials
- **kubernetes.io/tls**: TLS certificate and key

```yaml
apiVersion: v1
kind: Secret
metadata:
  name: db-credentials
type: Opaque
data:
  # Base64 encoded values
  username: YWRtaW4=        # "admin"
  password: cGFzc3dvcmQxMjM= # "password123"
stringData:
  # Plain text (K8s will encode)
  connection-string: "postgres://admin:password123@db:5432"
```

**Using Secret in Pod:**

```yaml
apiVersion: v1
kind: Pod
metadata:
  name: app-pod
spec:
  containers:
  - name: app
    image: myapp:1.0
    env:
    - name: DB_USERNAME
      valueFrom:
        secretKeyRef:
          name: db-credentials
          key: username
    - name: DB_PASSWORD
      valueFrom:
        secretKeyRef:
          name: db-credentials
          key: password
```

**Creating Secrets from Command Line:**

```bash
# From literals
kubectl create secret generic db-creds \
  --from-literal=username=admin \
  --from-literal=password=secret123

# From files
kubectl create secret generic tls-cert \
  --from-file=tls.crt=path/to/cert.crt \
  --from-file=tls.key=path/to/key.key
```

### 5. Namespaces

#### What Are Namespaces?
Virtual clusters within a physical cluster. Provide scope for names and resource isolation.

#### Default Namespaces
- **default**: Default namespace for objects with no namespace
- **kube-system**: For Kubernetes system components
- **kube-public**: Readable by all, reserved for cluster usage
- **kube-node-lease**: For node heartbeat data

#### Use Cases
- Multi-tenancy (team1, team2)
- Environment separation (dev, staging, prod)
- Resource quotas per namespace
- Access control boundaries

```yaml
apiVersion: v1
kind: Namespace
metadata:
  name: development
  labels:
    environment: dev
```

**Using Namespaces:**

```bash
# Create resource in namespace
kubectl create -f deployment.yaml -n development

# Set default namespace for context
kubectl config set-context --current --namespace=development

# View resources across all namespaces
kubectl get pods --all-namespaces
```

**Resource Quota Example:**

```yaml
apiVersion: v1
kind: ResourceQuota
metadata:
  name: dev-quota
  namespace: development
spec:
  hard:
    requests.cpu: "10"
    requests.memory: 20Gi
    limits.cpu: "20"
    limits.memory: 40Gi
    pods: "50"
```

### 6. Volumes and Persistent Volumes

#### Volume Types Overview

**Ephemeral Volumes** (lifespan tied to Pod):
- `emptyDir`: Empty directory created when Pod starts
- `configMap`: Inject ConfigMap data
- `secret`: Inject Secret data

**Persistent Volumes** (lifespan independent of Pods):
- `hostPath`: Mount from node's filesystem
- `nfs`: Network File System
- `persistentVolumeClaim`: Claim a PersistentVolume
- Cloud-specific: `awsElasticBlockStore`, `gcePersistentDisk`, `azureDisk`

#### emptyDir Example

```yaml
apiVersion: v1
kind: Pod
metadata:
  name: cache-pod
spec:
  containers:
  - name: app
    image: myapp:1.0
    volumeMounts:
    - name: cache-volume
      mountPath: /cache

  - name: cache-cleaner
    image: busybox
    volumeMounts:
    - name: cache-volume
      mountPath: /cache
    command: ['sh', '-c', 'while true; do rm -rf /cache/*; sleep 3600; done']

  volumes:
  - name: cache-volume
    emptyDir: {}
```

#### Persistent Storage Architecture

```
┌──────────────────────────────────────────────────────┐
│                  Storage Classes                     │
│  (Define types: fast-ssd, slow-hdd, nfs-storage)    │
└──────────────────┬───────────────────────────────────┘
                   │
                   ▼
┌──────────────────────────────────────────────────────┐
│              Persistent Volumes (PV)                 │
│  (Actual storage resources provisioned by admin)    │
└──────────────────┬───────────────────────────────────┘
                   │
                   │ (bound to)
                   ▼
┌──────────────────────────────────────────────────────┐
│        Persistent Volume Claims (PVC)                │
│  (Request for storage by users/pods)                 │
└──────────────────┬───────────────────────────────────┘
                   │
                   │ (mounted by)
                   ▼
┌──────────────────────────────────────────────────────┐
│                    Pods                              │
└──────────────────────────────────────────────────────┘
```

#### PersistentVolume Example

```yaml
apiVersion: v1
kind: PersistentVolume
metadata:
  name: pv-storage
spec:
  capacity:
    storage: 10Gi
  accessModes:
  - ReadWriteOnce     # RWO: Single node read-write
  # - ReadOnlyMany    # ROX: Multiple nodes read-only
  # - ReadWriteMany   # RWX: Multiple nodes read-write
  persistentVolumeReclaimPolicy: Retain  # or Delete, Recycle
  storageClassName: fast-ssd
  hostPath:
    path: /mnt/data
```

#### PersistentVolumeClaim Example

```yaml
apiVersion: v1
kind: PersistentVolumeClaim
metadata:
  name: pvc-storage
spec:
  accessModes:
  - ReadWriteOnce
  resources:
    requests:
      storage: 5Gi
  storageClassName: fast-ssd
```

#### Using PVC in Pod

```yaml
apiVersion: v1
kind: Pod
metadata:
  name: database-pod
spec:
  containers:
  - name: postgres
    image: postgres:13
    volumeMounts:
    - name: postgres-storage
      mountPath: /var/lib/postgresql/data

  volumes:
  - name: postgres-storage
    persistentVolumeClaim:
      claimName: pvc-storage
```

#### StorageClass for Dynamic Provisioning

```yaml
apiVersion: storage.k8s.io/v1
kind: StorageClass
metadata:
  name: fast-ssd
provisioner: kubernetes.io/aws-ebs  # Cloud-specific
parameters:
  type: gp2
  fsType: ext4
reclaimPolicy: Delete
allowVolumeExpansion: true
```

### 7. Ingress

#### What Is Ingress?
Ingress manages external HTTP/HTTPS access to services in a cluster. It provides load balancing, SSL termination, and name-based virtual hosting.

#### Ingress vs Service

```
Without Ingress:
Internet → LoadBalancer Service → Pods
(One LoadBalancer per service = expensive)

With Ingress:
Internet → Ingress → Multiple Services → Pods
(One LoadBalancer for many services)
```

#### Ingress Controller
Ingress resources require an Ingress Controller to function (not included by default):
- **nginx-ingress**: Most popular
- **traefik**: Feature-rich, easy to use
- **HAProxy**: High performance
- **Cloud-specific**: AWS ALB, GCE

#### Basic Ingress Example

```yaml
apiVersion: networking.k8s.io/v1
kind: Ingress
metadata:
  name: app-ingress
  annotations:
    nginx.ingress.kubernetes.io/rewrite-target: /
spec:
  rules:
  - host: myapp.example.com
    http:
      paths:
      - path: /
        pathType: Prefix
        backend:
          service:
            name: frontend-service
            port:
              number: 80
      - path: /api
        pathType: Prefix
        backend:
          service:
            name: backend-service
            port:
              number: 8080
```

#### Ingress with TLS

```yaml
apiVersion: networking.k8s.io/v1
kind: Ingress
metadata:
  name: tls-ingress
spec:
  tls:
  - hosts:
    - secure.example.com
    secretName: tls-secret  # Contains tls.crt and tls.key
  rules:
  - host: secure.example.com
    http:
      paths:
      - path: /
        pathType: Prefix
        backend:
          service:
            name: web-service
            port:
              number: 443
```

#### Multiple Host Ingress

```yaml
apiVersion: networking.k8s.io/v1
kind: Ingress
metadata:
  name: multi-host-ingress
spec:
  rules:
  - host: app1.example.com
    http:
      paths:
      - path: /
        pathType: Prefix
        backend:
          service:
            name: app1-service
            port:
              number: 80
  - host: app2.example.com
    http:
      paths:
      - path: /
        pathType: Prefix
        backend:
          service:
            name: app2-service
            port:
              number: 80
```

---

## Essential kubectl Commands

### Cluster Information

```bash
# View cluster info
kubectl cluster-info

# View cluster nodes
kubectl get nodes

# Detailed node information
kubectl describe node <node-name>

# View node resource usage
kubectl top nodes
```

### Working with Pods

```bash
# List all pods
kubectl get pods

# List pods in all namespaces
kubectl get pods --all-namespaces
kubectl get pods -A

# List pods with more details
kubectl get pods -o wide

# Watch pods in real-time
kubectl get pods --watch

# Describe a pod (detailed info)
kubectl describe pod <pod-name>

# Get pod logs
kubectl logs <pod-name>

# Follow logs (tail -f style)
kubectl logs -f <pod-name>

# Logs from specific container in multi-container pod
kubectl logs <pod-name> -c <container-name>

# Previous container logs (if restarted)
kubectl logs <pod-name> --previous

# Execute command in pod
kubectl exec <pod-name> -- <command>

# Interactive shell in pod
kubectl exec -it <pod-name> -- /bin/bash

# Port forwarding to local machine
kubectl port-forward <pod-name> 8080:80
# Access via localhost:8080

# Copy files to/from pod
kubectl cp <pod-name>:/path/to/file ./local-file
kubectl cp ./local-file <pod-name>:/path/to/file

# Delete pod
kubectl delete pod <pod-name>

# Force delete (use with caution)
kubectl delete pod <pod-name> --force --grace-period=0
```

### Working with Deployments

```bash
# List deployments
kubectl get deployments

# Create deployment
kubectl create deployment nginx --image=nginx:1.21

# Create from YAML file
kubectl apply -f deployment.yaml

# Update deployment image
kubectl set image deployment/nginx nginx=nginx:1.22

# Scale deployment
kubectl scale deployment/nginx --replicas=5

# Autoscale deployment
kubectl autoscale deployment/nginx --min=2 --max=10 --cpu-percent=80

# View rollout status
kubectl rollout status deployment/nginx

# View rollout history
kubectl rollout history deployment/nginx

# Rollback to previous version
kubectl rollout undo deployment/nginx

# Rollback to specific revision
kubectl rollout undo deployment/nginx --to-revision=2

# Pause rollout
kubectl rollout pause deployment/nginx

# Resume rollout
kubectl rollout resume deployment/nginx

# Delete deployment
kubectl delete deployment nginx
```

### Working with Services

```bash
# List services
kubectl get services
kubectl get svc

# Describe service
kubectl describe svc <service-name>

# Create service (expose deployment)
kubectl expose deployment nginx --port=80 --type=NodePort

# Delete service
kubectl delete svc <service-name>
```

### Working with ConfigMaps and Secrets

```bash
# Create ConfigMap from literal
kubectl create configmap app-config \
  --from-literal=key1=value1 \
  --from-literal=key2=value2

# Create ConfigMap from file
kubectl create configmap app-config --from-file=config.properties

# Create ConfigMap from directory
kubectl create configmap app-config --from-file=./config-dir/

# View ConfigMap
kubectl get configmap app-config -o yaml

# Create Secret from literal
kubectl create secret generic db-creds \
  --from-literal=username=admin \
  --from-literal=password=secret123

# Create Secret from file
kubectl create secret generic tls-certs \
  --from-file=tls.crt=./cert.crt \
  --from-file=tls.key=./key.key

# View Secret (values are base64 encoded)
kubectl get secret db-creds -o yaml

# Decode secret value
kubectl get secret db-creds -o jsonpath='{.data.password}' | base64 -d
```

### Working with Namespaces

```bash
# List namespaces
kubectl get namespaces
kubectl get ns

# Create namespace
kubectl create namespace development

# Set default namespace for context
kubectl config set-context --current --namespace=development

# View current namespace
kubectl config view --minify | grep namespace:

# Delete namespace (deletes all resources in it)
kubectl delete namespace development
```

### Apply, Create, Delete Resources

```bash
# Apply configuration (create or update)
kubectl apply -f resource.yaml

# Apply all YAML files in directory
kubectl apply -f ./manifests/

# Create resource (fails if exists)
kubectl create -f resource.yaml

# Delete resource
kubectl delete -f resource.yaml

# Delete by resource type and name
kubectl delete pod <pod-name>
kubectl delete deployment <deployment-name>

# Delete all pods in namespace
kubectl delete pods --all

# Delete all resources with label
kubectl delete all -l app=myapp
```

### Labels and Selectors

```bash
# Show labels
kubectl get pods --show-labels

# Add label to pod
kubectl label pod <pod-name> environment=production

# Remove label
kubectl label pod <pod-name> environment-

# Select pods by label
kubectl get pods -l environment=production
kubectl get pods -l 'environment in (production,staging)'
kubectl get pods -l environment=production,tier=frontend

# Update label
kubectl label pod <pod-name> environment=staging --overwrite
```

### Resource Management

```bash
# View resource usage (requires metrics-server)
kubectl top nodes
kubectl top pods

# View resource usage for specific pod
kubectl top pod <pod-name>

# View resource quotas
kubectl get resourcequota

# View limit ranges
kubectl get limitrange
```

### Debugging and Troubleshooting

```bash
# Get events (cluster-wide)
kubectl get events

# Get events sorted by timestamp
kubectl get events --sort-by=.metadata.creationTimestamp

# Describe resource (shows events at bottom)
kubectl describe pod <pod-name>

# Run temporary debugging pod
kubectl run debug-pod --image=busybox --rm -it -- sh

# Check API resources available
kubectl api-resources

# Explain resource fields
kubectl explain pod
kubectl explain pod.spec.containers

# View cluster configuration
kubectl config view

# View current context
kubectl config current-context

# Switch context
kubectl config use-context <context-name>

# Dry-run (see what would be created)
kubectl apply -f deployment.yaml --dry-run=client

# Server-side dry-run (validates against API)
kubectl apply -f deployment.yaml --dry-run=server

# Diff before applying
kubectl diff -f deployment.yaml
```

### Output Formatting

```bash
# YAML output
kubectl get pod <pod-name> -o yaml

# JSON output
kubectl get pod <pod-name> -o json

# Custom columns
kubectl get pods -o custom-columns=NAME:.metadata.name,STATUS:.status.phase

# JSONPath
kubectl get pods -o jsonpath='{.items[*].metadata.name}'

# Wide output (more details)
kubectl get pods -o wide

# Get specific field
kubectl get pod <pod-name> -o jsonpath='{.spec.containers[0].image}'
```

### Useful Aliases

Add these to your `.bashrc` or `.zshrc`:

```bash
alias k='kubectl'
alias kgp='kubectl get pods'
alias kgs='kubectl get svc'
alias kgd='kubectl get deployments'
alias kdp='kubectl describe pod'
alias kds='kubectl describe svc'
alias kdd='kubectl describe deployment'
alias kl='kubectl logs'
alias klf='kubectl logs -f'
alias kex='kubectl exec -it'
alias kaf='kubectl apply -f'
alias kdel='kubectl delete'
alias kgpa='kubectl get pods --all-namespaces'
```

---

## YAML Manifests

### YAML Basics for Kubernetes

#### Structure
Every Kubernetes YAML has four required fields:

```yaml
apiVersion: <api-version>  # API version for the resource type
kind: <resource-type>       # Type of resource (Pod, Deployment, etc.)
metadata:                   # Data about the object
  name: <name>              # Unique name
  labels:                   # Key-value pairs for organization
    key: value
spec:                       # Desired state specification
  # Resource-specific configuration
```

### Common Fields Across Resources

#### metadata
```yaml
metadata:
  name: my-app              # Required: unique name
  namespace: production     # Optional: namespace (default: "default")
  labels:                   # Optional: organize and select resources
    app: myapp
    version: v1
    environment: prod
  annotations:              # Optional: non-identifying metadata
    description: "Main application deployment"
    contact: "team@example.com"
```

#### Labels Best Practices
```yaml
labels:
  app.kubernetes.io/name: myapp
  app.kubernetes.io/instance: myapp-prod
  app.kubernetes.io/version: "1.0.0"
  app.kubernetes.io/component: backend
  app.kubernetes.io/part-of: myapp-system
  app.kubernetes.io/managed-by: helm
```

### Complete Pod Manifest

```yaml
apiVersion: v1
kind: Pod
metadata:
  name: advanced-pod
  namespace: default
  labels:
    app: myapp
    tier: backend
  annotations:
    description: "Advanced pod example"
spec:
  # Restart policy: Always (default), OnFailure, Never
  restartPolicy: Always

  # Node selection
  nodeSelector:
    disktype: ssd

  # Containers
  containers:
  - name: main-app
    image: myapp:1.0
    imagePullPolicy: IfNotPresent  # Always, Never, IfNotPresent

    # Command and args override Docker CMD and ENTRYPOINT
    command: ["/bin/sh"]
    args: ["-c", "echo Hello && sleep 3600"]

    # Ports
    ports:
    - name: http
      containerPort: 8080
      protocol: TCP

    # Environment variables
    env:
    - name: DATABASE_HOST
      value: "postgres.default.svc.cluster.local"
    - name: DATABASE_USER
      valueFrom:
        secretKeyRef:
          name: db-credentials
          key: username
    - name: CONFIG_VALUE
      valueFrom:
        configMapKeyRef:
          name: app-config
          key: setting

    # Resource requests and limits
    resources:
      requests:
        memory: "128Mi"
        cpu: "250m"
      limits:
        memory: "256Mi"
        cpu: "500m"

    # Liveness probe (restart if fails)
    livenessProbe:
      httpGet:
        path: /healthz
        port: 8080
      initialDelaySeconds: 30
      periodSeconds: 10
      timeoutSeconds: 5
      failureThreshold: 3

    # Readiness probe (remove from service if fails)
    readinessProbe:
      httpGet:
        path: /ready
        port: 8080
      initialDelaySeconds: 5
      periodSeconds: 5

    # Volume mounts
    volumeMounts:
    - name: config-volume
      mountPath: /etc/config
      readOnly: true
    - name: data-volume
      mountPath: /data

  # Init containers (run before main containers)
  initContainers:
  - name: init-db
    image: busybox:1.28
    command: ['sh', '-c', 'until nslookup postgres; do sleep 2; done']

  # Volumes
  volumes:
  - name: config-volume
    configMap:
      name: app-config
  - name: data-volume
    emptyDir: {}

  # Image pull secrets (for private registries)
  imagePullSecrets:
  - name: regcred
```

### Complete Deployment Manifest

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: myapp-deployment
  namespace: production
  labels:
    app: myapp
spec:
  # Number of pod replicas
  replicas: 3

  # Label selector (must match template labels)
  selector:
    matchLabels:
      app: myapp
      version: v1

  # Rolling update strategy
  strategy:
    type: RollingUpdate
    rollingUpdate:
      maxSurge: 1         # Max pods above desired during update
      maxUnavailable: 0   # Max pods unavailable during update

  # Minimum time before pod is considered available
  minReadySeconds: 10

  # Revision history limit
  revisionHistoryLimit: 10

  # Pod template
  template:
    metadata:
      labels:
        app: myapp
        version: v1
    spec:
      containers:
      - name: myapp
        image: myapp:1.0
        ports:
        - containerPort: 8080
        resources:
          requests:
            memory: "128Mi"
            cpu: "250m"
          limits:
            memory: "256Mi"
            cpu: "500m"
        livenessProbe:
          httpGet:
            path: /health
            port: 8080
          initialDelaySeconds: 30
          periodSeconds: 10
        readinessProbe:
          httpGet:
            path: /ready
            port: 8080
          initialDelaySeconds: 5
          periodSeconds: 5
        env:
        - name: ENVIRONMENT
          value: "production"
```

### Complete Service Manifest

```yaml
apiVersion: v1
kind: Service
metadata:
  name: myapp-service
  namespace: production
  labels:
    app: myapp
spec:
  # Service type
  type: ClusterIP  # ClusterIP, NodePort, LoadBalancer, ExternalName

  # Label selector (routes to pods with these labels)
  selector:
    app: myapp

  # Ports
  ports:
  - name: http
    protocol: TCP
    port: 80          # Service port
    targetPort: 8080  # Container port (can be name or number)
  - name: metrics
    protocol: TCP
    port: 9090
    targetPort: metrics

  # Session affinity
  sessionAffinity: ClientIP
  sessionAffinityConfig:
    clientIP:
      timeoutSeconds: 10800
```

### Complete ConfigMap Manifest

```yaml
apiVersion: v1
kind: ConfigMap
metadata:
  name: app-config
  namespace: production
data:
  # Simple key-value pairs
  database.host: "postgres.default.svc.cluster.local"
  database.port: "5432"
  log.level: "info"

  # File-like keys
  application.yaml: |
    server:
      port: 8080
      host: 0.0.0.0
    database:
      pool_size: 20
      timeout: 30

  nginx.conf: |
    server {
      listen 80;
      server_name example.com;
      location / {
        proxy_pass http://backend:8080;
      }
    }
```

### Complete Secret Manifest

```yaml
apiVersion: v1
kind: Secret
metadata:
  name: app-secrets
  namespace: production
type: Opaque
# Option 1: Base64 encoded data
data:
  username: YWRtaW4=           # "admin"
  password: cGFzc3dvcmQxMjM=   # "password123"

# Option 2: Plain text (K8s will encode)
stringData:
  api-key: "sk-1234567890abcdef"
  database-url: "postgres://user:pass@host:5432/db"
```

### Complete PersistentVolumeClaim Manifest

```yaml
apiVersion: v1
kind: PersistentVolumeClaim
metadata:
  name: app-storage
  namespace: production
spec:
  accessModes:
  - ReadWriteOnce      # RWO, ROX, RWX

  storageClassName: fast-ssd

  resources:
    requests:
      storage: 10Gi

  # Optional: selector to bind to specific PV
  selector:
    matchLabels:
      release: stable
```

### Complete Ingress Manifest

```yaml
apiVersion: networking.k8s.io/v1
kind: Ingress
metadata:
  name: app-ingress
  namespace: production
  annotations:
    # Nginx-specific annotations
    nginx.ingress.kubernetes.io/rewrite-target: /
    nginx.ingress.kubernetes.io/ssl-redirect: "true"
    nginx.ingress.kubernetes.io/rate-limit: "100"
    # Cert-manager annotation for automatic TLS
    cert-manager.io/cluster-issuer: "letsencrypt-prod"
spec:
  ingressClassName: nginx

  # TLS configuration
  tls:
  - hosts:
    - myapp.example.com
    - api.example.com
    secretName: tls-secret

  # Routing rules
  rules:
  - host: myapp.example.com
    http:
      paths:
      - path: /
        pathType: Prefix
        backend:
          service:
            name: frontend-service
            port:
              number: 80
      - path: /api
        pathType: Prefix
        backend:
          service:
            name: backend-service
            port:
              number: 8080

  - host: api.example.com
    http:
      paths:
      - path: /
        pathType: Prefix
        backend:
          service:
            name: api-service
            port:
              number: 8080
```

### Multi-Resource YAML File

You can define multiple resources in one file separated by `---`:

```yaml
apiVersion: v1
kind: Namespace
metadata:
  name: myapp
---
apiVersion: v1
kind: ConfigMap
metadata:
  name: app-config
  namespace: myapp
data:
  database.host: "postgres"
---
apiVersion: apps/v1
kind: Deployment
metadata:
  name: myapp
  namespace: myapp
spec:
  replicas: 3
  selector:
    matchLabels:
      app: myapp
  template:
    metadata:
      labels:
        app: myapp
    spec:
      containers:
      - name: myapp
        image: myapp:1.0
        ports:
        - containerPort: 8080
---
apiVersion: v1
kind: Service
metadata:
  name: myapp-service
  namespace: myapp
spec:
  selector:
    app: myapp
  ports:
  - port: 80
    targetPort: 8080
  type: ClusterIP
```

### YAML Validation Tips

```bash
# Dry-run (client-side validation)
kubectl apply -f manifest.yaml --dry-run=client

# Server-side validation (checks against API)
kubectl apply -f manifest.yaml --dry-run=server

# View what would be created
kubectl create deployment test --image=nginx --dry-run=client -o yaml

# Explain resource fields
kubectl explain deployment.spec.strategy
```

---

## Networking

### Pod Networking Fundamentals

#### Core Principles
Kubernetes networking follows these rules:
1. **Every Pod gets its own IP address**
2. **Pods can communicate with all other Pods** without NAT
3. **Nodes can communicate with all Pods** without NAT
4. **The IP a Pod sees itself as** is the same IP others see it as

#### Network Model

```
┌─────────────────────────────────────────────────────────┐
│                    Kubernetes Cluster                    │
│                                                           │
│  ┌──────────────────┐         ┌──────────────────┐      │
│  │    Node 1        │         │    Node 2        │      │
│  │  (10.0.1.0/24)   │         │  (10.0.2.0/24)   │      │
│  ├──────────────────┤         ├──────────────────┤      │
│  │                  │         │                  │      │
│  │ Pod A            │         │ Pod C            │      │
│  │ IP: 10.244.1.5   │◄───────►│ IP: 10.244.2.3   │      │
│  │                  │         │                  │      │
│  │ Pod B            │         │ Pod D            │      │
│  │ IP: 10.244.1.6   │         │ IP: 10.244.2.4   │      │
│  │                  │         │                  │      │
│  └──────────────────┘         └──────────────────┘      │
│         ▲                              ▲                 │
│         │                              │                 │
│         └──────────────┬───────────────┘                 │
│                        │                                 │
│                  ┌─────▼──────┐                          │
│                  │   CNI      │                          │
│                  │  Plugin    │                          │
│                  │ (Calico,   │                          │
│                  │  Flannel)  │                          │
│                  └────────────┘                          │
└─────────────────────────────────────────────────────────┘
```

#### Container Network Interface (CNI)
Kubernetes delegates networking to CNI plugins:

**Popular CNI Plugins:**
- **Calico**: Feature-rich, network policies, BGP routing
- **Flannel**: Simple overlay network, easy to set up
- **Weave**: Mesh networking, encryption
- **Cilium**: eBPF-based, high performance, advanced features
- **Canal**: Calico + Flannel combination

### Service Discovery

#### DNS-Based Discovery
Kubernetes runs an internal DNS service (CoreDNS) that automatically creates DNS records for Services.

**DNS Record Format:**
```
<service-name>.<namespace>.svc.cluster.local
```

**Examples:**
```bash
# Same namespace
curl http://backend-service

# Different namespace
curl http://backend-service.production

# Fully qualified
curl http://backend-service.production.svc.cluster.local
```

#### DNS Records Created

**For Services:**
```
# A record (ClusterIP)
my-service.default.svc.cluster.local → 10.96.0.10

# SRV records (for named ports)
_http._tcp.my-service.default.svc.cluster.local
```

**For Pods:**
```
# Only if hostname and subdomain are set
pod-ip.my-service.default.svc.cluster.local
# Example: 10-244-1-5.my-service.default.svc.cluster.local
```

### Service Types in Detail

#### ClusterIP Flow

```
┌────────────┐
│  Client    │
│   Pod      │
└─────┬──────┘
      │ DNS lookup: backend-service → 10.96.0.10
      ▼
┌─────────────┐
│  Service    │
│  ClusterIP  │
│ 10.96.0.10  │
└──────┬──────┘
       │ iptables/IPVS rules (kube-proxy)
       ├──────┬──────┬──────┐
       ▼      ▼      ▼      ▼
    ┌───┐  ┌───┐  ┌───┐  ┌───┐
    │Pod│  │Pod│  │Pod│  │Pod│
    └───┘  └───┘  └───┘  └───┘
   .1.5   .1.6   .2.3   .2.4
```

#### NodePort Flow

```
External Client
      │
      │ http://node-ip:30080
      ▼
┌──────────────┐
│     Node     │
│ NodePort     │
│   :30080     │
└──────┬───────┘
       │ Routes to ClusterIP
       ▼
┌──────────────┐
│   Service    │
│  ClusterIP   │
└──────┬───────┘
       │ Load balances
       ▼
    Backend Pods
```

#### LoadBalancer Flow

```
External Client
      │
      ▼
Cloud Load Balancer (AWS ELB, GCP LB)
  Public IP: 203.0.113.10
      │
      ▼
┌──────────────┐
│  NodePort    │
│   Service    │
└──────┬───────┘
       │
       ▼
┌──────────────┐
│  ClusterIP   │
│   Service    │
└──────┬───────┘
       │
       ▼
    Backend Pods
```

### Network Policies

Network Policies control traffic flow between Pods and to/from external endpoints.

**Default Behavior:**
- All Pods can communicate with all Pods
- No isolation by default

#### Example: Deny All Ingress

```yaml
apiVersion: networking.k8s.io/v1
kind: NetworkPolicy
metadata:
  name: deny-all-ingress
  namespace: production
spec:
  podSelector: {}  # Applies to all pods in namespace
  policyTypes:
  - Ingress
  # No ingress rules = deny all
```

#### Example: Allow Specific Ingress

```yaml
apiVersion: networking.k8s.io/v1
kind: NetworkPolicy
metadata:
  name: allow-frontend-to-backend
  namespace: production
spec:
  podSelector:
    matchLabels:
      app: backend
  policyTypes:
  - Ingress
  ingress:
  - from:
    - podSelector:
        matchLabels:
          app: frontend
    ports:
    - protocol: TCP
      port: 8080
```

#### Example: Allow from Namespace

```yaml
apiVersion: networking.k8s.io/v1
kind: NetworkPolicy
metadata:
  name: allow-from-monitoring
  namespace: production
spec:
  podSelector:
    matchLabels:
      app: myapp
  policyTypes:
  - Ingress
  ingress:
  - from:
    - namespaceSelector:
        matchLabels:
          name: monitoring
    ports:
    - protocol: TCP
      port: 9090
```

#### Example: Egress Policy

```yaml
apiVersion: networking.k8s.io/v1
kind: NetworkPolicy
metadata:
  name: allow-dns-and-api
  namespace: production
spec:
  podSelector:
    matchLabels:
      app: myapp
  policyTypes:
  - Egress
  egress:
  # Allow DNS
  - to:
    - namespaceSelector:
        matchLabels:
          name: kube-system
    ports:
    - protocol: UDP
      port: 53
  # Allow external API
  - to:
    - ipBlock:
        cidr: 203.0.113.0/24
    ports:
    - protocol: TCP
      port: 443
```

### Service Mesh (Advanced)

For complex microservices, consider a service mesh like **Istio** or **Linkerd**:

**Features:**
- Advanced traffic management (retries, timeouts, circuit breaking)
- Mutual TLS between services
- Observability (metrics, tracing)
- Fine-grained access control

**Trade-off:** Additional complexity and resource overhead

---

## Scaling & Self-Healing

### Horizontal Pod Autoscaler (HPA)

#### What It Does
Automatically scales the number of Pods based on CPU utilization, memory, or custom metrics.

#### Requirements
- Metrics Server must be installed in the cluster
- Pods must have resource requests defined

#### HPA Workflow

```
Metrics Server
      │ (collects metrics)
      ▼
┌──────────────────┐
│       HPA        │
│  Target: 50% CPU │
└────────┬─────────┘
         │ (checks every 15s)
         │
         │ Current: 80% CPU
         │ → Scale up
         ▼
┌──────────────────┐
│   Deployment     │
│  Replicas: 3→5   │
└──────────────────┘
```

#### Basic HPA Example

```yaml
apiVersion: autoscaling/v2
kind: HorizontalPodAutoscaler
metadata:
  name: myapp-hpa
spec:
  scaleTargetRef:
    apiVersion: apps/v1
    kind: Deployment
    name: myapp
  minReplicas: 2
  maxReplicas: 10
  metrics:
  - type: Resource
    resource:
      name: cpu
      target:
        type: Utilization
        averageUtilization: 50
```

#### Command-Line HPA

```bash
# Create HPA
kubectl autoscale deployment myapp --cpu-percent=50 --min=2 --max=10

# View HPA status
kubectl get hpa

# Describe HPA (shows scaling events)
kubectl describe hpa myapp-hpa

# Delete HPA
kubectl delete hpa myapp-hpa
```

#### Multi-Metric HPA

```yaml
apiVersion: autoscaling/v2
kind: HorizontalPodAutoscaler
metadata:
  name: myapp-hpa
spec:
  scaleTargetRef:
    apiVersion: apps/v1
    kind: Deployment
    name: myapp
  minReplicas: 2
  maxReplicas: 20
  metrics:
  # CPU metric
  - type: Resource
    resource:
      name: cpu
      target:
        type: Utilization
        averageUtilization: 60

  # Memory metric
  - type: Resource
    resource:
      name: memory
      target:
        type: AverageValue
        averageValue: 500Mi

  # Custom metric (requires custom metrics API)
  - type: Pods
    pods:
      metric:
        name: http_requests_per_second
      target:
        type: AverageValue
        averageValue: "1k"

  # Scale behavior (v2 feature)
  behavior:
    scaleDown:
      stabilizationWindowSeconds: 300
      policies:
      - type: Percent
        value: 50
        periodSeconds: 60
    scaleUp:
      stabilizationWindowSeconds: 0
      policies:
      - type: Percent
        value: 100
        periodSeconds: 15
      - type: Pods
        value: 4
        periodSeconds: 15
      selectPolicy: Max
```

### Vertical Pod Autoscaler (VPA)

Automatically adjusts CPU and memory requests/limits based on usage.

**Use Case:** When you don't know the right resource requests

**Note:** VPA is not built-in; requires installation

```yaml
apiVersion: autoscaling.k8s.io/v1
kind: VerticalPodAutoscaler
metadata:
  name: myapp-vpa
spec:
  targetRef:
    apiVersion: apps/v1
    kind: Deployment
    name: myapp
  updatePolicy:
    updateMode: Auto  # Auto, Recreate, Initial, Off
```

### Health Checks: Probes

#### Liveness Probe
**Purpose:** Determine if container is running properly. If it fails, kubelet restarts the container.

**Use Cases:**
- Detect deadlocks
- Restart hung applications
- Health check for long-running processes

#### Readiness Probe
**Purpose:** Determine if container is ready to serve traffic. If it fails, Pod is removed from Service endpoints.

**Use Cases:**
- Application startup time
- Dependency checks (database connection)
- Temporary overload conditions

#### Startup Probe
**Purpose:** Determine if container application has started. Disables liveness/readiness until it succeeds.

**Use Cases:**
- Slow-starting applications
- Legacy applications with long initialization

#### Probe Types

**1. HTTP GET**
```yaml
livenessProbe:
  httpGet:
    path: /healthz
    port: 8080
    httpHeaders:
    - name: Custom-Header
      value: Awesome
  initialDelaySeconds: 30
  periodSeconds: 10
  timeoutSeconds: 5
  successThreshold: 1
  failureThreshold: 3
```

**2. TCP Socket**
```yaml
livenessProbe:
  tcpSocket:
    port: 8080
  initialDelaySeconds: 15
  periodSeconds: 20
```

**3. Exec Command**
```yaml
livenessProbe:
  exec:
    command:
    - cat
    - /tmp/healthy
  initialDelaySeconds: 5
  periodSeconds: 5
```

#### Comprehensive Probe Example

```yaml
apiVersion: v1
kind: Pod
metadata:
  name: probe-demo
spec:
  containers:
  - name: app
    image: myapp:1.0
    ports:
    - containerPort: 8080

    # Startup probe (runs first)
    startupProbe:
      httpGet:
        path: /startup
        port: 8080
      failureThreshold: 30   # 30 * 10 = 300s max startup time
      periodSeconds: 10

    # Liveness probe (restarts if fails)
    livenessProbe:
      httpGet:
        path: /healthz
        port: 8080
      initialDelaySeconds: 30
      periodSeconds: 10
      timeoutSeconds: 5
      failureThreshold: 3

    # Readiness probe (removes from service if fails)
    readinessProbe:
      httpGet:
        path: /ready
        port: 8080
      initialDelaySeconds: 5
      periodSeconds: 5
      timeoutSeconds: 3
      failureThreshold: 2
```

#### Probe Configuration Fields

- **initialDelaySeconds**: Wait before first probe
- **periodSeconds**: How often to perform probe
- **timeoutSeconds**: Probe timeout
- **successThreshold**: Minimum consecutive successes
- **failureThreshold**: Minimum consecutive failures to mark as failed

### Self-Healing Mechanisms

#### 1. Automatic Pod Restart
```yaml
spec:
  restartPolicy: Always  # Always, OnFailure, Never
```

**Backoff Mechanism:**
- First restart: immediate
- Subsequent restarts: 10s, 20s, 40s, ... up to 5 minutes

#### 2. ReplicaSet Guarantees
If a Pod is deleted or fails, ReplicaSet creates a new one to maintain desired count.

```bash
# Delete a pod
kubectl delete pod myapp-deployment-abc123

# ReplicaSet immediately creates a new one
kubectl get pods --watch
```

#### 3. Node Failure Recovery
If a node becomes unreachable:
1. Node marked as NotReady after ~40 seconds
2. After ~5 minutes, Pods are evicted
3. Pods are rescheduled on healthy nodes

#### 4. Resource Constraints Protection

```yaml
resources:
  requests:
    memory: "128Mi"
    cpu: "250m"
  limits:
    memory: "256Mi"
    cpu: "500m"
```

**Behaviors:**
- **CPU limit exceeded**: Throttled
- **Memory limit exceeded**: OOMKilled (restarted)

### Pod Disruption Budgets (PDB)

Ensure minimum availability during voluntary disruptions (node drains, updates).

```yaml
apiVersion: policy/v1
kind: PodDisruptionBudget
metadata:
  name: myapp-pdb
spec:
  minAvailable: 2  # or maxUnavailable: 1
  selector:
    matchLabels:
      app: myapp
```

**Use Cases:**
- Cluster upgrades
- Node maintenance
- Voluntary pod evictions

```bash
# Drain node (respects PDB)
kubectl drain <node-name> --ignore-daemonsets
```

---

## Real-World Patterns

### 1. Sidecar Pattern

#### Concept
Additional container(s) running alongside the main container in the same Pod, sharing resources.

#### Use Cases
- Log shipping/aggregation
- Monitoring agents
- Service mesh proxies (Envoy, Linkerd)
- Configuration synchronization

#### Example: Logging Sidecar

```yaml
apiVersion: v1
kind: Pod
metadata:
  name: app-with-logging
spec:
  containers:
  # Main application container
  - name: app
    image: myapp:1.0
    volumeMounts:
    - name: logs
      mountPath: /var/log/app

  # Sidecar: log collector
  - name: log-collector
    image: fluentd:latest
    volumeMounts:
    - name: logs
      mountPath: /var/log/app
      readOnly: true
    env:
    - name: FLUENT_ELASTICSEARCH_HOST
      value: "elasticsearch.logging.svc.cluster.local"

  volumes:
  - name: logs
    emptyDir: {}
```

#### Example: Service Mesh Sidecar

```yaml
apiVersion: v1
kind: Pod
metadata:
  name: app-with-proxy
spec:
  containers:
  # Main application
  - name: app
    image: myapp:1.0
    ports:
    - containerPort: 8080

  # Sidecar: Envoy proxy
  - name: envoy
    image: envoyproxy/envoy:v1.20.0
    ports:
    - containerPort: 15001  # Envoy admin
    volumeMounts:
    - name: envoy-config
      mountPath: /etc/envoy

  volumes:
  - name: envoy-config
    configMap:
      name: envoy-config
```

### 2. Init Containers

#### Concept
Specialized containers that run before app containers start. Must complete successfully.

#### Use Cases
- Wait for dependencies (database, external service)
- Pre-populate data or configuration
- Security setup (file permissions)
- Registration with external systems

#### Characteristics
- Run sequentially (not in parallel)
- Share volumes with main containers
- Do not support probes
- Failure causes Pod to restart

#### Example: Database Initialization

```yaml
apiVersion: v1
kind: Pod
metadata:
  name: app-with-init
spec:
  # Init containers (run in order)
  initContainers:
  # 1. Wait for database
  - name: wait-for-db
    image: busybox:1.28
    command: ['sh', '-c', 'until nslookup postgres; do echo waiting for postgres; sleep 2; done']

  # 2. Run database migrations
  - name: db-migration
    image: myapp-migrations:1.0
    env:
    - name: DATABASE_URL
      valueFrom:
        secretKeyRef:
          name: db-credentials
          key: url
    command: ['./migrate.sh']

  # 3. Download configuration
  - name: fetch-config
    image: appropriate/curl
    command:
    - sh
    - -c
    - |
      curl https://config-server/config > /config/app.yaml
    volumeMounts:
    - name: config
      mountPath: /config

  # Main application container
  containers:
  - name: app
    image: myapp:1.0
    volumeMounts:
    - name: config
      mountPath: /etc/app

  volumes:
  - name: config
    emptyDir: {}
```

#### Example: Security Setup

```yaml
apiVersion: v1
kind: Pod
metadata:
  name: secure-app
spec:
  initContainers:
  - name: setup-permissions
    image: busybox
    command:
    - sh
    - -c
    - |
      chown -R 1000:1000 /data
      chmod 700 /data
    volumeMounts:
    - name: data
      mountPath: /data
    securityContext:
      runAsUser: 0  # Run as root for permission changes

  containers:
  - name: app
    image: myapp:1.0
    volumeMounts:
    - name: data
      mountPath: /data
    securityContext:
      runAsUser: 1000
      runAsNonRoot: true

  volumes:
  - name: data
    emptyDir: {}
```

### 3. Jobs

#### Concept
Creates one or more Pods and ensures a specified number of them successfully terminate.

#### Use Cases
- Batch processing
- Data processing pipelines
- Backup operations
- One-time administrative tasks

#### Basic Job

```yaml
apiVersion: batch/v1
kind: Job
metadata:
  name: data-import
spec:
  # How many pods should complete successfully
  completions: 5

  # How many pods can run in parallel
  parallelism: 2

  # Backoff limit before marking job as failed
  backoffLimit: 4

  # Time limit for job completion
  activeDeadlineSeconds: 600

  template:
    metadata:
      name: data-import
    spec:
      restartPolicy: OnFailure  # or Never
      containers:
      - name: import
        image: data-importer:1.0
        command: ['./import.sh']
        env:
        - name: BATCH_ID
          value: "batch-001"
```

#### Parallel Jobs with Work Queue

```yaml
apiVersion: batch/v1
kind: Job
metadata:
  name: process-queue
spec:
  parallelism: 10
  completions: 50  # 50 items to process
  template:
    spec:
      restartPolicy: OnFailure
      containers:
      - name: worker
        image: queue-worker:1.0
        env:
        - name: QUEUE_URL
          value: "redis://redis:6379"
```

#### Job Management

```bash
# Create job
kubectl apply -f job.yaml

# View job status
kubectl get jobs

# View pods created by job
kubectl get pods --selector=job-name=data-import

# View job logs
kubectl logs job/data-import

# Delete job (also deletes pods)
kubectl delete job data-import

# Delete job but keep pods
kubectl delete job data-import --cascade=orphan
```

### 4. CronJobs

#### Concept
Creates Jobs on a schedule (cron format).

#### Use Cases
- Periodic backups
- Report generation
- Data cleanup
- Scheduled maintenance tasks

#### CronJob Example

```yaml
apiVersion: batch/v1
kind: CronJob
metadata:
  name: database-backup
spec:
  # Cron schedule: "minute hour day month weekday"
  schedule: "0 2 * * *"  # Every day at 2 AM

  # Timezone (requires K8s 1.24+)
  timeZone: "America/New_York"

  # How many successful jobs to keep
  successfulJobsHistoryLimit: 3

  # How many failed jobs to keep
  failedJobsHistoryLimit: 1

  # Concurrency policy
  concurrencyPolicy: Forbid  # Forbid, Allow, Replace

  # Deadline for starting job if missed
  startingDeadlineSeconds: 300

  jobTemplate:
    spec:
      template:
        spec:
          restartPolicy: OnFailure
          containers:
          - name: backup
            image: postgres:13
            command:
            - sh
            - -c
            - |
              pg_dump -h postgres -U admin mydb > /backup/db-$(date +%Y%m%d).sql
            env:
            - name: PGPASSWORD
              valueFrom:
                secretKeyRef:
                  name: db-credentials
                  key: password
            volumeMounts:
            - name: backup
              mountPath: /backup
          volumes:
          - name: backup
            persistentVolumeClaim:
              claimName: backup-storage
```

#### Cron Schedule Examples

```
# Format: minute hour day month weekday

"*/5 * * * *"      # Every 5 minutes
"0 * * * *"        # Every hour
"0 0 * * *"        # Every day at midnight
"0 0 * * 0"        # Every Sunday at midnight
"0 0 1 * *"        # First day of every month
"0 2 1 */2 *"      # Every 2 months on the 1st at 2 AM
"0 9-17 * * 1-5"   # Weekdays between 9 AM and 5 PM
```

#### CronJob Management

```bash
# Create CronJob
kubectl apply -f cronjob.yaml

# List CronJobs
kubectl get cronjobs

# View recent jobs created by CronJob
kubectl get jobs --selector=job-name=database-backup

# Manually trigger a job from CronJob
kubectl create job manual-backup --from=cronjob/database-backup

# Suspend CronJob (stop scheduling)
kubectl patch cronjob database-backup -p '{"spec":{"suspend":true}}'

# Resume CronJob
kubectl patch cronjob database-backup -p '{"spec":{"suspend":false}}'
```

### 5. DaemonSets

#### Concept
Ensures a copy of a Pod runs on all (or selected) nodes.

#### Use Cases
- Node monitoring (node-exporter)
- Log collection (fluentd)
- Network plugins
- Storage daemons

```yaml
apiVersion: apps/v1
kind: DaemonSet
metadata:
  name: node-exporter
spec:
  selector:
    matchLabels:
      app: node-exporter
  template:
    metadata:
      labels:
        app: node-exporter
    spec:
      hostNetwork: true  # Use host networking
      hostPID: true      # Access host PID namespace
      containers:
      - name: node-exporter
        image: prom/node-exporter:latest
        ports:
        - containerPort: 9100
          hostPort: 9100
```

### 6. StatefulSets

#### Concept
Like Deployments, but for stateful applications requiring stable network identities and persistent storage.

#### Features
- Stable, unique network identifiers
- Stable, persistent storage
- Ordered, graceful deployment and scaling
- Ordered, automated rolling updates

#### Use Cases
- Databases (MySQL, PostgreSQL)
- Distributed systems (Kafka, Cassandra, Elasticsearch)
- Applications requiring stable storage

```yaml
apiVersion: apps/v1
kind: StatefulSet
metadata:
  name: postgresql
spec:
  serviceName: postgres
  replicas: 3
  selector:
    matchLabels:
      app: postgres
  template:
    metadata:
      labels:
        app: postgres
    spec:
      containers:
      - name: postgres
        image: postgres:13
        ports:
        - containerPort: 5432
          name: postgres
        env:
        - name: POSTGRES_PASSWORD
          valueFrom:
            secretKeyRef:
              name: postgres-credentials
              key: password
        volumeMounts:
        - name: data
          mountPath: /var/lib/postgresql/data

  # Volume claim template
  volumeClaimTemplates:
  - metadata:
      name: data
    spec:
      accessModes: [ "ReadWriteOnce" ]
      storageClassName: fast-ssd
      resources:
        requests:
          storage: 20Gi
```

**Pod Naming:** `<statefulset-name>-<ordinal>`
- postgresql-0
- postgresql-1
- postgresql-2

**DNS Names:** `<pod-name>.<service-name>.<namespace>.svc.cluster.local`
- postgresql-0.postgres.default.svc.cluster.local

---

## Best Practices

### 1. Resource Management

#### Always Set Resource Requests and Limits

**Why:**
- Scheduler makes better placement decisions
- Prevents resource starvation
- Enables autoscaling
- Protects against runaway containers

**Requests:** Guaranteed resources
**Limits:** Maximum allowed resources

```yaml
resources:
  requests:
    memory: "128Mi"   # Guaranteed memory
    cpu: "250m"       # Guaranteed CPU (250 millicores = 0.25 cores)
  limits:
    memory: "256Mi"   # Max memory (exceeding = OOMKill)
    cpu: "500m"       # Max CPU (exceeding = throttle)
```

#### Quality of Service (QoS) Classes

Kubernetes assigns QoS based on resources:

**Guaranteed** (highest priority):
- Requests = Limits for all containers
- Least likely to be evicted

```yaml
resources:
  requests:
    memory: "256Mi"
    cpu: "500m"
  limits:
    memory: "256Mi"
    cpu: "500m"
```

**Burstable** (medium priority):
- Requests < Limits (or only requests set)
- Can use extra resources when available

```yaml
resources:
  requests:
    memory: "128Mi"
    cpu: "250m"
  limits:
    memory: "512Mi"
    cpu: "1000m"
```

**BestEffort** (lowest priority):
- No requests or limits set
- First to be evicted under pressure
- Avoid in production

#### Resource Units

**CPU:**
- `1` = 1 CPU core
- `100m` = 100 millicores = 0.1 core
- `250m` = 0.25 core

**Memory:**
- `128Mi` = 128 mebibytes = 134,217,728 bytes
- `1Gi` = 1 gibibyte = 1,073,741,824 bytes
- Also: `128M` (megabytes), `1G` (gigabytes)

### 2. Labels and Selectors

#### Label Best Practices

**Use structured, semantic labels:**

```yaml
metadata:
  labels:
    # Recommended labels (from K8s docs)
    app.kubernetes.io/name: myapp
    app.kubernetes.io/instance: myapp-prod
    app.kubernetes.io/version: "1.0.0"
    app.kubernetes.io/component: backend
    app.kubernetes.io/part-of: ecommerce-system
    app.kubernetes.io/managed-by: helm

    # Custom labels
    environment: production
    team: platform
    cost-center: engineering
```

**Label Organization:**
- **Identifying attributes**: app, component, version
- **Operational attributes**: environment, tier
- **Business attributes**: team, cost-center, customer

**Selector Types:**

```yaml
# Equality-based
selector:
  matchLabels:
    app: myapp
    environment: production

# Set-based
selector:
  matchExpressions:
  - key: environment
    operator: In
    values: [production, staging]
  - key: tier
    operator: NotIn
    values: [development]
  - key: app
    operator: Exists
```

### 3. Namespace Organization

#### Strategy 1: By Environment

```
namespaces:
  - development
  - staging
  - production
```

#### Strategy 2: By Team

```
namespaces:
  - team-frontend
  - team-backend
  - team-data
  - shared-services
```

#### Strategy 3: Hybrid

```
namespaces:
  - production-frontend
  - production-backend
  - staging-frontend
  - staging-backend
```

#### Namespace Resource Isolation

```yaml
# Limit resources per namespace
apiVersion: v1
kind: ResourceQuota
metadata:
  name: production-quota
  namespace: production
spec:
  hard:
    requests.cpu: "100"
    requests.memory: 200Gi
    limits.cpu: "200"
    limits.memory: 400Gi
    persistentvolumeclaims: "50"
    pods: "100"
    services.loadbalancers: "5"
```

```yaml
# Set default resource limits
apiVersion: v1
kind: LimitRange
metadata:
  name: default-limits
  namespace: production
spec:
  limits:
  - default:
      cpu: 500m
      memory: 512Mi
    defaultRequest:
      cpu: 250m
      memory: 256Mi
    type: Container
```

### 4. Configuration Management

#### Don't Hardcode Configuration

**Bad:**
```yaml
env:
- name: DATABASE_URL
  value: "postgres://user:pass@db:5432/mydb"  # ❌ Hardcoded
```

**Good:**
```yaml
env:
- name: DATABASE_URL
  valueFrom:
    secretKeyRef:
      name: db-credentials
      key: url  # ✅ From Secret
```

#### Use ConfigMaps for Non-Sensitive Data

```yaml
env:
- name: LOG_LEVEL
  valueFrom:
    configMapKeyRef:
      name: app-config
      key: log-level
```

#### Use Secrets for Sensitive Data

```yaml
env:
- name: API_KEY
  valueFrom:
    secretKeyRef:
      name: api-secrets
      key: api-key
```

### 5. Health Checks

#### Always Use Probes

**Liveness Probe:** Is the app running?
**Readiness Probe:** Is the app ready for traffic?

```yaml
livenessProbe:
  httpGet:
    path: /healthz
    port: 8080
  initialDelaySeconds: 30
  periodSeconds: 10

readinessProbe:
  httpGet:
    path: /ready
    port: 8080
  initialDelaySeconds: 5
  periodSeconds: 5
```

#### Implement Health Endpoints in Your App

```python
# Python/Flask example
@app.route('/healthz')
def healthz():
    return 'OK', 200

@app.route('/ready')
def ready():
    # Check dependencies
    if database.is_connected():
        return 'OK', 200
    else:
        return 'Not Ready', 503
```

### 6. Security Best Practices

#### Run as Non-Root User

```yaml
securityContext:
  runAsNonRoot: true
  runAsUser: 1000
  fsGroup: 1000
  capabilities:
    drop:
    - ALL
```

#### Read-Only Root Filesystem

```yaml
securityContext:
  readOnlyRootFilesystem: true

# Mount tmpfs for writable directories
volumeMounts:
- name: tmp
  mountPath: /tmp
volumes:
- name: tmp
  emptyDir: {}
```

#### Use Pod Security Standards

```yaml
apiVersion: v1
kind: Namespace
metadata:
  name: production
  labels:
    pod-security.kubernetes.io/enforce: restricted
    pod-security.kubernetes.io/audit: restricted
    pod-security.kubernetes.io/warn: restricted
```

#### Scan Images for Vulnerabilities

Use tools like:
- Trivy
- Clair
- Snyk

```bash
trivy image myapp:1.0
```

### 7. Image Management

#### Use Specific Image Tags

**Bad:**
```yaml
image: nginx:latest  # ❌ Unpredictable
```

**Good:**
```yaml
image: nginx:1.21.6-alpine  # ✅ Specific, reproducible
```

#### Use Small Base Images

- `alpine` (~5 MB)
- `distroless` (Google's minimal images)
- Multi-stage Docker builds

#### Use Private Registry

```yaml
imagePullSecrets:
- name: regcred
```

### 8. Logging and Monitoring

#### Structured Logging

Output logs to stdout/stderr in JSON format:

```json
{"timestamp":"2025-01-30T10:00:00Z","level":"INFO","message":"Request processed","request_id":"abc123"}
```

#### Centralized Log Aggregation

Use tools like:
- ELK Stack (Elasticsearch, Logstash, Kibana)
- EFK Stack (Elasticsearch, Fluentd, Kibana)
- Loki + Grafana
- Cloud solutions (CloudWatch, Stackdriver)

#### Monitoring and Metrics

**Prometheus + Grafana:**
- Metrics collection
- Alerting
- Visualization

**Install kube-state-metrics:**
Exposes cluster-level metrics

### 9. Deployment Strategies

#### Rolling Update (Default)

```yaml
strategy:
  type: RollingUpdate
  rollingUpdate:
    maxSurge: 1
    maxUnavailable: 0  # Zero-downtime
```

#### Blue-Green Deployment

1. Deploy new version (green)
2. Test green
3. Switch traffic to green
4. Keep blue for rollback

#### Canary Deployment

Gradually shift traffic to new version:
- 10% traffic to v2
- Monitor metrics
- 50% traffic to v2
- Monitor metrics
- 100% traffic to v2

Tools: Flagger, Argo Rollouts

### 10. GitOps

Store all Kubernetes manifests in Git:

**Benefits:**
- Version control
- Audit trail
- Easy rollback
- Declarative infrastructure

**Tools:**
- ArgoCD
- Flux
- Jenkins X

---

## Common Troubleshooting

### Pod Issues

#### Pod Stuck in Pending

**Symptoms:**
```bash
kubectl get pods
NAME          READY   STATUS    RESTARTS   AGE
myapp-xyz     0/1     Pending   0          5m
```

**Common Causes:**

**1. Insufficient Resources**
```bash
kubectl describe pod myapp-xyz
# Look for: "0/3 nodes are available: 3 Insufficient cpu"
```

**Solution:**
- Scale down other workloads
- Add more nodes
- Reduce resource requests

**2. Node Selector Mismatch**
```bash
kubectl describe pod myapp-xyz
# Look for: "0/3 nodes are available: 3 node(s) didn't match node selector"
```

**Solution:**
- Check nodeSelector in pod spec
- Verify node labels: `kubectl get nodes --show-labels`

**3. PersistentVolumeClaim Not Bound**
```bash
kubectl get pvc
# Look for: STATUS = Pending
```

**Solution:**
- Check if PV exists and matches PVC requirements
- Verify StorageClass exists

#### Pod in CrashLoopBackOff

**Symptoms:**
```bash
kubectl get pods
NAME          READY   STATUS             RESTARTS   AGE
myapp-xyz     0/1     CrashLoopBackOff   5          10m
```

**Diagnosis:**

```bash
# View logs from current container
kubectl logs myapp-xyz

# View logs from previous container (after crash)
kubectl logs myapp-xyz --previous

# Describe pod to see events
kubectl describe pod myapp-xyz
```

**Common Causes:**

**1. Application Error**
- Check application logs for errors
- Verify configuration (ConfigMaps, Secrets)
- Check environment variables

**2. Missing Dependencies**
- Database not reachable
- External service unavailable
- Use init containers to wait for dependencies

**3. Liveness Probe Failing**
```bash
kubectl describe pod myapp-xyz
# Look for: "Liveness probe failed"
```

**Solution:**
- Increase `initialDelaySeconds`
- Fix health check endpoint
- Increase `failureThreshold`

#### Pod in ImagePullBackOff

**Symptoms:**
```bash
kubectl get pods
NAME          READY   STATUS            RESTARTS   AGE
myapp-xyz     0/1     ImagePullBackOff  0          2m
```

**Common Causes:**

**1. Image Doesn't Exist**
```bash
kubectl describe pod myapp-xyz
# Look for: "Failed to pull image: manifest for myapp:1.0 not found"
```

**Solution:**
- Verify image name and tag
- Check if image is pushed to registry

**2. Authentication Required**
```bash
kubectl describe pod myapp-xyz
# Look for: "Pull access denied"
```

**Solution:**
- Create image pull secret
- Add to pod spec or service account

```bash
kubectl create secret docker-registry regcred \
  --docker-server=registry.example.com \
  --docker-username=user \
  --docker-password=pass \
  --docker-email=user@example.com
```

**3. Network Issues**
- Registry unreachable
- DNS resolution failure

#### Pod Status: CreateContainerConfigError

**Cause:** Usually missing ConfigMap or Secret

```bash
kubectl describe pod myapp-xyz
# Look for: "configmap "app-config" not found"
```

**Solution:**
- Create missing ConfigMap/Secret
- Fix reference in pod spec

### Service Issues

#### Cannot Access Service

**Diagnosis Steps:**

```bash
# 1. Check service exists
kubectl get svc myapp-service

# 2. Check endpoints (should list pod IPs)
kubectl get endpoints myapp-service

# 3. Check pod labels match service selector
kubectl get pods --show-labels
kubectl describe svc myapp-service  # See selector

# 4. Test from within cluster
kubectl run test-pod --image=busybox --rm -it -- sh
wget -O- http://myapp-service
```

**Common Issues:**

**1. No Endpoints**
- Service selector doesn't match pod labels
- No pods are ready (check readiness probes)

**2. Wrong Port**
- Check `port` (service port) vs `targetPort` (container port)

```yaml
ports:
- port: 80          # Access service on port 80
  targetPort: 8080  # Forwards to container port 8080
```

### Deployment Issues

#### Deployment Rollout Stuck

```bash
kubectl rollout status deployment/myapp
# Waiting for deployment "myapp" rollout to finish...
```

**Diagnosis:**

```bash
# Check deployment
kubectl describe deployment myapp

# Check ReplicaSet
kubectl get rs
kubectl describe rs myapp-xyz

# Check pods
kubectl get pods -l app=myapp
kubectl describe pod myapp-xyz
```

**Common Causes:**

1. New pods failing health checks
2. Insufficient resources
3. Image pull failures

**Solutions:**

```bash
# Pause rollout
kubectl rollout pause deployment/myapp

# Fix issues

# Resume rollout
kubectl rollout resume deployment/myapp

# Or rollback
kubectl rollout undo deployment/myapp
```

### Node Issues

#### Node NotReady

```bash
kubectl get nodes
NAME     STATUS     ROLES    AGE   VERSION
node-1   NotReady   worker   10d   v1.24.0
```

**Diagnosis:**

```bash
kubectl describe node node-1
# Look at Conditions section
```

**Common Causes:**

1. **Disk Pressure:** Node running out of disk space
2. **Memory Pressure:** Node running out of memory
3. **Network Issues:** Node can't reach control plane
4. **kubelet Problems:** kubelet crashed or stopped

**Solutions:**

```bash
# SSH to node (if possible)
ssh node-1

# Check kubelet status
systemctl status kubelet

# Check kubelet logs
journalctl -u kubelet

# Restart kubelet
systemctl restart kubelet
```

### Networking Issues

#### Cannot Reach External Services

**Diagnosis:**

```bash
# Test DNS resolution
kubectl run test --image=busybox --rm -it -- nslookup google.com

# Test connectivity
kubectl run test --image=busybox --rm -it -- wget -O- https://google.com

# Check CoreDNS
kubectl get pods -n kube-system -l k8s-app=kube-dns
kubectl logs -n kube-system -l k8s-app=kube-dns
```

#### Pod-to-Pod Communication Failure

**Check:**

1. **Network Policies:** May be blocking traffic
```bash
kubectl get networkpolicies
kubectl describe networkpolicy <name>
```

2. **CNI Plugin:** Issues with CNI
```bash
kubectl get pods -n kube-system  # Check CNI pods
```

### Debugging Tools and Commands

#### Execute Commands in Container

```bash
# Interactive shell
kubectl exec -it myapp-xyz -- /bin/bash

# Run single command
kubectl exec myapp-xyz -- ls /app

# For multi-container pods
kubectl exec -it myapp-xyz -c sidecar -- sh
```

#### Port Forwarding for Local Testing

```bash
# Forward pod port to localhost
kubectl port-forward pod/myapp-xyz 8080:80

# Forward service port
kubectl port-forward svc/myapp-service 8080:80

# Access via http://localhost:8080
```

#### Temporary Debug Pod

```bash
# Run temporary pod
kubectl run debug --image=busybox --rm -it -- sh

# With network troubleshooting tools
kubectl run debug --image=nicolaka/netshoot --rm -it -- bash
```

#### Copy Files To/From Pod

```bash
# Copy from pod to local
kubectl cp myapp-xyz:/var/log/app.log ./app.log

# Copy from local to pod
kubectl cp ./config.yaml myapp-xyz:/etc/config.yaml
```

#### View Events

```bash
# All events in namespace
kubectl get events --sort-by=.metadata.creationTimestamp

# Events for specific resource
kubectl describe pod myapp-xyz  # See events at bottom

# Watch events in real-time
kubectl get events --watch
```

#### Resource Metrics

```bash
# Node metrics
kubectl top nodes

# Pod metrics
kubectl top pods

# Specific pod
kubectl top pod myapp-xyz

# All pods in namespace with containers
kubectl top pod --containers
```

#### API Resources and Versions

```bash
# List all API resources
kubectl api-resources

# Explain resource structure
kubectl explain pod
kubectl explain pod.spec
kubectl explain pod.spec.containers

# Get API versions
kubectl api-versions
```

### Common Error Messages and Solutions

#### "Error from server (Forbidden): pods is forbidden"

**Cause:** Insufficient RBAC permissions

**Solution:** Check your permissions or contact cluster admin

```bash
# Check your permissions
kubectl auth can-i create pods
kubectl auth can-i get pods --as system:serviceaccount:default:myapp
```

#### "The connection to the server was refused"

**Cause:** Cannot reach Kubernetes API server

**Solutions:**
- Check cluster is running
- Verify kubeconfig: `kubectl config view`
- Check VPN connection (if applicable)

#### "OOMKilled"

**Cause:** Container exceeded memory limit

**Solution:**
- Increase memory limits
- Investigate memory leak in application
- Check actual memory usage: `kubectl top pod`

### Debugging Checklist

When troubleshooting a problem:

1. **Check pod status**
   ```bash
   kubectl get pods
   ```

2. **Describe the resource**
   ```bash
   kubectl describe pod <name>
   ```

3. **Check logs**
   ```bash
   kubectl logs <pod-name>
   kubectl logs <pod-name> --previous
   ```

4. **View events**
   ```bash
   kubectl get events --sort-by=.metadata.creationTimestamp
   ```

5. **Check resource metrics**
   ```bash
   kubectl top nodes
   kubectl top pods
   ```

6. **Verify configuration**
   ```bash
   kubectl get pod <name> -o yaml
   ```

7. **Test connectivity**
   ```bash
   kubectl run test --image=busybox --rm -it -- sh
   ```

---

## Summary and Next Steps

### Key Takeaways

1. **Kubernetes is a container orchestration platform** that automates deployment, scaling, and management of containerized applications.

2. **Core abstractions** include Pods (smallest unit), Deployments (manage replicas), Services (networking), and more.

3. **Everything is declarative** - you describe desired state in YAML, Kubernetes makes it happen.

4. **kubectl is your primary interface** for interacting with clusters.

5. **Labels and selectors** are fundamental for organizing and connecting resources.

6. **Health probes and resource limits** are essential for production workloads.

7. **Kubernetes is self-healing** - automatically restarts failed containers and reschedules pods.

### Learning Path

**Level 1: Beginner**
- ✅ Understand core concepts (covered in this guide)
- Practice with Minikube or kind (local clusters)
- Deploy simple applications
- Master kubectl basics

**Level 2: Intermediate**
- Learn Helm (package manager for Kubernetes)
- Understand StatefulSets for stateful apps
- Implement network policies
- Set up monitoring with Prometheus/Grafana
- Practice troubleshooting

**Level 3: Advanced**
- Service mesh (Istio, Linkerd)
- GitOps (ArgoCD, Flux)
- Custom Resource Definitions (CRDs)
- Operators
- Multi-cluster management
- Advanced security (OPA, Falco)

### Practice Resources

**Local Development:**
- **Minikube**: Full Kubernetes cluster on your machine
- **kind**: Kubernetes in Docker
- **k3s**: Lightweight Kubernetes
- **Docker Desktop**: Includes Kubernetes

**Cloud Platforms:**
- GKE (Google Kubernetes Engine)
- EKS (Amazon Elastic Kubernetes Service)
- AKS (Azure Kubernetes Service)

**Online Playgrounds:**
- Katacoda (interactive scenarios)
- Play with Kubernetes
- KillerCoda

**Certifications:**
- CKA (Certified Kubernetes Administrator)
- CKAD (Certified Kubernetes Application Developer)
- CKS (Certified Kubernetes Security Specialist)

### Quick Reference Commands

```bash
# Cluster info
kubectl cluster-info
kubectl get nodes

# Pods
kubectl get pods
kubectl describe pod <name>
kubectl logs <pod>
kubectl exec -it <pod> -- sh

# Deployments
kubectl get deployments
kubectl scale deployment/<name> --replicas=5
kubectl set image deployment/<name> container=image:tag
kubectl rollout status deployment/<name>
kubectl rollout undo deployment/<name>

# Services
kubectl get svc
kubectl expose deployment/<name> --port=80 --type=LoadBalancer

# ConfigMaps & Secrets
kubectl create configmap <name> --from-literal=key=value
kubectl create secret generic <name> --from-literal=key=value

# Apply manifests
kubectl apply -f manifest.yaml
kubectl delete -f manifest.yaml

# Debugging
kubectl describe <resource> <name>
kubectl logs <pod> --previous
kubectl get events
kubectl top nodes/pods
```

---

## Conclusion

Kubernetes is a powerful platform that has become the de facto standard for container orchestration. While it has a steep learning curve, understanding its core concepts, architecture, and best practices will enable you to build, deploy, and manage scalable, resilient applications.

The key to mastering Kubernetes is **hands-on practice**. Start with simple deployments, experiment with different resource types, break things, and learn from troubleshooting. The more you work with Kubernetes, the more intuitive it becomes.

Remember: **Kubernetes doesn't make distributed systems easy, but it makes them manageable**. It provides the primitives to build robust, scalable systems, but you still need to design your applications thoughtfully.

Good luck on your Kubernetes journey!

---

**Author:** Generated by Claude Code
**Last Updated:** January 2026
**Version:** 1.0
