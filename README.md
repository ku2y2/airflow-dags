# Airflow DAGs Repository

This repository contains Airflow DAGs for the POC deployment with comprehensive Kubernetes deployment instructions.

## DAGs included:
- `hello_world_dag.py`: Simple demo DAG that prints hello world
- `dbt_dag.py`: dbt integration DAG for running dbt jobs
- More DAGs to be added for dbt integration

## Repository Structure
```
airflow-dags/
├── README.md                    # This documentation file
├── requirements.txt             # Python dependencies for Airflow
├── airflow-values.yaml         # Helm values for Airflow deployment
├── dags/                       # Airflow DAG files
│   ├── hello_world_dag.py
│   └── dbt_dag.py
└── dbt/                        # dbt project files
    ├── models/
    └── dbt_project.yml
```

## Prerequisites

Before starting the deployment, ensure you have the following tools installed:

### 1. Install Minikube
```bash
# macOS
brew install minikube

# Start minikube with sufficient resources
minikube start --cpus=4 --memory=8192 --disk-size=20g --driver=docker
```

### 2. Install Helm
```bash
# macOS
brew install helm
```

### 3. Add Airflow Helm Repository
```bash
helm repo add apache-airflow https://airflow.apache.org
helm repo update
```

## Deployment Steps

### Step 1: Prepare Kubernetes Environment
```bash
# Ensure minikube is running
minikube status

# Start minikube if not running (with sufficient resources)
minikube start --cpus=4 --memory=8192 --disk-size=20g --driver=docker

# Set kubectl context to minikube
kubectl config use-context minikube

# Verify cluster access
kubectl cluster-info
```

### Step 2: Add Airflow Helm Repository
```bash
# Add the Apache Airflow Helm repository
helm repo add apache-airflow https://airflow.apache.org
helm repo update
```

### Step 3: Deploy Complete Stack
The `airflow-values.yaml` file contains the complete configuration including:
- Airflow components (webserver, scheduler, triggerer)
- MySQL deployment for metadata storage
- MinIO deployment for log storage
- Kubernetes secrets for connections
- Git sync configuration for your public repository

```bash
# Deploy everything with a single command
helm install airflow apache-airflow/airflow \
    --namespace default \
    --values airflow-values.yaml \
    --timeout 15m

# Verify deployment (this may take 5-10 minutes)
kubectl get pods
kubectl get services
```

### Step 4: Monitor Deployment Progress
```bash
# Watch pod status (wait for all pods to be Running/Ready)
kubectl get pods -w

# Check specific pod logs if needed
kubectl logs -f deployment/airflow-scheduler
kubectl logs -f deployment/airflow-webserver

# Check all services
kubectl get svc
```

### Step 5: Wait for Deployment to Complete
```bash
# Watch pod status
kubectl get pods -w

# Check airflow logs
kubectl logs -l app.kubernetes.io/name=airflow

# Verify all pods are running
kubectl get pods | grep airflow
```

### Step 6: Port Forward Services

#### Port Forward Airflow UI
```bash
# Forward Airflow webserver port
kubectl port-forward svc/airflow-webserver 8080:8080

# Access Airflow UI at: http://localhost:8080
# Default credentials: admin / admin
```

#### Port Forward MinIO Console
```bash
# Forward MinIO console port (in a separate terminal)
kubectl port-forward svc/minio-service 9090:9090

# Access MinIO console at: http://localhost:9090
# Credentials: minioadmin / minioadmin123
```

#### Port Forward MySQL (Optional)
```bash
# Forward MySQL port for local connection (in a separate terminal)
kubectl port-forward svc/mysql-service 3306:3306

# Connect using: mysql -h localhost -P 3306 -u airflow -p
# Password: airflow123
```

## Airflow Configuration Details

### Executor Configuration
- **Type:** KubernetesExecutor
- **Namespace:** default
- **Worker Pods:** Auto-scaled and auto-deleted
- **Worker Image:** apache/airflow:2.10.2

### Git Sync Configuration
- **Repository:** This repository (airflow-dags)
- **Branch:** airflow-kubernetes-deployment
- **Sync Interval:** 60 seconds
- **SubPath:** "" (root directory)

### Database Configuration
- **Type:** MySQL 8.0
- **Connection:** `mysql://airflow:airflow123@mysql-service:3306/airflow`
- **SSL:** Disabled for local development

### Logging Configuration
- **Remote Logging:** Enabled
- **Storage:** MinIO S3-compatible storage
- **Bucket:** airflow-logs
- **Connection:** `s3://minioadmin:minioadmin123@minio-service:9000`

## dbt Integration

### dbt Project Setup
The repository includes a dbt project configured to work with Airflow:

```bash
# dbt project structure
dbt/
├── dbt_project.yml
├── models/
│   ├── staging/
│   └── marts/
└── profiles.yml
```

### dbt DAG Example
The `dbt_dag.py` file contains an example DAG that runs dbt commands:
- `dbt deps`: Install dbt packages
- `dbt run`: Execute dbt models
- `dbt test`: Run dbt tests

## Troubleshooting

### Common Issues and Solutions

#### 1. Pods Stuck in Pending State
```bash
# Check node resources
kubectl top nodes
kubectl describe nodes

# Check pod events
kubectl describe pod <pod-name>
```

#### 2. Database Connection Issues
```bash
# Test MySQL connection
kubectl exec -it <mysql-pod> -- mysql -u airflow -p airflow

# Check connection strings in Airflow config
kubectl exec -it <airflow-scheduler-pod> -- airflow config get-value database sql_alchemy_conn
```

