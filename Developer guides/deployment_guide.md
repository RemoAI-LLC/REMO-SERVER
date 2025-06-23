# Deployment Guide

This guide covers deploying the Remo AI Assistant backend and frontend to production environments.

## Table of Contents

1. [Overview](#overview)
2. [Backend Deployment](#backend-deployment)
3. [Frontend Deployment](#frontend-deployment)
4. [Environment Configuration](#environment-configuration)
5. [Domain and SSL Setup](#domain-and-ssl-setup)
6. [Monitoring and Maintenance](#monitoring-and-maintenance)
7. [Troubleshooting](#troubleshooting)

## Overview

The Remo AI Assistant consists of two main components:

- **Backend**: FastAPI server with multi-agent orchestration
- **Frontend**: React application with TypeScript

### Deployment Options

| Platform    | Backend | Frontend | Cost        | Ease of Use |
| ----------- | ------- | -------- | ----------- | ----------- |
| **Render**  | ✅      | ✅       | Free tier   | Easy        |
| **Railway** | ✅      | ✅       | Free tier   | Easy        |
| **Vercel**  | ❌      | ✅       | Free tier   | Very Easy   |
| **Netlify** | ❌      | ✅       | Free tier   | Easy        |
| **Heroku**  | ✅      | ✅       | Paid        | Medium      |
| **AWS**     | ✅      | ✅       | Pay-per-use | Complex     |

**Recommended Stack:**

- **Backend**: Render (Free tier available)
- **Frontend**: Vercel (Free tier available)

## Backend Deployment

### Option 1: Render (Recommended)

Render provides a free tier and excellent Python support.

#### Step 1: Prepare Your Repository

Ensure your repository structure is correct:

```
REMO-SERVER/
├── app.py                 # FastAPI application
├── requirements.txt       # Python dependencies
├── .env.example          # Environment template
├── src/                  # Source code
└── README.md
```

#### Step 2: Create Render Account

1. Go to [render.com](https://render.com)
2. Sign up with GitHub
3. Connect your repository

#### Step 3: Deploy Backend

1. **Create New Web Service**

   - Click "New +" → "Web Service"
   - Connect your GitHub repository
   - Select the `REMO-SERVER` directory

2. **Configure Service**

   ```
   Name: remo-backend
   Environment: Python 3
   Build Command: pip install -r requirements.txt
   Start Command: uvicorn app:app --host 0.0.0.0 --port $PORT
   ```

3. **Set Environment Variables**

   ```
   OPENAI_API_KEY=your_openai_api_key_here
   LANGCHAIN_API_KEY=your_langsmith_key (optional)
   LANGCHAIN_PROJECT=remo-ai-assistant (optional)
   LANGCHAIN_TRACING_V2=false (optional)
   ```

4. **Deploy**
   - Click "Create Web Service"
   - Wait for build to complete
   - Your API will be available at: `https://your-app-name.onrender.com`

#### Step 4: Verify Deployment

```bash
# Test health endpoint
curl https://your-app-name.onrender.com/health

# Test chat endpoint
curl -X POST https://your-app-name.onrender.com/chat \
  -H "Content-Type: application/json" \
  -d '{"message": "Hello", "conversation_history": []}'
```

### Option 2: Railway

Railway offers a generous free tier and simple deployment.

#### Step 1: Create Railway Account

1. Go to [railway.app](https://railway.app)
2. Sign up with GitHub
3. Connect your repository

#### Step 2: Deploy Backend

1. **Create New Project**

   - Click "New Project"
   - Select "Deploy from GitHub repo"
   - Choose your repository

2. **Configure Service**

   - Select the `REMO-SERVER` directory
   - Railway will auto-detect Python

3. **Set Environment Variables**

   - Go to "Variables" tab
   - Add your environment variables

4. **Deploy**
   - Railway will automatically deploy
   - Get your URL from the "Deployments" tab

### Option 3: Heroku

Heroku requires a credit card but offers reliable deployment.

#### Step 1: Install Heroku CLI

```bash
# macOS
brew install heroku/brew/heroku

# Windows
# Download from https://devcenter.heroku.com/articles/heroku-cli
```

#### Step 2: Create Heroku App

```bash
# Login to Heroku
heroku login

# Create app
heroku create remo-backend

# Add Python buildpack
heroku buildpacks:set heroku/python
```

#### Step 3: Configure Environment

```bash
# Set environment variables
heroku config:set OPENAI_API_KEY=your_openai_api_key_here
heroku config:set LANGCHAIN_API_KEY=your_langsmith_key
heroku config:set LANGCHAIN_PROJECT=remo-ai-assistant
```

#### Step 4: Deploy

```bash
# Deploy to Heroku
git push heroku main

# Open the app
heroku open
```

### Option 4: Docker Deployment

For more control, deploy using Docker.

#### Step 1: Create Dockerfile

```dockerfile
# Dockerfile
FROM python:3.11-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements and install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Expose port
EXPOSE 8000

# Run the application
CMD ["uvicorn", "app:app", "--host", "0.0.0.0", "--port", "8000"]
```

#### Step 2: Create docker-compose.yml

```yaml
version: "3.8"

services:
  remo-backend:
    build: .
    ports:
      - "8000:8000"
    environment:
      - OPENAI_API_KEY=${OPENAI_API_KEY}
      - LANGCHAIN_API_KEY=${LANGCHAIN_API_KEY}
    volumes:
      - ./conversations:/app/conversations
      - ./reminders.json:/app/reminders.json
      - ./todos.json:/app/todos.json
```

#### Step 3: Deploy with Docker

```bash
# Build and run
docker-compose up -d

# Check logs
docker-compose logs -f
```

## Frontend Deployment

### Option 1: Vercel (Recommended)

Vercel provides the best experience for React applications.

#### Step 1: Prepare Frontend

Update your API URL in the frontend:

```typescript
// src/config/index.ts
export const config = {
  apiUrl:
    import.meta.env.VITE_API_URL || "https://your-backend-url.onrender.com",
  // ... other config
};
```

#### Step 2: Create Vercel Account

1. Go to [vercel.com](https://vercel.com)
2. Sign up with GitHub
3. Import your repository

#### Step 3: Deploy Frontend

1. **Import Project**

   - Click "New Project"
   - Import your GitHub repository
   - Select the `REMO-APP` directory

2. **Configure Build Settings**

   ```
   Framework Preset: Vite
   Build Command: npm run build:web
   Output Directory: dist
   Install Command: npm install
   ```

3. **Set Environment Variables**

   ```
   VITE_API_URL=https://your-backend-url.onrender.com
   VITE_APP_TITLE=Remo AI Assistant
   VITE_APP_VERSION=1.0.0
   ```

4. **Deploy**
   - Click "Deploy"
   - Vercel will build and deploy automatically
   - Your app will be available at: `https://your-app-name.vercel.app`

### Option 2: Netlify

Netlify offers similar features to Vercel.

#### Step 1: Create Netlify Account

1. Go to [netlify.com](https://netlify.com)
2. Sign up with GitHub
3. Connect your repository

#### Step 2: Deploy Frontend

1. **Create New Site**

   - Click "New site from Git"
   - Choose your repository
   - Select the `REMO-APP` directory

2. **Configure Build Settings**

   ```
   Build command: npm run build:web
   Publish directory: dist
   ```

3. **Set Environment Variables**

   - Go to "Site settings" → "Environment variables"
   - Add your environment variables

4. **Deploy**
   - Netlify will automatically deploy
   - Your app will be available at: `https://your-app-name.netlify.app`

### Option 3: GitHub Pages

Free hosting for static sites.

#### Step 1: Configure Build

```json
// package.json
{
  "scripts": {
    "build:web": "tsc && vite build",
    "predeploy": "npm run build:web",
    "deploy": "gh-pages -d dist"
  }
}
```

#### Step 2: Install gh-pages

```bash
npm install --save-dev gh-pages
```

#### Step 3: Deploy

```bash
# Build and deploy
npm run deploy

# Your app will be available at:
# https://your-username.github.io/your-repo-name
```

## Environment Configuration

### Backend Environment Variables

```bash
# Required
OPENAI_API_KEY=your_openai_api_key_here

# Optional (for LangSmith tracing)
LANGCHAIN_API_KEY=your_langsmith_api_key
LANGCHAIN_PROJECT=remo-ai-assistant
LANGCHAIN_TRACING_V2=false

# Optional (for production)
DEBUG=false
HOST=0.0.0.0
PORT=8000
```

### Frontend Environment Variables

```bash
# Required
VITE_API_URL=https://your-backend-url.onrender.com

# Optional
VITE_APP_TITLE=Remo AI Assistant
VITE_APP_VERSION=1.0.0
```

### Environment File Structure

```
REMO-SERVER/
├── .env.example          # Template for environment variables
├── .env                  # Local development (gitignored)
└── app.py               # Uses environment variables

REMO-APP/
├── .env.example         # Template for environment variables
├── .env.local           # Local development (gitignored)
└── src/config/          # Configuration management
```

## Domain and SSL Setup

### Custom Domain Setup

#### Vercel (Frontend)

1. **Add Custom Domain**

   - Go to your project settings
   - Click "Domains"
   - Add your custom domain

2. **Configure DNS**
   - Add CNAME record pointing to your Vercel app
   - Wait for DNS propagation

#### Render (Backend)

1. **Add Custom Domain**

   - Go to your service settings
   - Click "Custom Domains"
   - Add your subdomain (e.g., `api.yourdomain.com`)

2. **Configure DNS**
   - Add CNAME record pointing to your Render service
   - Wait for DNS propagation

### SSL Certificate

Both Vercel and Render provide automatic SSL certificates.

## Monitoring and Maintenance

### Health Monitoring

#### Backend Health Checks

```bash
# Automated health check
curl https://your-backend-url.onrender.com/health

# Expected response
{
  "status": "healthy",
  "service": "Remo AI Assistant API",
  "version": "1.0.0"
}
```

#### Frontend Monitoring

- Vercel provides built-in analytics
- Monitor Core Web Vitals
- Track error rates and performance

### Logs and Debugging

#### Backend Logs

```bash
# Render logs
# Available in the Render dashboard

# Railway logs
railway logs

# Heroku logs
heroku logs --tail
```

#### Frontend Logs

- Browser developer tools
- Vercel function logs
- Error tracking services

### Performance Monitoring

#### Backend Performance

- Monitor response times
- Track memory usage
- Watch for errors

#### Frontend Performance

- Lighthouse scores
- Bundle size analysis
- Loading times

## Troubleshooting

### Common Issues

#### Backend Issues

**Build Failures:**

```bash
# Check requirements.txt
pip install -r requirements.txt

# Verify Python version
python --version
```

**Runtime Errors:**

```bash
# Check logs
# Verify environment variables
# Test locally first
```

**API Connection Issues:**

```bash
# Test health endpoint
curl https://your-backend-url.onrender.com/health

# Check CORS configuration
# Verify API URL in frontend
```

#### Frontend Issues

**Build Failures:**

```bash
# Clear cache
rm -rf node_modules package-lock.json
npm install

# Check TypeScript errors
npx tsc --noEmit
```

**API Connection Issues:**

```bash
# Verify API URL
# Check CORS settings
# Test API directly
```

**Deployment Issues:**

```bash
# Check build output
# Verify environment variables
# Check for TypeScript errors
```

### Debugging Steps

1. **Test Locally First**

   ```bash
   # Backend
   cd REMO-SERVER
   python app.py

   # Frontend
   cd REMO-APP
   npm run dev:web
   ```

2. **Check Environment Variables**

   ```bash
   # Verify all required variables are set
   # Check for typos in variable names
   ```

3. **Monitor Logs**

   ```bash
   # Check application logs
   # Look for error messages
   # Verify API responses
   ```

4. **Test API Endpoints**

   ```bash
   # Health check
   curl https://your-backend-url.onrender.com/health

   # Chat endpoint
   curl -X POST https://your-backend-url.onrender.com/chat \
     -H "Content-Type: application/json" \
     -d '{"message": "test", "conversation_history": []}'
   ```

### Performance Optimization

#### Backend Optimization

```python
# Enable compression
from fastapi.middleware.gzip import GZipMiddleware
app.add_middleware(GZipMiddleware)

# Add caching headers
@app.middleware("http")
async def add_cache_headers(request: Request, call_next):
    response = await call_next(request)
    response.headers["Cache-Control"] = "public, max-age=300"
    return response
```

#### Frontend Optimization

```typescript
// Lazy load components
const LazyComponent = lazy(() => import("./HeavyComponent"));

// Optimize bundle size
// Use dynamic imports
// Implement code splitting
```

## Security Best Practices

### Backend Security

1. **Environment Variables**

   - Never commit API keys to version control
   - Use secure environment variable management
   - Rotate keys regularly

2. **Input Validation**

   - Validate all input with Pydantic
   - Sanitize user input
   - Implement rate limiting

3. **CORS Configuration**
   - Configure CORS for specific domains
   - Don't use wildcard origins in production

### Frontend Security

1. **Environment Variables**

   - Only expose public variables to frontend
   - Use VITE\_ prefix for Vite variables
   - Don't expose sensitive data

2. **API Security**
   - Use HTTPS for all API calls
   - Implement proper error handling
   - Don't expose internal errors to users

## Conclusion

This deployment guide provides comprehensive instructions for deploying the Remo AI Assistant to production. The recommended stack (Render + Vercel) offers:

- **Free tier availability**
- **Easy deployment process**
- **Automatic SSL certificates**
- **Good performance**
- **Reliable uptime**

Follow the security best practices and monitoring guidelines to ensure a robust production deployment.

---

**For more detailed information, see the other developer guides in this directory.**
