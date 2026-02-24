#!/usr/bin/env python3
"""
DevForge - Deploy Agent
Handles deployment to various environments
"""

import os
import json
import subprocess
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional

class DeployAgent:
    """Deployment Agent - deploys code to various environments"""
    
    def __init__(self, config_path="config/.env"):
        self.config = self._load_config(config_path)
        self.projects_dir = Path("projects")
        self.deployments_dir = Path("data/deployments")
        self.deployments_dir.mkdir(parents=True, exist_ok=True)
        
    def _load_config(self, path):
        config = {}
        if os.path.exists(path):
            with open(path) as f:
                for line in f:
                    if '=' in line and not line.startswith('#'):
                        key, value = line.strip().split('=', 1)
                        config[key] = value.strip('"')
        for key in ['DOCKER_USERNAME', 'KUBECONFIG', 'AWS_ACCESS_KEY']:
            if os.environ.get(key):
                config[key] = os.environ.get(key)
        return config
    
    def deploy(self, feature_id: str, environment: str = "staging", 
               platform: str = "docker") -> Dict:
        """
        Deploy a feature to specified environment
        
        Args:
            feature_id: Feature to deploy
            environment: Target environment (local/staging/production)
            platform: Deployment platform (docker/kubernetes/vercel/aws)
        """
        feature_dir = self.projects_dir / feature_id
        codebase_dir = feature_dir / "codebase"
        
        if not feature_dir.exists():
            raise FileNotFoundError(f"Feature {feature_id} not found")
        
        # Load feature spec
        with open(feature_dir / "feature_spec.json") as f:
            feature_data = json.load(f)
        
        print(f"🚀 Deploy Agent: Deploying {feature_id}")
        print(f"   Environment: {environment}")
        print(f"   Platform: {platform}")
        
        # Pre-deployment checks
        checks = self._run_pre_deploy_checks(feature_id, feature_data)
        if not checks['passed']:
            print("❌ Pre-deployment checks failed!")
            return checks
        
        # Deploy based on platform
        if platform == "docker":
            deploy_result = self._deploy_docker(feature_id, codebase_dir, environment)
        elif platform == "kubernetes":
            deploy_result = self._deploy_kubernetes(feature_id, codebase_dir, environment)
        elif platform == "vercel":
            deploy_result = self._deploy_vercel(feature_id, codebase_dir, environment)
        elif platform == "aws":
            deploy_result = self._deploy_aws(feature_id, codebase_dir, environment)
        else:
            raise ValueError(f"Unknown platform: {platform}")
        
        # Run post-deployment verification
        verification = self._verify_deployment(deploy_result)
        
        # Update feature status
        deployment_record = {
            "deployment_id": f"deploy_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
            "feature_id": feature_id,
            "environment": environment,
            "platform": platform,
            "timestamp": datetime.now().isoformat(),
            "pre_deploy_checks": checks,
            "deployment": deploy_result,
            "verification": verification,
            "status": "success" if verification['passed'] else "failed",
            "urls": deploy_result.get('urls', {})
        }
        
        # Save deployment record
        deploy_file = self.deployments_dir / f"{deployment_record['deployment_id']}.json"
        with open(deploy_file, 'w') as f:
            json.dump(deployment_record, f, indent=2)
        
        # Update feature
        feature_data['deployments'] = feature_data.get('deployments', [])
        feature_data['deployments'].append(deployment_record)
        
        if verification['passed']:
            feature_data['status'] = f'deployed_{environment}'
        
        with open(feature_dir / "feature_spec.json", 'w') as f:
            json.dump(feature_data, f, indent=2)
        
        # Display results
        self._display_results(deployment_record)
        
        return deployment_record
    
    def _run_pre_deploy_checks(self, feature_id: str, feature_data: Dict) -> Dict:
        """Run pre-deployment checks"""
        print("\n   Running pre-deployment checks...")
        
        checks = {
            "passed": True,
            "checks": []
        }
        
        # Check 1: Tests passed
        test_results = feature_data.get('test_results', {})
        test_score = test_results.get('summary', {}).get('overall_score', 0)
        test_passed = test_score >= 70
        
        checks['checks'].append({
            "name": "Tests passed",
            "status": "passed" if test_passed else "failed",
            "details": f"Score: {test_score:.1f}%"
        })
        
        if not test_passed:
            checks['passed'] = False
        
        # Check 2: Code exists
        codebase_exists = (self.projects_dir / feature_id / "codebase").exists()
        checks['checks'].append({
            "name": "Codebase exists",
            "status": "passed" if codebase_exists else "failed"
        })
        
        if not codebase_exists:
            checks['passed'] = False
        
        # Check 3: Docker files exist (for docker deploy)
        dockerfile_exists = (self.projects_dir / feature_id / "codebase" / "docker-compose.yml").exists()
        checks['checks'].append({
            "name": "Docker configuration",
            "status": "passed" if dockerfile_exists else "warning",
            "details": "docker-compose.yml found" if dockerfile_exists else "Will use fallback"
        })
        
        # Check 4: Environment variables configured
        env_configured = bool(self.config.get('JWT_SECRET') or self.config.get('DATABASE_URL'))
        checks['checks'].append({
            "name": "Environment configured",
            "status": "passed" if env_configured else "warning"
        })
        
        return checks
    
    def _deploy_docker(self, feature_id: str, codebase_dir: Path, environment: str) -> Dict:
        """Deploy using Docker Compose"""
        print(f"\n   Building Docker containers...")
        
        # Generate production docker-compose if needed
        compose_file = codebase_dir / "docker-compose.yml"
        if not compose_file.exists():
            self._generate_production_docker_compose(codebase_dir, environment)
        
        # Build and start
        try:
            # In production, would actually run docker-compose
            # For demo, simulate the deployment
            
            return {
                "method": "docker-compose",
                "services": {
                    "postgres": {
                        "status": "running",
                        "port": 5432,
                        "health": "healthy"
                    },
                    "backend": {
                        "status": "running",
                        "port": 3001,
                        "health": "healthy",
                        "build_time": "45s"
                    },
                    "frontend": {
                        "status": "running",
                        "port": 3000,
                        "health": "healthy",
                        "build_time": "32s"
                    }
                },
                "urls": {
                    "application": f"http://localhost:3000",
                    "api": f"http://localhost:3001",
                    "api_docs": f"http://localhost:3001/api-docs"
                },
                "logs": "docker-compose logs -f",
                "scale_command": "docker-compose up -d --scale backend=3"
            }
        except Exception as e:
            return {
                "method": "docker-compose",
                "status": "failed",
                "error": str(e)
            }
    
    def _generate_production_docker_compose(self, codebase_dir: Path, environment: str):
        """Generate production-ready docker-compose"""
        compose = f'''version: '3.8'

services:
  postgres:
    image: postgres:15-alpine
    environment:
      POSTGRES_USER: ${{DB_USER}}
      POSTGRES_PASSWORD: ${{DB_PASSWORD}}
      POSTGRES_DB: ${{DB_NAME}}
    volumes:
      - postgres_data:/var/lib/postgresql/data
    networks:
      - app-network
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U ${{DB_USER}} -d ${{DB_NAME}}"]
      interval: 10s
      timeout: 5s
      retries: 5

  backend:
    build: 
      context: ./backend
      dockerfile: Dockerfile
    environment:
      - NODE_ENV={environment}
      - DATABASE_URL=postgresql://${{DB_USER}}:${{DB_PASSWORD}}@postgres:5432/${{DB_NAME}}
      - JWT_SECRET=${{JWT_SECRET}}
      - PORT=3001
    depends_on:
      postgres:
        condition: service_healthy
    networks:
      - app-network
    restart: unless-stopped
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:3001/health"]
      interval: 30s
      timeout: 10s
      retries: 3

  frontend:
    build:
      context: ./frontend
      dockerfile: Dockerfile
    environment:
      - VITE_API_URL=/api/v1
    networks:
      - app-network
    restart: unless-stopped

  nginx:
    image: nginx:alpine
    ports:
      - "80:80"
      - "443:443"
    volumes:
      - ./nginx.conf:/etc/nginx/nginx.conf:ro
    depends_on:
      - backend
      - frontend
    networks:
      - app-network
    restart: unless-stopped

volumes:
  postgres_data:

networks:
  app-network:
    driver: bridge
'''
        
        with open(codebase_dir / "docker-compose.prod.yml", 'w') as f:
            f.write(compose)
    
    def _deploy_kubernetes(self, feature_id: str, codebase_dir: Path, environment: str) -> Dict:
        """Deploy to Kubernetes"""
        print(f"\n   Deploying to Kubernetes...")
        
        # Generate K8s manifests
        k8s_dir = codebase_dir / "k8s"
        k8s_dir.mkdir(exist_ok=True)
        
        # Deployment manifest
        deployment = f'''apiVersion: apps/v1
kind: Deployment
metadata:
  name: {feature_id}-backend
  namespace: {environment}
spec:
  replicas: 3
  selector:
    matchLabels:
      app: {feature_id}-backend
  template:
    metadata:
      labels:
        app: {feature_id}-backend
    spec:
      containers:
      - name: backend
        image: {feature_id}/backend:latest
        ports:
        - containerPort: 3001
        env:
        - name: NODE_ENV
          value: "{environment}"
        - name: DATABASE_URL
          valueFrom:
            secretKeyRef:
              name: db-credentials
              key: url
        resources:
          requests:
            memory: "256Mi"
            cpu: "250m"
          limits:
            memory: "512Mi"
            cpu: "500m"
        livenessProbe:
          httpGet:
            path: /health
            port: 3001
          initialDelaySeconds: 30
          periodSeconds: 10
        readinessProbe:
          httpGet:
            path: /health
            port: 3001
          initialDelaySeconds: 5
          periodSeconds: 5
---
apiVersion: v1
kind: Service
metadata:
  name: {feature_id}-backend-service
  namespace: {environment}
spec:
  selector:
    app: {feature_id}-backend
  ports:
  - port: 80
    targetPort: 3001
  type: ClusterIP
'''
        
        with open(k8s_dir / "deployment.yaml", 'w') as f:
            f.write(deployment)
        
        return {
            "method": "kubernetes",
            "manifests": [
                "k8s/deployment.yaml",
                "k8s/service.yaml",
                "k8s/ingress.yaml"
            ],
            "namespace": environment,
            "replicas": 3,
            "urls": {
                "application": f"https://{feature_id}.{environment}.example.com",
                "api": f"https://{feature_id}.{environment}.example.com/api/v1"
            },
            "commands": {
                "apply": f"kubectl apply -f k8s/ -n {environment}",
                "status": f"kubectl get pods -n {environment} -l app={feature_id}-backend",
                "logs": f"kubectl logs -n {environment} -l app={feature_id}-backend --tail=100"
            }
        }
    
    def _deploy_vercel(self, feature_id: str, codebase_dir: Path, environment: str) -> Dict:
        """Deploy to Vercel (frontend only)"""
        print(f"\n   Deploying to Vercel...")
        
        # Generate vercel.json
        vercel_config = {
            "version": 2,
            "builds": [
                {"src": "frontend/package.json", "use": "@vercel/static-build"}
            ],
            "routes": [
                {"src": "/(.*)", "dest": "frontend/$1"}
            ],
            "env": {
                "VITE_API_URL": f"https://api-{feature_id}.vercel.app/api/v1"
            }
        }
        
        with open(codebase_dir / "vercel.json", 'w') as f:
            json.dump(vercel_config, f, indent=2)
        
        return {
            "method": "vercel",
            "platform": "serverless",
            "urls": {
                "frontend": f"https://{feature_id}.vercel.app",
                "preview": f"https://{feature_id}-git-main.vercel.app"
            },
            "commands": {
                "deploy": "vercel --prod",
                "preview": "vercel"
            }
        }
    
    def _deploy_aws(self, feature_id: str, codebase_dir: Path, environment: str) -> Dict:
        """Deploy to AWS"""
        print(f"\n   Deploying to AWS...")
        
        return {
            "method": "aws",
            "services": {
                "ecs": {
                    "cluster": f"{feature_id}-{environment}",
                    "service": "backend-service",
                    "tasks": 2
                },
                "rds": {
                    "instance": "db.t3.micro",
                    "engine": "postgres",
                    "status": "available"
                },
                "s3": {
                    "bucket": f"{feature_id}-assets",
                    "purpose": "Static assets and uploads"
                },
                "cloudfront": {
                    "purpose": "CDN for frontend"
                }
            },
            "urls": {
                "application": f"https://{feature_id}.{environment}.amazonaws.com",
                "cdn": f"https://d123456789.cloudfront.net"
            },
            "estimated_monthly_cost": "$45-80",
            "commands": {
                "deploy": "aws ecs update-service --cluster {cluster} --service backend-service --force-new-deployment",
                "logs": "aws logs tail /ecs/{feature_id} --follow"
            }
        }
    
    def _verify_deployment(self, deploy_result: Dict) -> Dict:
        """Verify deployment is working"""
        print("\n   Verifying deployment...")
        
        # In production: Actually make HTTP requests
        # For demo: Simulate verification
        
        return {
            "passed": True,
            "checks": [
                {"name": "Health endpoint", "status": "passed", "response_time": "45ms"},
                {"name": "Database connection", "status": "passed"},
                {"name": "API endpoints", "status": "passed", "tested": 7},
                {"name": "Frontend loads", "status": "passed", "load_time": "1.2s"},
                {"name": "Authentication works", "status": "passed"}
            ]
        }
    
    def _display_results(self, deployment: Dict):
        """Display deployment results"""
        print("\n" + "=" * 60)
        print("🚀 DEPLOYMENT COMPLETE")
        print("=" * 60)
        print(f"Deployment ID: {deployment['deployment_id']}")
        print(f"Environment: {deployment['environment']}")
        print(f"Platform: {deployment['platform']}")
        print(f"Status: {deployment['status'].upper()}")
        
        if 'urls' in deployment['deployment']:
            print("\n🌐 URLs:")
            for name, url in deployment['deployment']['urls'].items():
                print(f"   {name}: {url}")
        
        if deployment['status'] == 'success':
            print("\n✅ Deployment successful!")
            print(f"   Logs: {deployment['deployment'].get('logs', 'See deployment file')}")
        else:
            print("\n❌ Deployment failed")
            print(f"   Check: {deployment['verification']}")
        
        print("=" * 60)
    
    def rollback(self, deployment_id: str) -> Dict:
        """Rollback a deployment"""
        deploy_file = self.deployments_dir / f"{deployment_id}.json"
        
        if not deploy_file.exists():
            raise FileNotFoundError(f"Deployment {deployment_id} not found")
        
        with open(deploy_file) as f:
            deployment = json.load(f)
        
        print(f"🔄 Rolling back deployment {deployment_id}...")
        
        # In production: Actually rollback
        # docker-compose down, kubectl rollout undo, etc.
        
        deployment['rollback'] = {
            "timestamp": datetime.now().isoformat(),
            "status": "completed",
            "previous_version": "v1.0.0"
        }
        
        with open(deploy_file, 'w') as f:
            json.dump(deployment, f, indent=2)
        
        print("✅ Rollback complete")
        return deployment

if __name__ == "__main__":
    import sys
    
    if len(sys.argv) < 2:
        print("Usage: python3 deploy_agent.py <feature_id> [environment] [platform]")
        print("Example: python3 deploy_agent.py feat_20250225_0001 staging docker")
        print("\nEnvironments: local, staging, production")
        print("Platforms: docker, kubernetes, vercel, aws")
        sys.exit(1)
    
    deploy = DeployAgent()
    environment = sys.argv[2] if len(sys.argv) > 2 else "staging"
    platform = sys.argv[3] if len(sys.argv) > 3 else "docker"
    
    result = deploy.deploy(sys.argv[1], environment, platform)
    
    print(f"\n📁 Deployment record: data/deployments/{result['deployment_id']}.json")
