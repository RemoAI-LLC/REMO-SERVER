# REMO-SERVER EC2 Deployment Guide

## 🚀 Complete Step-by-Step Deployment Guide

This guide will walk you through deploying REMO-SERVER to an AWS EC2 instance from scratch, including cloning the repository, setting up dependencies, and running the server with screen.

---

## 📋 Prerequisites

1. **AWS EC2 Instance** running Ubuntu 24.04 LTS
2. **Security Group** configured with:
   - SSH (Port 22)
   - HTTP (Port 80)
   - HTTPS (Port 443)
   - Custom TCP (Port 8000)
3. **AWS Parameter Store** with environment variables configured
4. **SSH access** to your EC2 instance

---

## 🔧 Step 1: Connect to Your EC2 Instance

```bash
# Connect to your EC2 instance
ssh -i your-key.pem ubuntu@your-ec2-public-ip

# Example:
ssh -i remo-server-key.pem ubuntu@34.207.217.9
```

---

## 📥 Step 2: Clone the Repository

```bash
# Clone the REMO-SERVER repository
git clone https://github.com/RemoAI-LLC/REMO-SERVER.git

# Navigate to the project directory
cd REMO-SERVER

# Verify the files are present
ls -la
```

**Expected output:**

```
total 40
drwxr-xr-x 8 ubuntu ubuntu 4096 Aug  5 16:49 .
drwxr-xr-x 3 ubuntu ubuntu 4096 Aug  5 16:49 ..
drwxr-xr-x 2 ubuntu ubuntu 4096 Aug  5 16:49 scripts
drwxr-xr-x 4 ubuntu ubuntu 4096 Aug  5 16:49 src
-rw-r--r-- 1 ubuntu ubuntu 1050 Aug  5 16:49 app.py
-rw-r--r-- 1 ubuntu ubuntu 286 Aug  5 16:49 DEPLOYMENT_GUIDE.md
-rw-r--r-- 1 ubuntu ubuntu 102 Aug  5 16:49 deploy.sh
-rw-r--r-- 1 ubuntu ubuntu 39 Aug  5 16:49 requirements.txt
-rw-r--r-- 1 ubuntu ubuntu 114 Aug  5 16:49 setup_env.py
...
```

---

## 🐍 Step 3: Install Python and Dependencies

```bash
# Update system packages
sudo apt update && sudo apt upgrade -y

# Install Python 3.12 and virtual environment package
sudo apt install python3.12 python3.12-venv python3.12-dev python3-pip -y

# Install system dependencies for Python packages
sudo apt install build-essential libssl-dev libffi-dev python3-dev -y

# Verify Python installation
python3.12 --version
```

**Expected output:**

```
Python 3.12.3
```

---

## 🔧 Step 4: Install AWS CLI

```bash
# Install AWS CLI v2 (required for Ubuntu 24.04)
curl "https://awscli.amazonaws.com/awscli-exe-linux-x86_64.zip" -o "awscliv2.zip"
sudo apt install unzip -y
unzip awscliv2.zip
sudo ./aws/install

# Verify AWS CLI installation
aws --version
```

**Expected output:**

```
aws-cli/2.x.x Python/3.x.x Linux/x.x.x source/x.x.x prompt/off
```

---

## ⚙️ Step 5: Configure AWS Credentials

```bash
# Configure AWS credentials
aws configure

# Enter your credentials when prompted:
# AWS Access Key ID: [your-access-key]
# AWS Secret Access Key: [your-secret-key]
# Default region name: us-east-1
# Default output format: json

# Test AWS connectivity
aws sts get-caller-identity
```

**Expected output:**

```json
{
  "UserId": "AIDA...",
  "Account": "123456789012",
  "Arn": "arn:aws:iam::123456789012:user/your-user"
}
```

---

## 🧪 Step 6: Test Parameter Store Access

```bash
# Test if you can access Parameter Store
aws ssm get-parameter --name "/remo-server/AWS_ACCESS_KEY_ID" --with-decryption
```

**Expected output:**

