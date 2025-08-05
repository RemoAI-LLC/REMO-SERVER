# REMO-SERVER EC2 Deployment Guide

## 🚀 Quick Start (AWS Parameter Store Method)

**✅ UPDATED: This guide now uses AWS Parameter Store for secure environment variable management. No secrets are stored in code.**

### Step 1: Make Your Repository Public

```bash
# In your local repository
git add .
git commit -m "Prepare for EC2 deployment"
git push origin main
```

### Step 2: Launch EC2 Instance

1. **Launch Instance**:

   - AMI: Ubuntu 22.04 LTS
   - Instance Type: t3.medium or larger (recommended: t3.large)
   - Storage: 20GB minimum
   - Security Group: Allow ports 22 (SSH), 80 (HTTP), 443 (HTTPS), 8000 (API)

2. **Security Group Configuration**:
   ```
   SSH (22): 0.0.0.0/0
   HTTP (80): 0.0.0.0/0
   HTTPS (443): 0.0.0.0/0
   Custom TCP (8000): 0.0.0.0/0
   ```

### Step 3: Connect to EC2 and Deploy

```bash
# Connect to your EC2 instance
ssh -i your-key.pem ubuntu@your-ec2-public-ip

# Clone your repository
git clone https://github.com/your-username/your-repo-name.git
cd your-repo-name

# Make deployment script executable
chmod +x deploy.sh

# Run deployment
./deploy.sh
```

### Step 4: Set Up Environment Variables with AWS Parameter Store

#### Configure AWS CLI and Create Parameter Store Entries

```bash
# Install AWS CLI v2 (since v1 isn't available on Ubuntu 24.04)
curl "https://awscli.amazonaws.com/awscli-exe-linux-x86_64.zip" -o "awscliv2.zip"
sudo apt install unzip
unzip awscliv2.zip
sudo ./aws/install

# Configure AWS credentials
aws configure
# Enter your AWS Access Key ID, Secret Access Key, Region (us-east-1), and output format (json)

# Test Parameter Store access
aws ssm get-parameter --name "/remo-server/AWS_ACCESS_KEY_ID" --with-decryption
```

#### Required Environment Variables to Set in AWS Parameter Store:

You need to create **15 parameters** in AWS Parameter Store with the prefix `/remo-server/`:

**AWS Configuration (3 parameters):**

1. `/remo-server/AWS_ACCESS_KEY_ID` → `SecureString` → `your-aws-access-key-id`
2. `/remo-server/AWS_SECRET_ACCESS_KEY` → `SecureString` → `your-aws-secret-access-key`
3. `/remo-server/AWS_REGION` → `String` → `us-east-1`

**Bedrock Configuration (1 parameter):** 4. `/remo-server/BEDROCK_MODEL_ID` → `String` → `amazon.nova-lite-v1:0`

**LangChain Configuration (3 parameters):** 5. `/remo-server/LANGCHAIN_API_KEY` → `SecureString` → `your-langchain-api-key` 6. `/remo-server/LANGCHAIN_PROJECT` → `String` → `AWS EC2` 7. `/remo-server/LANGCHAIN_TRACING_V2` → `String` → `true`

**DynamoDB Configuration (1 parameter):** 8. `/remo-server/DYNAMODB_TABLE_NAME` → `String` → `remo-user-data`

**Server Configuration (3 parameters):** 9. `/remo-server/HOST` → `String` → `0.0.0.0` 10. `/remo-server/PORT` → `String` → `8000` 11. `/remo-server/DEBUG` → `String` → `true`

**Google OAuth Configuration (3 parameters):** 12. `/remo-server/GOOGLE_CLIENT_ID` → `SecureString` → `your-google-client-id` 13. `/remo-server/GOOGLE_CLIENT_SECRET` → `SecureString` → `your-google-client-secret` 14. `/remo-server/GOOGLE_REDIRECT_URI` → `String` → `http://app.hireremo.com/auth/google/callback`

**OpenAI Configuration (1 parameter):** 15. `/remo-server/OPENAI_API_KEY` → `SecureString` → `your-openai-api-key`

### Step 5: Update Google OAuth Redirect URI

1. Go to Google Cloud Console
2. Update your OAuth redirect URI to: `http://your-ec2-public-ip:8000/auth/google/callback`
3. Make sure this matches the GOOGLE_REDIRECT_URI in your Parameter Store

