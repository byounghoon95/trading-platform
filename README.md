# MarketPulse

MarketPulse is a compact crypto market dashboard portfolio project.

## Deployment

- Helm chart: `infra/helm/marketpulse`
- Image build workflow: `.github/workflows/images.yml`
- Deployment notes: `docs/deployment.md`
- Operations and monitoring notes: `docs/operations.md`

The image workflow pushes backend and frontend images to Docker Hub. k3s rollout is currently a documented manual handoff; automated deployment is planned for infra TASK-09.

## Monitoring

The backend exposes Prometheus metrics at `/metrics`. The Helm chart includes a compact Prometheus and Grafana runtime, with the `MarketPulse Operations` Grafana dashboard packaged from `infra/helm/marketpulse/files/grafana/marketpulse-dashboard.json`.

Prometheus is exposed through `prometheus.marketpulse.byhoon.co.kr` and Grafana is exposed through `grafana.marketpulse.byhoon.co.kr` when DNS points those hosts at the k3s ingress node.
