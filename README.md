# MarketPulse

MarketPulse is a compact crypto market dashboard portfolio project.

## Deployment

- Kubernetes manifests: `infra/k8s`
- Image build workflow: `.github/workflows/images.yml`
- Deployment notes: `docs/deployment.md`
- Operations and monitoring notes: `docs/operations.md`

The image workflow pushes backend and frontend images to Docker Hub. k3s rollout is currently a documented manual handoff; automated deployment is planned for infra TASK-09.

## Monitoring

The backend exposes Prometheus metrics at `/metrics`. The k3s manifests include a compact Prometheus and Grafana runtime in `infra/k8s/06-monitoring.yaml`, with the `MarketPulse Operations` Grafana dashboard provisioned from `infra/monitoring/grafana/marketpulse-dashboard.json`.