### Step 6: Test Your Deployment

```bash
# Check if the service is running
sudo systemctl status remo-server

# View logs
sudo journalctl -u remo-server -f

# Test the API
curl http://localhost:8000/health

# Test from external network
curl http://your-ec2-public-ip:8000/health
```

## 🔧 Manual Deployment (Alternative)

If you prefer manual deployment:

```bash
# Update system
sudo apt-get update && sudo apt-get upgrade -y

# Install Python 3.12 (available on Ubuntu 24.04)
sudo apt-get install -y python3.12 python3.12-venv python3.12-dev python3-pip

# Install system dependencies
sudo apt-get install -y build-essential libssl-dev libffi-dev python3-dev

# Clone repository
git clone https://github.com/your-username/your-repo-name.git
cd your-repo-name

# Create virtual environment
python3.12 -m venv venv
source venv/bin/activate

# Install dependencies
pip install --upgrade pip
pip install -r requirements.txt

# Set up environment variables with Parameter Store
curl "https://awscli.amazonaws.com/awscli-exe-linux-x86_64.zip" -o "awscliv2.zip"
sudo apt install unzip
unzip awscliv2.zip
sudo ./aws/install
aws configure

# Run the application
python app.py
```

## 🌐 Production Setup with Nginx (Optional)

For production with domain name and SSL:

```bash
# Install Nginx
sudo apt-get install nginx

# Create Nginx configuration
sudo nano /etc/nginx/sites-available/remo-server

# Add this configuration:
server {
    listen 80;
    server_name your-domain.com;

    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}

# Enable the site
sudo ln -s /etc/nginx/sites-available/remo-server /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl restart nginx

# Install SSL with Let's Encrypt
sudo apt-get install certbot python3-certbot-nginx
sudo certbot --nginx -d your-domain.com
```

## 🔍 Troubleshooting

### Common Issues:

1. **Port 8000 not accessible**:

   ```bash
   # Check if service is running
   sudo systemctl status remo-server

   # Check if port is listening
   sudo netstat -tlnp | grep 8000

   # Check firewall
   sudo ufw status
   ```

2. **Environment variables not loading from Parameter Store**:

   ```bash
   # Test AWS connectivity
   aws sts get-caller-identity

   # Check if credentials are properly set
   aws configure list

   # Test Parameter Store access
   aws ssm get-parameter --name "/remo-server/AWS_ACCESS_KEY_ID" --with-decryption
   ```

3. **Dependencies installation fails**:

   ```bash
   # Install additional system dependencies
   sudo apt-get install -y python3-dev libpq-dev

   # Upgrade pip and retry
   pip install --upgrade pip setuptools wheel
   pip install -r requirements.txt
   ```

4. **AWS credentials issues**:

   ```bash
   # Test AWS connectivity
   aws sts get-caller-identity

   # Check if credentials are properly set
   aws configure list
   ```

## 📊 Monitoring and Logs

```bash
# View real-time logs
sudo journalctl -u remo-server -f

# View recent logs
sudo journalctl -u remo-server --since "1 hour ago"

# Check service status
sudo systemctl status remo-server

# Restart service
sudo systemctl restart remo-server
```

## 🔄 Updates and Maintenance

```bash
# Pull latest code
git pull origin main

# Restart service
sudo systemctl restart remo-server

# Check status
sudo systemctl status remo-server
```

## 🛡️ Security Best Practices

1. **Use AWS IAM roles** instead of access keys when possible
2. **Store sensitive data in Parameter Store** as SecureString
3. **Regular security updates**:
   ```bash
   sudo apt-get update && sudo apt-get upgrade -y
   ```
4. **Monitor logs** for suspicious activity
5. **Use HTTPS** in production
6. **Limit Parameter Store access** to only necessary IAM users/roles

## 📞 Support

If you encounter issues:

1. Check the logs: `sudo journalctl -u remo-server -f`
2. Verify Parameter Store entries are set correctly
3. Ensure all dependencies are installed
4. Check AWS credentials and permissions
5. Test Parameter Store access: `aws ssm get-parameter --name "/remo-server/AWS_ACCESS_KEY_ID" --with-decryption`
