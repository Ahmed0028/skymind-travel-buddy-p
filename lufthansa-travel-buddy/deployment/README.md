# Deployment to Vertex AI Agent Engine

## Setup

```bash
pip install google-cloud-aiplatform
```

## Deploy

```bash
python deployment/deploy.py --create
```

## Test

```bash
python deployment/test_deployment.py --resource_id="projects/.../reasoningEngines/..."
```

## Manage

```bash
# List agents
python deployment/deploy.py --list

# Delete agent
python deployment/deploy.py --delete --resource_id="..."
```
