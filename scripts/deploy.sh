#!/bin/bash
set -euo pipefail

# deploy a new docker image to a service in ECS and wait for the deployment to finish
# usage: `ENVIRONMENT=integration IMAGE_TAG=latest ./deploy.sh bread`

APP=${1?"app name required"}
ENVIRONMENT=${ENVIRONMENT?"must be defined"}
IMAGE_TAG=${IMAGE_TAG:-latest}
DEPLOY_TIMEOUT=${DEPLOY_TIMEOUT:-900}

CLUSTER="$ENVIRONMENT-newhippo"
SERVICE="$ENVIRONMENT-sandwich-$APP"

SERVICES=("$SERVICE")

# TODO: the sandwich service might deploy both frontends and backends out of the same image
#if [[ "$APP" == "sandwich" ]]; then
#  SERVICES+=("$SERVICE-worker")
#fi

# 1: re-tag the docker image app:latest to app:integration
MANIFEST=$(aws ecr batch-get-image --repository-name "$APP" --image-ids imageTag="$IMAGE_TAG" --output text --query 'images[].imageManifest')
if [[ -z "$MANIFEST" ]]; then
  echo "failed to get image manifest for $APP:$IMAGE_TAG"
  exit 1
fi
aws ecr put-image --repository-name "$APP" --image-tag "$ENVIRONMENT" --image-manifest "$MANIFEST"

# 2: trigger an ECS deployment that will pick up the updated image
for SERVICE in "${SERVICES[@]}"; do
  aws ecs update-service --cluster "$CLUSTER" --service "$SERVICE" --force-new-deployment
done

# 3: wait for the previous deployment to drain
for SERVICE in "${SERVICES[@]}"; do
  while true; do
    DEPLOYMENTS=$(aws ecs describe-services --cluster "$CLUSTER" --services "$SERVICE" --query 'services[].deployments[].[rolloutState,createdAt]' --output text)
    N_DEPLOYMENTS=$(echo "$DEPLOYMENTS" | wc -l | tr -d ' ')
    echo "$DEPLOYMENTS"

    if [[ "$N_DEPLOYMENTS" -gt 1 ]]; then
      if [[ "$SECONDS" -gt "$DEPLOY_TIMEOUT" ]]; then
        echo "timed out after $SECONDS seconds"
        exit 1
      fi
      echo "will check again in 10s..."
      sleep 10
    else
      break
    fi
  done
done
