# TERA Engine - Production Deployment Guide

## Quick Start (5 Minutes)

### 1. Install Dependencies
```bash
pip install -r requirements.txt
python -m spacy download en_core_web_sm
```

### 2. Configure Environment
```bash
cp .env.example .env
# Edit .env with your settings
```

### 3. Initialize Database
```bash
# Start MySQL
mysql -u root -p < database/schema.sql
```

### 4. Run Engine
```bash
python main.py
```

### 5. Test API
```bash
curl http://localhost:5000/health
```

## Docker Deployment (Recommended)

### Single Command Deploy
```bash
docker-compose up -d
```

### Manual Docker
```bash
# Build
docker build -t tera-engine .

# Run
docker run -d --name tera-engine --gpus all -p 5000:5000 tera-engine
```

## Cloud Deployment

### AWS (EC2 + ECS)
```bash
# Launch p4d.24xlarge instance
aws ec2 run-instances --image-id ami-xxx --instance-type p4d.24xlarge

# Deploy with ECS
aws ecs create-cluster --cluster-name tera-engine
aws ecs create-service --cluster tera-engine --service-name tera-api
```

### Google Cloud (GKE)
```bash
gcloud container clusters create tera-engine --machine-type a2-highgpu-8g
kubectl apply -f k8s/
```

### Azure (AKS)
```bash
az aks create --name tera-engine --node-vm-size Standard_NC24ads_A100_v4
kubectl apply -f k8s/
```

## Production Checklist

- [ ] Set strong API_KEY in .env
- [ ] Configure database credentials
- [ ] Set up SSL/TLS certificates
- [ ] Configure firewall rules
- [ ] Enable monitoring and logging
- [ ] Set up backup system
- [ ] Configure auto-scaling
- [ ] Test all endpoints
- [ ] Load test with expected traffic
- [ ] Set up CI/CD pipeline

## Monitoring

### Prometheus + Grafana
```bash
docker-compose -f docker-compose.monitoring.yml up -d
```

### Access Dashboards
- Grafana: http://localhost:3000
- Prometheus: http://localhost:9090

## Scaling

### Horizontal Scaling
```bash
# Add more workers
docker-compose up -d --scale tera-engine=4
```

### Vertical Scaling
```yaml
# Increase resources in docker-compose.yml
deploy:
  resources:
    limits:
      cpus: '32'
      memory: 256G
```

## Security

### Enable HTTPS
```bash
# Use Nginx reverse proxy
docker-compose -f docker-compose.nginx.yml up -d
```

### API Rate Limiting
```python
# Already configured in web_server.py
RATE_LIMIT = 1000  # requests per minute
```

## Backup

### Database Backup
```bash
# Automated daily backup
0 2 * * * mysqldump -u tera_user -p tera_engine > backup_$(date +\%Y\%m\%d).sql
```

### Asset Backup
```bash
# Sync to S3
aws s3 sync ./assets s3://tera-engine-assets/
```

## Performance Optimization

### GPU Optimization
```bash
export CUDA_VISIBLE_DEVICES=0,1,2,3,4,5,6,7
export GPU_MEMORY_FRACTION=0.95
```

### Cache Optimization
```bash
export MAX_CACHE_SIZE_GB=200
export REDIS_MAXMEMORY=50gb
```

## Troubleshooting

### Check Logs
```bash
docker logs tera-engine
tail -f logs/tera-engine.log
```

### Restart Services
```bash
docker-compose restart
```

### Clear Cache
```bash
redis-cli FLUSHALL
rm -rf cache/*
```
