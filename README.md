#  Chat Server
A **FastAPI-based real-time chat server** built with **MySQL** and **Redis**, deployed on **Railway**. The platform supports JWT-based authentication, WebSocket connections, and a scalable backend architecture.

##  Project Overview
This system enables:
 **JWT Authentication** for secure user access
  **Real-time messaging** between users
  **MySQL database** for persistent storage
  **Redis** for caching and session management
  **Railway deployment** with auto-deploy from GitHub

> This project demonstrates backend architecture, WebSocket integration, async database management, and cloud deployment.
## 🛠️ Tech Stack
| Technology | Purpose |
|---|---|
| Python FastAPI | Web Framework |
| MySQL | Relational Database |
| Redis | Caching / Session Management |
| Uvicorn | ASGI Server |
| Pydantic Settings | Environment Variable Management |
| JWT | Authentication |
| Railway | Cloud Deployment |

##  Project Structure
chat-server/
│── app/
│   │── main.py          ← FastAPI app entry point
│   │── config.py        ← Settings & environment variables
│   │── database.py      ← DB connection pool
│   │── models.py        ← Database models
│   │── routes/          ← API route handlers
│   └── utils/           ← Helper functions
│── requirements.txt
│── Dockerfile
└── README.md

##  Key Features

###  Authentication
- JWT-based login
- Token expiry management
- Secure password hashing

###  Chat System
- Real-time messaging
- User-to-user communication
- Message persistence in MySQL

###  Redis Integration
- Session caching
- Fast data retrieval
- Reduced DB load

###  Cloud Deployment
- Hosted on Railway
- Auto-deploy on GitHub push
- MySQL service linked via Railway Variables

##  Installation & Setup

### 1️ Clone the repository
git clone https://github.com/appadilokesh04-source/chat-server.git
cd chat-server


### 2️ Install dependencies
pip install -r requirements.txt

### 3️ Configure environment variables
Create a `.env` file in the root directory:

DB_HOST=localhost
DB_PORT=3306
DB_USER=root
DB_PASSWORD=yourpassword
DB_NAME=chatdb
SECRET_KEY=your_secret_key
ACCESS_TOKEN_EXPIRE_MINUTES=60
REDIS_HOST=localhost
REDIS_PORT=6379

### 4️ Run the application
uvicorn app.main:app --reload

App runs on: `http://127.0.0.1:8000`

##  API Docs

Once running, visit:

| Page | URL |
|---|---|
| Swagger UI | `http://127.0.0.1:8000/docs` |
| ReDoc | `http://127.0.0.1:8000/redoc` |

---

##  Deploying to Railway

### 1️ Push code to GitHub
git add .
git commit -m "your message"
git push origin main

### 2️ Add MySQL service on Railway
- Go to Railway dashboard → **New Service** → **Database** → **MySQL**

### 3️ Link MySQL variables to your app service
DB_HOST=${{MySQL.MYSQLHOST}}
DB_PORT=${{MySQL.MYSQLPORT}}
DB_USER=${{MySQL.MYSQLUSER}}
DB_PASSWORD=${{MySQL.MYSQLPASSWORD}}
DB_NAME=${{MySQL.MYSQLDATABASE}}

### 4 Generate public domain
- Go to **Settings → Networking → Generate Domain**

##  Backend Concepts Demonstrated

-  FastAPI async routing
-  JWT authentication
-  MySQL connection pooling
-  Redis caching
-  Pydantic settings & validation
-  Environment-based configuration
-  Cloud deployment with Railway


##  Author
**Lokesh Appadi**  
Backend Developer | DevOps Engineer

[![GitHub](https://img.shields.io/badge/GitHub-appadilokesh04--source-181717?style=for-the-badge&logo=github)](https://github.com/appadilokesh04-source)
