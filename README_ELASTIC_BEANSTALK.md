# REMO-SERVER Elastic Beanstalk Deployment Guide

## Prerequisites

1. **AWS Account** with appropriate permissions
2. **AWS CLI** installed and configured
3. **GitHub Repository** with your REMO-SERVER code
4. **AWS IAM Role** for Elastic Beanstalk

## Step 1: Prepare Your Repository

### 1.1 Your repository structure should look like this:

```
REMO-SERVER/
├── app.py
├── application.py
├── requirements.txt
├── Procfile
├── runtime.txt
├── .env                    # Your existing .env file (will be copied)
├── .ebextensions/
│   ├── 01_python.config
│   ├── 02_environment.config
│   ├── 03_packages.config
│   └── 04_env_file.config
├── .ebignore              # Excludes unnecessary files
└── src/
    └── ...
```

## Step 2: Environment Variables Setup

### Option A: Use Your Existing .env File (Recommended)

1. **Keep your existing `.env` file** in the REMO-SERVER directory
2. **Update the GOOGLE_REDIRECT_URI** in your `.env` file:
   ```
   GOOGLE_REDIRECT_URI=https://your-eb-domain.elasticbeanstalk.com/auth/google/callback
   ```
3. **The deployment will automatically copy your `.env` file** to the server

### Option B: Set Environment Variables in AWS Console

1. Go to your Elastic Beanstalk environment
2. Click "Configuration" → "Software"
3. Add these environment variables:
   ```
   AWS_REGION=us-east-1
   AWS_ACCESS_KEY_ID=your_access_key
   AWS_SECRET_ACCESS_KEY=your_secret_key
   BEDROCK_MODEL_ID=amazon.nova-lite-v1:0
   GOOGLE_CLIENT_ID=your_google_client_id
   GOOGLE_CLIENT_SECRET=your_google_client_secret
   GOOGLE_REDIRECT_URI=https://your-domain.elasticbeanstalk.com/auth/google/callback
   HOST=0.0.0.0
   PORT=8000
   DEBUG=false
   ENVIRONMENT=production
   ```

### Option C: Use AWS Systems Manager Parameter Store (Most Secure)

1. Store your secrets in AWS Systems Manager Parameter Store
2. Update your code to fetch them at runtime
3. Only store non-sensitive config in environment variables

## Step 3: Set Up AWS IAM Role

1. Go to AWS IAM Console
2. Create a new role: `aws-elasticbeanstalk-ec2-role`
3. Attach policies:
   - `AWSElasticBeanstalkWebTier`
   - `AWSElasticBeanstalkWorkerTier`
   - `AWSElasticBeanstalkMulticontainerDocker`
   - Custom policy for DynamoDB and Bedrock access

## Step 4: Deploy via AWS Console

### 4.1 Create Application

1. Go to AWS Elastic Beanstalk Console
2. Click "Create Application"
3. Enter application name: `remo-server`
4. Choose platform: `Python`
5. Platform branch: `Python 3.11`
6. Platform version: Latest

### 4.2 Configure Environment

1. Environment name: `remo-server-prod`
2. Domain: Choose a unique subdomain
3. Platform: Python 3.11
4. Application code: Upload your code or connect to GitHub

### 4.3 Configure Instance

1. Instance type: `t3.medium` (minimum for ML workloads)
2. Enable auto-scaling: Yes
3. Min instances: 1
4. Max instances: 4

## Step 5: Connect GitHub (Optional)

### 5.1 Using AWS CodePipeline

1. Go to AWS CodePipeline Console
2. Create pipeline: `remo-server-pipeline`
3. Source: GitHub (version 2)
4. Connect your GitHub repository
5. Build: Use CodeBuild or skip
6. Deploy: Elastic Beanstalk

### 5.2 Using GitHub Actions

The `.github/workflows/deploy.yml` file is already configured. Just add these secrets to your GitHub repository:

**Required Secrets:**

- `AWS_ACCESS_KEY_ID`
- `AWS_SECRET_ACCESS_KEY`
- `AWS_REGION` (optional, defaults to us-east-1)

**Optional Secrets:**

- `EB_APPLICATION_NAME` (defaults to 'remo-server')
- `EB_ENVIRONMENT_NAME` (defaults to 'remo-server-prod')

## Step 6: Manual Deployment with EB CLI

### 6.1 Install EB CLI

```bash
pip install awsebcli
```

### 6.2 Initialize EB Application

```bash
cd REMO-SERVER
eb init remo-server --platform python-3.11 --region us-east-1
```

### 6.3 Create Environment

```bash
eb create remo-server-prod --instance-type t3.medium
```

### 6.4 Set Environment Variables (if not using .env file)

```bash
eb setenv AWS_REGION=us-east-1 AWS_ACCESS_KEY_ID=your_key AWS_SECRET_ACCESS_KEY=your_secret
```

### 6.5 Deploy

```bash
eb deploy
```

## Step 7: Update Frontend Configuration

Update your REMO-APP to point to the new backend URL:

```typescript
// In your frontend configuration
const API_BASE_URL = "https://your-eb-domain.elasticbeanstalk.com";
```

## Step 8: Monitor and Scale

### 8.1 Health Checks

- Monitor application health in EB console
- Set up CloudWatch alarms
- Configure health check endpoint: `/health`

### 8.2 Auto Scaling

- CPU utilization threshold: 70%
- Memory utilization threshold: 80%
- Scale up: Add instances when threshold exceeded
- Scale down: Remove instances when below 30%

### 8.3 Logs

- View logs in EB console
- Set up CloudWatch log groups
- Monitor application errors and performance

## Troubleshooting

### Common Issues:

1. **Memory Issues**: Increase instance type to t3.large or t3.xlarge
2. **Timeout Issues**: Increase timeout in Procfile
3. **Permission Issues**: Check IAM roles and policies
4. **Environment Variables**: Ensure all required variables are set
5. **Dependencies**: Check requirements.txt for missing packages

### Debug Commands:

```bash
# View logs
eb logs

# SSH into instance
eb ssh

# Check environment
eb status

# View configuration
eb config
```

## Cost Optimization

1. **Use Spot Instances**: For non-critical workloads
2. **Right-size Instances**: Monitor usage and adjust
3. **Auto Scaling**: Scale down during low usage
4. **Reserved Instances**: For predictable workloads

## Security Considerations

1. **Use IAM Roles**: Instead of access keys
2. **VPC Configuration**: Place in private subnets
3. **Security Groups**: Restrict access
4. **HTTPS**: Enable SSL/TLS
5. **Environment Variables**: Use AWS Systems Manager Parameter Store

## Next Steps

1. Set up custom domain with Route 53
2. Configure SSL certificate
3. Set up monitoring and alerting
4. Implement CI/CD pipeline
5. Set up backup and disaster recovery
