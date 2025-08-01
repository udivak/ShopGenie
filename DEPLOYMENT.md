# Deployment Guide for ShopGenie

This guide provides detailed instructions for deploying the ShopGenie Telegram bot on various platforms.

## Prerequisites

Before deploying, ensure you have:

1. **Telegram Bot Token** - Create a bot via @BotFather
2. **Node.js 16+** - For local development and some deployment platforms
3. **Git** - For version control and deployment

## Local Development Setup

### 1. Clone and Setup

```bash
git clone <your-repo-url>
cd ShopGenie
npm install
```

### 2. Environment Configuration

```bash
cp env.example .env
```

Edit `.env` with your configuration:
```env
TELEGRAM_BOT_TOKEN=your_bot_token_here
NODE_ENV=development
PORT=3000
```

### 3. Start Development Server

```bash
npm run dev
```

The bot will start with auto-restart on file changes.

## Cloud Deployment Options

### Option 1: Heroku (Recommended for Beginners)

#### Step 1: Install Heroku CLI
```bash
# macOS
brew install heroku/brew/heroku

# Windows
# Download from https://devcenter.heroku.com/articles/heroku-cli

# Linux
curl https://cli-assets.heroku.com/install.sh | sh
```

#### Step 2: Login and Create App
```bash
heroku login
heroku create your-shopgenie-bot
```

#### Step 3: Set Environment Variables
```bash
heroku config:set TELEGRAM_BOT_TOKEN=your_bot_token_here
heroku config:set NODE_ENV=production
```

#### Step 4: Deploy
```bash
git add .
git commit -m "Initial deployment"
git push heroku main
```

#### Step 5: Verify Deployment
```bash
heroku logs --tail
```

### Option 2: Railway

