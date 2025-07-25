#!/bin/bash

# RAG2.0 Azure Setup Script
# This script creates all necessary Azure resources for deployment

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration
RESOURCE_GROUP="rag20-rg"
LOCATION="eastus"
ACR_NAME="chatbotdeveloper"
WEBAPP_NAME="rag20-webapp"
APP_SERVICE_PLAN="rag20-plan"
SERVICE_PRINCIPAL_NAME="rag20-github-actions"

echo -e "${BLUE}🚀 RAG2.0 Azure Setup Script${NC}"
echo "=================================="

# Check if Azure CLI is installed
if ! command -v az &> /dev/null; then
    echo -e "${RED}❌ Azure CLI is not installed. Please install it first.${NC}"
    echo "Visit: https://docs.microsoft.com/en-us/cli/azure/install-azure-cli"
    exit 1
fi

# Check if logged in
if ! az account show &> /dev/null; then
    echo -e "${YELLOW}⚠️  You are not logged in to Azure. Please log in first.${NC}"
    az login
fi

echo -e "${GREEN}✅ Azure CLI is ready${NC}"

# Get subscription ID
SUBSCRIPTION_ID=$(az account show --query id -o tsv)
echo -e "${BLUE}📋 Using subscription: ${SUBSCRIPTION_ID}${NC}"

# Create Resource Group
echo -e "${BLUE}📦 Creating Resource Group...${NC}"
az group create --name $RESOURCE_GROUP --location $LOCATION --output none
echo -e "${GREEN}✅ Resource Group created: $RESOURCE_GROUP${NC}"

# Create Azure Container Registry
echo -e "${BLUE}🐳 Creating Azure Container Registry...${NC}"
az acr create --resource-group $RESOURCE_GROUP --name $ACR_NAME --sku Basic --output none
az acr update --name $ACR_NAME --admin-enabled true --output none
echo -e "${GREEN}✅ Container Registry created: $ACR_NAME${NC}"

# Get ACR credentials
echo -e "${BLUE}🔑 Getting ACR credentials...${NC}"
ACR_USERNAME=$(az acr credential show --name $ACR_NAME --query username -o tsv)
ACR_PASSWORD=$(az acr credential show --name $ACR_NAME --query passwords[0].value -o tsv)
echo -e "${GREEN}✅ ACR Username: $ACR_USERNAME${NC}"

# Create App Service Plan
echo -e "${BLUE}📋 Creating App Service Plan...${NC}"
az appservice plan create --name $APP_SERVICE_PLAN --resource-group $RESOURCE_GROUP --sku B1 --is-linux --output none
echo -e "${GREEN}✅ App Service Plan created: $APP_SERVICE_PLAN${NC}"

# Create Web App
echo -e "${BLUE}🌐 Creating Web App...${NC}"
az webapp create --resource-group $RESOURCE_GROUP --plan $APP_SERVICE_PLAN --name $WEBAPP_NAME --deployment-local-git --output none
echo -e "${GREEN}✅ Web App created: $WEBAPP_NAME${NC}"

# Configure Web App for containers
echo -e "${BLUE}⚙️  Configuring Web App for containers...${NC}"
az webapp config container set --name $WEBAPP_NAME --resource-group $RESOURCE_GROUP \
    --docker-custom-image-name $ACR_NAME.azurecr.io/rag-all-in-one:latest \
    --docker-registry-server-url https://$ACR_NAME.azurecr.io \
    --docker-registry-server-user $ACR_USERNAME \
    --docker-registry-server-password $ACR_PASSWORD \
    --output none

# Set startup command
az webapp config set --name $WEBAPP_NAME --resource-group $RESOURCE_GROUP \
    --startup-file "/usr/local/bin/supervisord -c /etc/supervisor/conf.d/supervisord.conf" \
    --output none

echo -e "${GREEN}✅ Web App configured for containers${NC}"

# Create Service Principal for GitHub Actions
echo -e "${BLUE}🔐 Creating Service Principal for GitHub Actions...${NC}"
SP_OUTPUT=$(az ad sp create-for-rbac --name $SERVICE_PRINCIPAL_NAME --role contributor \
    --scopes /subscriptions/$SUBSCRIPTION_ID/resourceGroups/$RESOURCE_GROUP \
    --sdk-auth --output json)

echo -e "${GREEN}✅ Service Principal created: $SERVICE_PRINCIPAL_NAME${NC}"

# Display results
echo ""
echo -e "${GREEN}🎉 Azure Resources Created Successfully!${NC}"
echo "=============================================="
echo ""
echo -e "${BLUE}📋 Resource Details:${NC}"
echo "  Resource Group: $RESOURCE_GROUP"
echo "  Container Registry: $ACR_NAME.azurecr.io"
echo "  Web App: $WEBAPP_NAME"
echo "  App Service Plan: $APP_SERVICE_PLAN"
echo ""
echo -e "${BLUE}🔑 Credentials for GitHub Secrets:${NC}"
echo "  REGISTRY_USERNAME: $ACR_USERNAME"
echo "  REGISTRY_PASSWORD: $ACR_PASSWORD"
echo "  AZURE_RESOURCE_GROUP: $RESOURCE_GROUP"
echo ""
echo -e "${YELLOW}⚠️  IMPORTANT: Copy the following JSON for AZURE_CREDENTIALS secret:${NC}"
echo "$SP_OUTPUT"
echo ""
echo -e "${BLUE}🌐 Your application will be available at:${NC}"
echo "  https://$WEBAPP_NAME.azurewebsites.net"
echo ""
echo -e "${BLUE}📝 Next Steps:${NC}"
echo "  1. Go to your GitHub repository"
echo "  2. Navigate to Settings → Secrets and variables → Actions"
echo "  3. Add the secrets listed above"
echo "  4. Push code to trigger deployment"
echo ""
echo -e "${GREEN}✅ Setup complete!${NC}" 