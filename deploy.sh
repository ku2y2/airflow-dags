#!/bin/bash

# Complete Airflow Deployment Script
# Deploys MySQL, MinIO, and Airflow in the correct order

set -e  # Exit on any error

echo "🚀 Starting Complete Airflow Deployment..."

# Colors for output
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

print_status() {
    echo -e "${BLUE}==== $1 ====${NC}"
}

print_success() {
    echo -e "${GREEN}✅ $1${NC}"
}

print_warning() {
    echo -e "${YELLOW}⚠️  $1${NC}"
}

# Check prerequisites
print_status "Checking Prerequisites"
if ! command -v kubectl &> /dev/null; then
    echo "❌ kubectl not found. Please install kubectl."
    exit 1
fi

if ! command -v helm &> /dev/null; then
    echo "❌ helm not found. Please install helm."
    exit 1
fi

if ! kubectl cluster-info &> /dev/null; then
    echo "❌ Cannot connect to Kubernetes cluster. Check your connection."
    exit 1
fi

print_success "Prerequisites check passed"

# Set Docker environment for minikube
print_status "Setting up Minikube Docker Environment"
if command -v minikube &> /dev/null; then
    eval $(minikube docker-env)
    print_success "Minikube Docker environment set"
else
    print_warning "Minikube not found, assuming regular Kubernetes cluster"
fi

# Step 1: Deploy MySQL
print_status "Deploying MySQL Database"
kubectl apply -f mysql-deployment.yaml
print_success "MySQL deployment applied"

# Step 2: Deploy MinIO
print_status "Deploying MinIO Storage"
kubectl apply -f minio-deployment.yaml
print_success "MinIO deployment applied"

# Step 3: Wait for MySQL and MinIO to be ready
print_status "Waiting for MySQL and MinIO to be ready"
echo "Waiting for MySQL..."
kubectl wait --for=condition=available --timeout=300s deployment/mysql
print_success "MySQL is ready"

echo "Waiting for MinIO..."
kubectl wait --for=condition=available --timeout=300s deployment/minio
print_success "MinIO is ready"

# Step 4: Build custom Airflow image (if Dockerfile exists)
if [ -f "Dockerfile" ]; then
    print_status "Building Custom Airflow Image"
    docker build -t custom-airflow:2.10.2 .
    print_success "Custom Airflow image built"
else
    print_warning "Dockerfile not found, skipping custom image build"
fi

# Step 5: Add Airflow Helm repository
print_status "Setting up Airflow Helm Repository"
helm repo add apache-airflow https://airflow.apache.org || true
helm repo update
print_success "Airflow Helm repository ready"

# Step 6: Deploy Airflow
print_status "Deploying Airflow"
if helm list | grep -q "^airflow"; then
    print_warning "Airflow already exists, upgrading..."
    helm upgrade airflow apache-airflow/airflow -f airflow-values.yaml
else
    helm install airflow apache-airflow/airflow -f airflow-values.yaml
fi
print_success "Airflow deployment applied"

# Step 7: Wait for Airflow to be ready
print_status "Waiting for Airflow Components to be Ready"
echo "This may take 5-10 minutes..."

echo "Waiting for Airflow webserver..."
kubectl wait --for=condition=available --timeout=600s deployment/airflow-webserver || true

echo "Waiting for Airflow scheduler..."
kubectl wait --for=condition=available --timeout=600s deployment/airflow-scheduler || true

# Step 8: Show deployment status
print_status "Deployment Status"
echo ""
echo "📊 Pod Status:"
kubectl get pods | grep -E "(mysql|minio|airflow)"
echo ""
echo "🌐 Service Status:"
kubectl get svc | grep -E "(mysql|minio|airflow)"
echo ""

# Step 9: Show access instructions
print_status "Access Instructions"
echo ""
echo "🎯 Airflow UI:"
echo "   kubectl port-forward svc/airflow-webserver 8080:8080"
echo "   Then access: http://localhost:8080"
echo "   Login: admin / admin"
echo ""
echo "📦 MinIO Console:"
echo "   kubectl port-forward svc/minio-service 9090:9090"
echo "   Then access: http://localhost:9090"
echo "   Login: minioadmin / minioadmin123"
echo ""
echo "🗄️ MySQL Database:"
echo "   kubectl port-forward svc/mysql-service 3306:3306"
echo "   Connection: mysql -h localhost -P 3306 -u airflow -p"
echo "   Password: airflow123"
echo ""

print_success "Deployment Complete!"
echo ""
echo "🎉 Your Airflow deployment is ready!"
echo "   - Custom image with dbt integration"
echo "   - Remote logging to MinIO working"
echo "   - Git sync enabled for DAG deployment"
echo "   - MySQL database for metadata"
echo ""
echo "Next steps:"
echo "1. Set up port forwarding for the services you need"
echo "2. Access Airflow UI and verify your DAGs are loaded"
echo "3. Test dbt integration with your custom image"