#### Step 1: Connect Repository
1. Go to [Railway.app](https://railway.app)
2. Sign in with GitHub
3. Click "New Project"
4. Select "Deploy from GitHub repo"
5. Choose your ShopGenie repository

#### Step 2: Configure Environment
1. Go to your project settings
2. Add environment variables:
   - `TELEGRAM_BOT_TOKEN`: Your bot token
   - `NODE_ENV`: production

#### Step 3: Deploy
Railway will automatically deploy when you push to your main branch.

### Option 3: Render

#### Step 1: Create Account
1. Sign up at [Render.com](https://render.com)
2. Connect your GitHub account

#### Step 2: Create Web Service
1. Click "New +" → "Web Service"
2. Connect your repository
3. Configure:
   - **Name**: shopgenie-bot
   - **Environment**: Node
   - **Build Command**: `npm install`
   - **Start Command**: `npm start`

#### Step 3: Set Environment Variables
Add in the Environment section:
- `TELEGRAM_BOT_TOKEN`: Your bot token
- `NODE_ENV`: production

#### Step 4: Deploy
Click "Create Web Service" to deploy.

### Option 4: DigitalOcean App Platform

#### Step 1: Create App
1. Go to DigitalOcean App Platform
2. Click "Create App"
3. Connect your GitHub repository

#### Step 2: Configure App
- **Source**: Your repository
- **Branch**: main
- **Build Command**: `npm install`
- **Run Command**: `npm start`

#### Step 3: Set Environment Variables
Add:
- `TELEGRAM_BOT_TOKEN`
- `NODE_ENV=production`

#### Step 4: Deploy
Click "Create Resources" to deploy.

### Option 5: VPS/Cloud Server

#### Step 1: Server Setup
```bash
# Update system
sudo apt update && sudo apt upgrade -y

# Install Node.js
curl -fsSL https://deb.nodesource.com/setup_18.x | sudo -E bash -
sudo apt-get install -y nodejs

# Install PM2
sudo npm install -g pm2
```

#### Step 2: Deploy Application
```bash
# Clone repository
git clone <your-repo-url>
cd ShopGenie

# Install dependencies
npm install

# Set up environment
cp env.example .env
nano .env  # Edit with your bot token
```

#### Step 3: Start with PM2
```bash
# Start the application
pm2 start src/index.js --name shopgenie

# Save PM2 configuration
pm2 startup
pm2 save

# Check status
pm2 status
pm2 logs shopgenie
```

#### Step 4: Set Up Nginx (Optional)
```bash
# Install Nginx
sudo apt install nginx

# Create Nginx configuration
sudo nano /etc/nginx/sites-available/shopgenie
```

Add configuration:
```nginx
server {
    listen 80;
    server_name your-domain.com;

    location / {
        proxy_pass http://localhost:3000;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection 'upgrade';
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_cache_bypass $http_upgrade;
    }
}
```

Enable site:
```bash
sudo ln -s /etc/nginx/sites-available/shopgenie /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl reload nginx
```

## Environment Variables Reference

| Variable | Required | Description | Example |
|----------|----------|-------------|---------|
| `TELEGRAM_BOT_TOKEN` | Yes | Your Telegram bot token | `123456789:ABCdefGHIjklMNOpqrsTUVwxyz` |
| `NODE_ENV` | No | Environment mode | `production` |
| `PORT` | No | Server port | `3000` |
| `ALIEXPRESS_SEARCH_URL` | No | AliExpress search URL | `https://www.aliexpress.com/wholesale` |
| `USER_AGENT` | No | Browser user agent | `Mozilla/5.0...` |
| `MAX_REQUESTS_PER_MINUTE` | No | Rate limit per user | `10` |
| `REQUEST_DELAY_MS` | No | Delay between requests | `1000` |

## SSL/HTTPS Setup

### Let's Encrypt (for VPS)
```bash
# Install Certbot
sudo apt install certbot python3-certbot-nginx

# Get certificate
sudo certbot --nginx -d your-domain.com

# Auto-renewal
sudo crontab -e
# Add: 0 12 * * * /usr/bin/certbot renew --quiet
```

### Cloudflare (for any platform)
1. Add your domain to Cloudflare
2. Update DNS to point to your server
3. Enable "Always Use HTTPS" in SSL/TLS settings

## Monitoring and Maintenance

### Health Checks
```bash
# Check if bot is running
curl https://your-domain.com/health

# Expected response:
# {"status":"OK","timestamp":"2024-01-01T12:00:00.000Z"}
```

### Logs
```bash
# Heroku
heroku logs --tail

# Railway
railway logs

# PM2
pm2 logs shopgenie

# Docker
docker logs container-name
```

### Updates
```bash
# Pull latest changes
git pull origin main

# Install dependencies
npm install

# Restart application
# For PM2:
pm2 restart shopgenie

# For Docker:
docker-compose up -d --build

# For cloud platforms:
# Usually automatic on git push
```

## Troubleshooting

### Common Issues

1. **Bot not responding**
   ```bash
   # Check logs
   pm2 logs shopgenie
   
   # Verify token
   curl -X POST https://api.telegram.org/bot<YOUR_TOKEN>/getMe
   ```

2. **Port already in use**
   ```bash
   # Find process using port
   lsof -i :3000
   
   # Kill process
   kill -9 <PID>
   ```

3. **Memory issues**
   ```bash
   # Monitor memory usage
   pm2 monit
   
   # Restart if needed
   pm2 restart shopgenie
   ```

4. **Rate limiting**
   - Check AliExpress accessibility
   - Verify user agent string
   - Add delays between requests

### Performance Optimization

1. **Enable compression**
   ```javascript
   const compression = require('compression');
   app.use(compression());
   ```

2. **Add caching**
   ```javascript
   const cache = require('memory-cache');
   // Cache search results for 5 minutes
   ```

3. **Database for persistence** (optional)
   ```javascript
   // Add MongoDB or PostgreSQL for user data
   ```

## Security Considerations

1. **Environment Variables**
   - Never commit `.env` files
   - Use secure random tokens
   - Rotate tokens regularly

2. **Rate Limiting**
   - Implement per-user limits
   - Add IP-based blocking
   - Monitor for abuse

3. **Input Validation**
   - Sanitize search queries
   - Escape HTML output
   - Validate URLs

4. **HTTPS Only**
   - Force HTTPS in production
   - Use secure headers
   - Enable HSTS

## Backup Strategy

### Code Backup
```bash
# Regular git pushes
git add .
git commit -m "Backup $(date)"
git push origin main
```

### Environment Backup
```bash
# Export environment variables
heroku config --shell > heroku.env
```

### Database Backup (if applicable)
```bash
# MongoDB
mongodump --uri="your-connection-string"

# PostgreSQL
pg_dump your-database > backup.sql
```

## Cost Optimization

### Free Tier Options
- **Heroku**: Free tier discontinued, but affordable paid plans
- **Railway**: $5/month for hobby projects
- **Render**: Free tier available
- **Vercel**: Free tier available

### Resource Monitoring
```bash
# Monitor CPU/Memory usage
htop
pm2 monit

# Check disk usage
df -h
du -sh *
```

---

For additional support, check the main README.md file or open an issue on GitHub. 