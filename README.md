# MarketPulse

MarketPulse is a compact crypto market dashboard portfolio project.

## Deployment

- Kubernetes manifests: `infra/k8s`
- Image build workflow: `.github/workflows/images.yml`
- Deployment notes: `docs/deployment.md`

The image workflow pushes backend and frontend images to Docker Hub. k3s rollout is currently a documented manual handoff; automated deployment is planned for infra TASK-09.