```json
{
  "Parameter": {
    "Name": "/remo-server/AWS_ACCESS_KEY_ID",
    "Type": "SecureString",
    "Value": "AKIA...",
    "Version": 1,
    "LastModifiedDate": "2025-08-05T...",
    "ARN": "arn:aws:ssm:us-east-1:..."
  }
}
```

---

## 🐍 Step 7: Create Virtual Environment

```bash
# Create Python virtual environment
python3.12 -m venv venv

# Activate the virtual environment
source venv/bin/activate

# Verify activation (you should see (venv) in your prompt)
which python
```

**Expected output:**

```
/home/ubuntu/REMO-SERVER/venv/bin/python
```

---

## 📦 Step 8: Install Python Dependencies

```bash
# Make sure you're in the virtual environment (venv)
source venv/bin/activate

# Upgrade pip
pip install --upgrade pip

# Install all required packages
pip install -r requirements.txt
```

**Expected output:**

```
Collecting langchain==0.3.26
  Downloading langchain-0.3.26-py3-none-any.whl (1.0 MB)
...
Successfully installed PyYAML-6.0.2 SQLAlchemy-2.0.42 ... [many packages]
```

---

## 🧪 Step 9: Test the Application

```bash
# Make sure you're in the virtual environment
source venv/bin/activate

# Test if the app can start (this will load environment variables from Parameter Store)
python app.py
```

**Expected output:**

```
✅ Reminders table 'remo-reminders' exists
✅ Todos table 'remo-todos' exists
✅ Users table 'remo-users' exists
✅ Conversations table 'remo-conversations' exists
✅ Emails table 'remo-emails' exists
✅ Waitlist table 'remo-waitlist' exists
✅ Data Analyst Reports table 'remo-data-analyst-reports' exists
✅ All DynamoDB tables are ready
✅ Conversation context table 'remo-conversation-context' exists
INFO:     Started server process [xxxxx]
INFO:     Waiting for application startup.
INFO:     Application startup complete.
INFO:     Uvicorn running on http://0.0.0.0:8000 (Press CTRL+C to quit)
```

**Press Ctrl+C to stop the test**

---

## 📺 Step 10: Install and Configure Screen

```bash
# Install screen
sudo apt install screen -y

# Verify screen installation
screen --version
```

**Expected output:**

```
Screen version 4.09.00 (GNU) 30-Jan-22
```

---

## 🚀 Step 11: Start Server with Screen

```bash
# Create a new screen session
screen -S remo-server

# In the screen session, activate virtual environment and start server
cd REMO-SERVER
source venv/bin/activate
python app.py
```

**Expected output in screen:**

```
✅ Reminders table 'remo-reminders' exists
✅ Todos table 'remo-todos' exists
✅ Users table 'remo-users' exists
✅ Conversations table 'remo-conversations' exists
✅ Emails table 'remo-emails' exists
✅ Waitlist table 'remo-waitlist' exists
✅ Data Analyst Reports table 'remo-data-analyst-reports' exists
✅ All DynamoDB tables are ready
✅ Conversation context table 'remo-conversation-context' exists
INFO:     Started server process [xxxxx]
INFO:     Waiting for application startup.
INFO:     Application startup complete.
INFO:     Uvicorn running on http://0.0.0.0:8000 (Press CTRL+C to quit)
```

---

## 🔄 Step 12: Detach from Screen Session

**To keep the server running after you disconnect:**

1. **Detach from screen:** Press `Ctrl + A`, then `D`
2. **You should see:** `[detached from xxxxx.remo-server]`

---

## 🧪 Step 13: Test Your Server

### Test from EC2 (locally):

```bash
# Test health endpoint
curl http://localhost:8000/health
```

**Expected output:**

```json
{
  "status": "healthy",
  "timestamp": "2025-08-05T16:49:32.951051",
  "dynamodb_available": true
}
```

### Test from your local machine:

```bash
# Test from your local computer
curl http://your-ec2-public-ip:8000/health
```

**Expected output:**

```json
{
  "status": "healthy",
  "timestamp": "2025-08-05T16:49:32.951051",
  "dynamodb_available": true
}
```

---

## 📺 Screen Session Management

### List Screen Sessions:

```bash
screen -ls
```

