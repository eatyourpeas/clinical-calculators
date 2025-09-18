#!/bin/bash -e

az acr login --name ${AZURE_REGISTRY_NAME}

docker compose build

# Tests (against local Postgres)
docker compose up -d
s/test.sh
docker compose down

# Push to Azure
azure_tag="${AZURE_REGISTRY_NAME}.azurecr.io/clinical-calculators:${GITHUB_SHA}"
docker tag clinical-calculators:built ${azure_tag}
docker push ${azure_tag}

# Deploy to Azure Container Apps

az containerapp revision copy \
    --name ${AZURE_LIVE_APP_NAME} \
    --resource-group ${AZURE_RESOURCE_GROUP} \
    --image ${azure_tag} \
    --query 'properties.provisioningState'

# Deploy to the docs is handled in the GitHub workflow itself