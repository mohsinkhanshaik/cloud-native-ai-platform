# 🧠 Cloud-Native AI Platform

[![CI/CD](https://github.com/mohsinkhanshaik/cloud-native-ai-platform/actions/workflows/ci-cd.yml/badge.svg)](https://github.com/mohsinkhanshaik/cloud-native-ai-platform/actions)
[![Docker](https://img.shields.io/badge/Docker-Containerized-2496ED?logo=docker&logoColor=white)](https://www.docker.com/)
[![Kubernetes](https://img.shields.io/badge/Kubernetes-Orchestrated-326CE5?logo=kubernetes&logoColor=white)](https://kubernetes.io/)
[![Terraform](https://img.shields.io/badge/Terraform-IaC-7B42BC?logo=terraform&logoColor=white)](https://www.terraform.io/)
[![AWS](https://img.shields.io/badge/AWS-EKS%20%7C%20ECR%20%7C%20VPC-FF9900?logo=amazonaws&logoColor=white)](https://aws.amazon.com/)
[![Python](https://img.shields.io/badge/Python-3.11-3776AB?logo=python&logoColor=white)](https://python.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.111-009688?logo=fastapi&logoColor=white)](https://fastapi.tiangolo.com/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

> A **production-ready AI inference platform** engineered for scale, reliability, and observability. Runs AI workloads on Kubernetes with full CI/CD automation, infrastructure-as-code, and Prometheus metrics out of the box.
>
> ---
>
> ## 🏗️ Architecture
>
> ```mermaid
> graph TB
>     Client["Client / API Consumer"] -->|HTTPS| ALB
>
>     subgraph AWS["AWS Cloud"]
>         subgraph VPC["VPC — 10.0.0.0/16"]
>             ALB["Application Load Balancer"]
>             subgraph Private["Private Subnets"]
>                 subgraph EKS["EKS Cluster (v1.29)"]
>                     Ingress["Nginx Ingress Controller"]
>                     subgraph NS["ai-platform namespace"]
>                         SVC["ClusterIP Service :80"]
>                         Pod1["Pod 1 — FastAPI :8000"]
>                         Pod2["Pod 2 — FastAPI :8000"]
>                         Pod3["Pod 3 — FastAPI :8000"]
>                         HPA["HPA min:2 max:20"]
>                     end
>                     subgraph MON["monitoring namespace"]
>                         Prometheus["Prometheus"]
>                         Grafana["Grafana"]
>                     end
>                 end
>             end
>         end
>         ECR["Amazon ECR"]
>         S3["S3 — TF State"]
>     end
>
>     subgraph GH["GitHub"]
>         Code["Source Code"] --> Actions["GitHub Actions CI/CD"]
>     end
>
>     ALB --> Ingress --> SVC --> Pod1 & Pod2 & Pod3
>     HPA -.->|scales| Pod1 & Pod2 & Pod3
>     Pod1 & Pod2 & Pod3 -->|/metrics| Prometheus --> Grafana
>     Actions -->|push image| ECR
>     Actions -->|kubectl apply| EKS
> ```
>
> ---
>
> ## ✨ Features
>
> - **AI Inference API** — FastAPI backend with pluggable LLM support (OpenAI, Anthropic, self-hosted)
> - - **Observability-First** — Prometheus counters and histograms on every request: latency, throughput, error rate, inference count by model
>   - - **Kubernetes-Ready** — Deployment with liveness/readiness/startup probes, resource limits, HPA scaling on CPU + Memory, Ingress with TLS
>     - - **Multi-Stage Docker Build** — Minimal production image with health check built-in
>       - - **Infrastructure as Code** — Terraform modules provision AWS EKS cluster, ECR registry, and VPC in one `terraform apply`
>         - - **Automated CI/CD** — GitHub Actions: test → build → push to ECR → rolling deploy to EKS → smoke test
>           - - **Local Dev Stack** — `docker-compose up` spins up the API + Prometheus + Grafana in one command
>            
>             - ---
>
> ## 📁 Project Structure
>
> ```
> cloud-native-ai-platform/
> ├── src/
> │   └── main.py                  # FastAPI app — inference API, health probes, Prometheus metrics
> ├── k8s/
> │   ├── namespace.yaml           # Kubernetes namespace
> │   ├── configmap.yaml           # App config (ENV, LOG_LEVEL, timeouts)
> │   ├── deployment.yaml          # Deployment — 3 replicas, probes, resource limits
> │   ├── service.yaml             # ClusterIP Service
> │   ├── hpa.yaml                 # HPA — CPU + Memory auto-scaling (min:2 max:20)
> │   └── ingress.yaml             # Nginx Ingress with TLS
> ├── terraform/
> │   ├── providers.tf             # AWS + Kubernetes providers, S3 remote state backend
> │   ├── main.tf                  # VPC + EKS cluster + ECR repository
> │   ├── variables.tf             # Input variables with validation
> │   └── outputs.tf               # Cluster name, ECR URL, VPC ID
> ├── monitoring/
> │   └── prometheus.yml           # Prometheus scrape config
> ├── .github/workflows/
> │   └── ci-cd.yml                # Full CI/CD pipeline (test → build → push → deploy → verify)
> ├── Dockerfile                   # Multi-stage production build
> ├── docker-compose.yml           # Local dev: API + Prometheus + Grafana
> └── requirements.txt
> ```
>
> ---
>
> ## 🚀 Quick Start — Local
>
> **Prerequisites:** Docker, Docker Compose
>
> ```bash
> git clone https://github.com/mohsinkhanshaik/cloud-native-ai-platform.git
> cd cloud-native-ai-platform
>
> # Start full local stack
> docker-compose up --build
>
> # API docs:    http://localhost:8000/docs
> # Prometheus:  http://localhost:9090
> # Grafana:     http://localhost:3000  (admin / admin)
> ```
>
> ---
>
> ## 📡 API Reference
>
> | Method | Endpoint | Description |
> |--------|----------|-------------|
> | `GET` | `/health` | Health check (k8s liveness probe) |
> | `GET` | `/ready` | Readiness check |
> | `GET` | `/live` | Liveness check |
> | `GET` | `/metrics` | Prometheus metrics |
> | `POST` | `/api/v1/infer` | AI inference request |
> | `GET` | `/api/v1/models` | List available models |
> | `GET` | `/docs` | Swagger UI |
>
> **Example:**
> ```bash
> curl -X POST http://localhost:8000/api/v1/infer \
>   -H "Content-Type: application/json" \
>   -d '{
>     "prompt": "Summarize the benefits of Kubernetes for AI workloads",
>     "model": "gpt-4o-mini",
>     "max_tokens": 256
>   }'
> ```
>
> ---
>
> ## ☁️ Deploy to AWS
>
> **Prerequisites:** AWS CLI, Terraform >= 1.5, kubectl
>
> ```bash
> # 1. Provision infrastructure
> cd terraform
> terraform init
> terraform plan -var="environment=production"
> terraform apply
>
> # 2. Configure kubectl
> aws eks update-kubeconfig --name ai-platform-eks --region us-east-1
>
> # 3. Push image to ECR
> ECR_URL=$(terraform output -raw ecr_repository_url)
> docker build -t $ECR_URL:latest .
> docker push $ECR_URL:latest
>
> # 4. Deploy to Kubernetes
> kubectl apply -f k8s/
> kubectl rollout status deployment/ai-platform -n ai-platform
> ```
>
> ---
>
> ## 📊 Observability
>
> Prometheus metrics exposed at `/metrics`:
>
> | Metric | Type | Labels | Description |
> |--------|------|--------|-------------|
> | `ai_platform_requests_total` | Counter | method, endpoint, status | Total HTTP requests |
> | `ai_platform_request_duration_seconds` | Histogram | endpoint | Request latency (p50/p95/p99) |
> | `ai_platform_inference_total` | Counter | model, status | Inference calls by model |
>
> ---
>
> ## 🔄 CI/CD Pipeline
>
> ```
> Push to main ──► Test (pytest) ──► Build Docker image
>                                         │
>                                Push to Amazon ECR
>                                         │
>                           kubectl apply -f k8s/ (rolling update)
>                                         │
>                           kubectl rollout status (verify)
>                                         │
>                               Smoke test /health endpoint
> ```
>
> ---
>
> ## 🏷️ Tech Stack
>
> | Layer | Technology |
> |-------|-----------|
> | Language | Python 3.11 |
> | API Framework | FastAPI + Uvicorn |
> | Containerization | Docker (multi-stage build) |
> | Orchestration | Kubernetes on AWS EKS |
> | Auto-scaling | HPA — CPU + Memory metrics |
> | Infrastructure | Terraform (VPC, EKS, ECR, S3) |
> | Cloud | AWS (EKS, ECR, VPC, S3, DynamoDB) |
> | CI/CD | GitHub Actions |
> | Observability | Prometheus + Grafana |
> | Ingress | Nginx Ingress Controller + cert-manager |
>
> ---
>
> ## 👤 Author
>
> **Mohsin Khan Shaik** — AI Infrastructure Engineer | SRE | Cloud & DevOps
>
> [![Portfolio](https://img.shields.io/badge/Portfolio-mohsinkhan--shaik.com-black?logo=googlechrome)](https://mohsinkhan-shaik.com)
> [![LinkedIn](https://img.shields.io/badge/LinkedIn-Connect-0A66C2?logo=linkedin)](https://linkedin.com/in/mohsin-khan-shaik-972817213)
>
> ---
>
> ## 📄 License
>
> MIT © Mohsin Khan Shaik