**Expected output:**

```
There is a screen on:
        xxxxx.remo-server    (Detached)
1 Socket in /run/screen/S-ubuntu.
```

### Reattach to Screen Session:

```bash
screen -r remo-server
```

### Kill Screen Session (stops server):

```bash
screen -S remo-server -X quit
```

---

## 🌐 Your Server URLs

Once deployed, your server will be available at:

- **🏠 Main API**: `http://your-ec2-public-ip:8000/`
- **📊 Health Check**: `http://your-ec2-public-ip:8000/health`
- **📚 API Documentation**: `http://your-ec2-public-ip:8000/docs`
- **💬 Chat Endpoint**: `http://your-ec2-public-ip:8000/chat`

---

## 🔧 Troubleshooting

### If the server won't start:

1. **Check if virtual environment is activated:**

   ```bash
   which python
   # Should show: /home/ubuntu/REMO-SERVER/venv/bin/python
   ```

2. **Check if dependencies are installed:**

   ```bash
   pip list | grep fastapi
   ```

3. **Check AWS credentials:**

   ```bash
   aws sts get-caller-identity
   ```

4. **Check Parameter Store access:**
   ```bash
   aws ssm get-parameter --name "/remo-server/AWS_ACCESS_KEY_ID" --with-decryption
   ```

### If you can't access the server externally:

1. **Check if server is running:**

   ```bash
   curl http://localhost:8000/health
   ```

2. **Check if port 8000 is listening:**

   ```bash
   sudo netstat -tlnp | grep 8000
   ```

3. **Check security group** - ensure port 8000 is open

### If screen session is lost:

1. **List all sessions:**

   ```bash
   screen -ls
   ```

2. **Reattach to existing session:**

   ```bash
   screen -r remo-server
   ```

3. **If session is stuck, kill and recreate:**
   ```bash
   screen -S remo-server -X quit
   screen -S remo-server
   cd REMO-SERVER
   source venv/bin/activate
   python app.py
   ```

---

## 📝 Quick Reference Commands

```bash
# Start server in screen
screen -S remo-server
cd REMO-SERVER && source venv/bin/activate && python app.py

# Detach from screen
Ctrl + A, then D

# Reattach to screen
screen -r remo-server

# List screen sessions
screen -ls

# Kill screen session
screen -S remo-server -X quit

# Check server health
curl http://localhost:8000/health

# View server logs (when attached to screen)
# Just watch the output in the screen session

# Restart server
# 1. Kill screen session: screen -S remo-server -X quit
# 2. Create new session: screen -S remo-server
# 3. Start server: cd REMO-SERVER && source venv/bin/activate && python app.py
```

---

## ✅ Deployment Checklist

- [ ] EC2 instance running Ubuntu 24.04
- [ ] Security group allows port 8000
- [ ] Repository cloned successfully
- [ ] Python 3.12 installed
- [ ] Virtual environment created and activated
- [ ] Dependencies installed
- [ ] AWS CLI installed and configured
- [ ] Parameter Store access verified
- [ ] Server starts without errors
- [ ] Screen installed
- [ ] Server running in screen session
- [ ] Health endpoint responds
- [ ] External access working

---

## 🎉 Congratulations!

Your REMO-SERVER is now successfully deployed and running on EC2! The server will continue running even after you disconnect from SSH, thanks to the screen session.

**Your server is live at:** `http://your-ec2-public-ip:8000`

---

## 🔄 Updating the Server

To update your server with new code:

```bash
# Pull latest changes
cd REMO-SERVER
git pull origin main

# Restart the server
screen -S remo-server -X quit
screen -S remo-server
cd REMO-SERVER
source venv/bin/activate
python app.py
# Detach: Ctrl + A, then D
```

---

## 🛡️ Security Notes

1. **Keep your AWS credentials secure**
2. **Regularly update your system:** `sudo apt update && sudo apt upgrade`
3. **Monitor your server logs** for any issues
4. **Consider setting up HTTPS** for production use
5. **Use IAM roles** instead of access keys when possible

---

**Your REMO AI Assistant is now live and ready to serve users! 🚀**
