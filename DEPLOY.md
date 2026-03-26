# AWS EC2 Deployment Guide

## Prerequisites
- AWS Account
- AWS CLI installed and configured
- SSH key pair

## Step 1: Launch EC2 Instance

1. Go to AWS Console → EC2 → Launch Instance
2. Choose **Amazon Linux 2** or **Ubuntu Server 22.04**
3. Select instance type: **t3.small** (minimum) or **t3.medium**
4. Configure security group:
   - SSH (22) - Your IP
   - HTTP (80) - 0.0.0.0/0
   - HTTPS (443) - 0.0.0.0/0
   - Custom TCP (8501) - 0.0.0.0/0 (Streamlit)
   - Custom TCP (8000) - 0.0.0.0/0 (API)
5. Launch and connect via SSH

## Step 2: Install Dependencies

```bash
# Update and install Python
sudo apt update && sudo apt install -y python3.11 python3-pip git

# Clone your repository
git clone <your-repo-url>
cd multi_agent_researcher

# Create virtual environment
python3 -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

## Step 3: Configure Environment Variables

```bash
# Create .env file
nano .env

# Add your API keys
TAVILY_API_KEY=your_tavily_key
GEMINI_API_KEY=your_gemini_key
```

## Step 4: Run with Systemd (Production)

```bash
# Create systemd service
sudo nano /etc/systemd/system/researcher.service

[Unit]
Description=Multi-Agent Research Assistant
After=network.target

[Service]
Type=simple
User=ubuntu
WorkingDirectory=/home/ubuntu/multi_agent_researcher
ExecStart=/home/ubuntu/multi_agent_researcher/venv/bin/streamlit run app.py --server.address 0.0.0.0 --server.port 8501
Restart=always

[Install]
WantedBy=multi-user.target
```

```bash
# Enable and start service
sudo systemctl daemon-reload
sudo systemctl enable researcher
sudo systemctl start researcher
```

## Step 5: Run API with Systemd

```bash
sudo nano /etc/systemd/system/researcher-api.service

[Unit]
Description=Multi-Agent Research API
After=network.target

[Service]
Type=simple
User=ubuntu
WorkingDirectory=/home/ubuntu/multi_agent_researcher
ExecStart=/home/ubuntu/multi_agent_researcher/venv/bin/uvicorn api.main:app --host 0.0.0.0 --port 8000
Restart=always

[Install]
WantedBy=multi-user.target
```

```bash
sudo systemctl daemon-reload
sudo systemctl enable researcher-api
sudo systemctl start researcher-api
```

## Step 6: Access Your Application

- Streamlit UI: `http://<your-ec2-ip>:8501`
- API: `http://<your-ec2-ip>:8000/docs`

## Optional: Use Gunicorn for API

```bash
pip install gunicorn

# Update service
ExecStart=/home/ubuntu/multi_agent_researcher/venv/bin/gunicorn -w 4 -k uvicorn.workers.UvicornWorker api.main:app --bind 0.0.0.0:8000
```

## Optional: Setup Nginx Reverse Proxy

```bash
sudo apt install nginx

sudo nano /etc/nginx/sites-available/researcher

server {
    listen 80;
    server_name your-domain.com;

    location / {
        proxy_pass http://localhost:8501;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }

    location /api {
        proxy_pass http://localhost:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}
```

```bash
sudo ln -s /etc/nginx/sites-available/researcher /etc/nginx/sites-enabled
sudo nginx -t
sudo systemctl restart nginx
```