#### 3. Git Sync Issues
```bash
# Check git-sync logs
kubectl logs <airflow-scheduler-pod> -c git-sync

# Verify git repository access
kubectl exec -it <airflow-scheduler-pod> -c git-sync -- ls /opt/airflow/dags
```

#### 4. MinIO Connection Issues
```bash
# Check MinIO service
kubectl get svc minio-service

# Test MinIO connectivity
kubectl exec -it <airflow-scheduler-pod> -- python -c "import boto3; print('MinIO connection test')"
```

### Useful Commands

#### Check Deployment Status
```bash
# Get all resources
kubectl get all

# Check persistent volumes (should be empty as PVC is disabled)
kubectl get pv,pvc

# Check secrets
kubectl get secrets
```

#### Scale Deployment
```bash
# Scale scheduler (if needed)
kubectl scale deployment airflow-scheduler --replicas=2

# Scale webserver
kubectl scale deployment airflow-webserver --replicas=2
```

#### Update Deployment
```bash
# Update Airflow with new values
helm upgrade airflow apache-airflow/airflow \
    --namespace default \
    --values airflow-values.yaml

# Restart deployment
kubectl rollout restart deployment airflow-scheduler
kubectl rollout restart deployment airflow-webserver
```

## Development Workflow

### Adding New DAGs
1. Create new DAG files in the `dags/` directory
2. Commit changes to the `airflow-kubernetes-deployment` branch
3. Git-sync will automatically sync changes within 60 seconds
4. New DAGs will appear in Airflow UI

### Adding New Dependencies
1. Update `requirements.txt` with new Python packages
2. Rebuild Airflow image or update `extraPipPackages` in values.yaml
3. Update Helm deployment

### Local Development
```bash
# Test DAG syntax locally
python dags/your_dag.py

# Install dependencies locally
pip install -r requirements.txt
```

## Security Notes

**⚠️ WARNING:** This configuration includes hardcoded secrets and is intended for **DEVELOPMENT/TESTING ONLY**.

For production deployments:
1. Use Kubernetes secrets properly
2. Enable TLS/SSL for all connections
3. Use proper authentication mechanisms
4. Implement network policies
5. Use image scanning and security policies

## Performance Optimization

### Resource Tuning
The current configuration uses minimal resources suitable for development:
- **MySQL:** 100m CPU, 256Mi RAM
- **MinIO:** 100m CPU, 256Mi RAM
- **Airflow Components:** 250m-500m CPU, 512Mi-1Gi RAM

For production workloads, increase these values based on requirements.

### Monitoring
```bash
# Check resource usage
kubectl top pods
kubectl top nodes

# View metrics (if metrics-server is installed)
minikube addons enable metrics-server
```

## Cleanup

### Remove Deployment
```bash
# Uninstall Airflow
helm uninstall airflow

# Remove persistent data (if any)
kubectl delete pvc --all

# Stop minikube (optional)
minikube stop
```

## Current Deployment Status

### ✅ Working Components
- **MySQL Database**: ✅ Running and accessible (mysql-5f6db874-44p4p)
- **MinIO Storage**: ✅ Running and accessible (minio-5f65999bc6-l7s92)
- **Git Repository**: ✅ Public repository configured for git-sync
- **Kubernetes Secrets**: ✅ airflow-connections secret deployed
- **Helm Configuration**: ✅ Complete airflow-values.yaml with all requirements
- **Port Forwarding**: ✅ Services accessible via localhost

### ⚠️ Components in Progress
- **Airflow Webserver**: In deployment phase (may take 5-10 minutes to be ready)
- **Airflow Scheduler**: In deployment phase
- **Airflow Triggerer**: In deployment phase
- **Database Migrations**: In progress during initialization

### 📋 Final Service Access (Once Ready)

| Service | URL | Username | Password | Status |
|---------|-----|----------|----------|---------|
| **Airflow UI** | http://localhost:8080 | `admin` | `admin` | ⏳ Deploying |
| **MinIO Console** | http://localhost:9090 | `minioadmin` | `minioadmin123` | ✅ Ready |
| **MySQL** | localhost:3306 | `airflow` | `airflow123` | ✅ Ready |

### 🔍 Troubleshooting Commands

If pods are not starting properly:
```bash
# Check pod status
kubectl get pods

# Check pod logs for specific issues
kubectl logs <pod-name>

# Describe pod for events
kubectl describe pod <pod-name>

# Restart deployment if needed
kubectl rollout restart deployment/<deployment-name>
```

### 📝 Known Issues and Solutions

1. **Pods Stuck in Init State**: Database migrations can take time. Wait 5-10 minutes.
2. **Git Sync Failures**: Ensure your repository is public and accessible.
3. **Resource Issues**: Increase minikube resources if pods are pending.

## Support

For issues and improvements:
1. Check logs: `kubectl logs <pod-name>`
2. Describe resources: `kubectl describe <resource-type> <resource-name>`
3. Review Airflow documentation: https://airflow.apache.org/docs/
4. Check Helm chart documentation: https://airflow.apache.org/docs/helm-chart/

## Next Steps

1. **Monitor Deployment**: Wait for all pods to be Running/Ready
2. **Access Services**: Use port forwarding to access Airflow UI and MinIO
3. **Deploy DAGs**: Your DAGs will be automatically synced from the git repository
4. **Test dbt Integration**: Run the included dbt_dag.py to test dbt functionality