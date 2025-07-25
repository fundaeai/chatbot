# RAG2.0 Deployment Guide

This guide will help you deploy your RAG2.0 application to Azure using GitHub Actions for automated CI/CD.

## 🚀 Quick Start

### Option 1: Azure Web App (Recommended)
- **Best for**: Web applications with continuous deployment
- **Cost**: Pay-per-use with free tier available
- **Features**: Auto-scaling, SSL certificates, custom domains

### Option 2: Azure Container Instances
- **Best for**: Simple container deployments
- **Cost**: Pay-per-second
- **Features**: Serverless, no infrastructure management

## 📋 Prerequisites

1. **Azure Account** with active subscription
2. **GitHub Repository** with your RAG2.0 code
3. **Azure CLI** installed locally (optional, for manual setup)

## 🔧 Step 1: Create Azure Resources

### 1.1 Create Resource Group
```bash
az group create --name rag20-rg --location eastus
```

### 1.2 Create Azure Container Registry (ACR)
```bash
az acr create --resource-group rag20-rg --name chatbotdeveloper --sku Basic
az acr update --name chatbotdeveloper --admin-enabled true
```

### 1.3 Get ACR Credentials
```bash
az acr credential show --name chatbotdeveloper
```

### 1.4 Create Azure Web App (Option 1)
```bash
az appservice plan create --name rag20-plan --resource-group rag20-rg --sku B1 --is-linux
az webapp create --resource-group rag20-rg --plan rag20-plan --name rag20-webapp --deployment-local-git
```

### 1.5 Create Container Instance (Option 2)
```bash
# This will be handled by GitHub Actions
```

## 🔐 Step 2: Set Up GitHub Secrets

Go to your GitHub repository → Settings → Secrets and variables → Actions

### Required Secrets:

#### Azure Container Registry
- `REGISTRY_USERNAME`: Your ACR username (usually the registry name)
- `REGISTRY_PASSWORD`: Your ACR password

#### Azure Credentials
- `AZURE_CREDENTIALS`: Service principal credentials (JSON format)
- `AZURE_RESOURCE_GROUP`: Your resource group name (e.g., `rag20-rg`)

#### Application Environment Variables
- `AZURE_OPENAI_API_KEY`: Your Azure OpenAI API key
- `AZURE_OPENAI_ENDPOINT`: Your Azure OpenAI endpoint
- `AZURE_OPENAI_API_VERSION`: API version (e.g., `2024-02-15-preview`)
- `AZURE_SEARCH_SERVICE_NAME`: Your Azure Cognitive Search service name
- `AZURE_SEARCH_INDEX_NAME`: Your search index name
- `AZURE_SEARCH_API_KEY`: Your Azure Cognitive Search API key

### How to Get Azure Credentials:

1. **Create Service Principal**:
```bash
az ad sp create-for-rbac --name "rag20-github-actions" --role contributor \
    --scopes /subscriptions/{subscription-id}/resourceGroups/rag20-rg \
    --sdk-auth
```

2. **Copy the JSON output** and save it as the `AZURE_CREDENTIALS` secret

## 🚀 Step 3: Deploy

### Option A: Azure Web App (Recommended)

1. **Enable the workflow**: The `deploy-webapp.yml` workflow will run automatically on pushes to main
2. **Manual trigger**: Go to Actions tab → "Deploy to Azure Web App" → "Run workflow"

### Option B: Azure Container Instances

1. **Enable the workflow**: The `deploy.yml` workflow will run automatically on pushes to main
2. **Manual trigger**: Go to Actions tab → "Deploy to Azure Container Instances" → "Run workflow"

## 📊 Step 4: Monitor Deployment

### Check GitHub Actions
1. Go to your repository's **Actions** tab
2. Click on the latest workflow run
3. Monitor the build and deployment steps

### Check Azure Resources
1. **Azure Portal** → Resource Groups → `rag20-rg`
2. **Web App**: Check the `rag20-webapp` resource
3. **Container Instances**: Check for running containers

## 🌐 Step 5: Access Your Application

### Web App URL
```
https://rag20-webapp.azurewebsites.net
```

### Container Instance URL
```
https://rag20-app-{commit-sha}.eastus.azurecontainer.io
```

## 🔧 Configuration

### Environment Variables
The application uses these environment variables:

| Variable | Description | Required |
|----------|-------------|----------|
| `AZURE_OPENAI_API_KEY` | Azure OpenAI API key | Yes |
| `AZURE_OPENAI_ENDPOINT` | Azure OpenAI endpoint | Yes |
| `AZURE_OPENAI_API_VERSION` | API version | Yes |
| `AZURE_SEARCH_SERVICE_NAME` | Cognitive Search service name | Yes |
| `AZURE_SEARCH_INDEX_NAME` | Search index name | Yes |
| `AZURE_SEARCH_API_KEY` | Cognitive Search API key | Yes |
| `WEBSITES_PORT` | Port for web app (default: 3000) | No |

### Custom Domain (Optional)
1. **Azure Portal** → Web App → Custom domains
2. **Add custom domain** and configure DNS
3. **Enable SSL** certificate

## 🛠️ Troubleshooting

### Common Issues

#### 1. Build Failures
- Check Dockerfile syntax
- Verify all required files are present
- Check GitHub Actions logs for specific errors

#### 2. Deployment Failures
- Verify Azure credentials are correct
- Check resource group exists
- Ensure service principal has proper permissions

#### 3. Application Errors
- Check application logs in Azure Portal
- Verify environment variables are set correctly
- Test locally first

### Debug Commands

#### Check Web App Logs
```bash
az webapp log tail --name rag20-webapp --resource-group rag20-rg
```

#### Check Container Logs
```bash
az container logs --name rag20-container --resource-group rag20-rg
```

#### Test Application Health
```bash
curl https://rag20-webapp.azurewebsites.net/health
```

## 💰 Cost Optimization

### Web App Pricing
- **Free Tier**: 1 GB RAM, 1 CPU, 60 minutes/day
- **Basic Tier**: $13/month for 1 GB RAM, 1 CPU
- **Standard Tier**: $73/month for 1 GB RAM, 1 CPU

### Container Instances Pricing
- **Pay per second**: ~$0.000014/second for 1 CPU, 1 GB RAM
- **No free tier**

## 🔄 Continuous Deployment

The workflows are configured to:
1. **Trigger** on push to main branch
2. **Build** Docker image
3. **Push** to Azure Container Registry
4. **Deploy** to Azure service
5. **Configure** environment variables

## 📞 Support

If you encounter issues:
1. Check GitHub Actions logs
2. Review Azure resource logs
3. Test application locally
4. Verify all secrets are correctly set

## 🎯 Next Steps

1. **Set up monitoring** with Azure Application Insights
2. **Configure auto-scaling** for production workloads
3. **Set up staging environment** for testing
4. **Implement blue-green deployment** for zero-downtime updates 