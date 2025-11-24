# WalletPay — Digital Wallet System with Realtime Messaging

WalletPay is a full-stack digital wallet and realtime communication platform built with FastAPI, PostgreSQL, React, and WebSockets.  
The application delivers secure user authentication, wallet transactions, and realtime messaging with reliable delivery and presence tracking.  
It is fully deployed on Vercel, Render, and Neon, showcasing practical experience in designing, building, and deploying a modern production-ready system.

---
## Deployment Architecture Images

### Frontend Deployment (Vercel)
<img src="https://github.com/user-attachments/assets/c622aaca-fdee-49b0-a762-34c1d27e312f" alt="Frontend Deployment" width="100%" />

### Backend Deployment (Render)
<img src="https://github.com/user-attachments/assets/409cfbd8-aa96-4b82-9a16-b283c5035232" alt="Backend Deployment" width="100%" />

### Database Deployment (NeonDB)
<img src="https://github.com/user-attachments/assets/d9584f1c-add7-49dc-891b-b98be38dcba0" alt="NeonDB Deployment" width="100%" />

---

## Production Deployments

| Component | URL |
|----------|-----|
| Frontend Application | https://payment-wallet-chat-frontend.vercel.app |
| Backend REST API | https://payment-wallet-chat-backend.onrender.com |
| API Documentation (Swagger UI) | https://payment-wallet-chat-backend.onrender.com/docs |

---
## Application Screenshots
<p align="center">
  <img src="https://github.com/user-attachments/assets/2d77433e-720f-44b3-808b-b8a5e1271912" width="48%" />
  <img src="https://github.com/user-attachments/assets/5adb315d-8aed-4a15-96fc-143c0899aa31" width="48%" />
</p>

<p align="center">
  <img src="https://github.com/user-attachments/assets/8bf534e0-37b1-40f2-ae1c-39b079532f38" width="48%" />
  <img src="https://github.com/user-attachments/assets/13fa7df3-b0f9-417c-a6f4-eaa27bdec4e5" width="48%" />
</p>

<p align="center">
  <img src="https://github.com/user-attachments/assets/97d56d51-4b02-4586-bfbf-193f80b6b710" width="48%" />
  <img src="https://github.com/user-attachments/assets/0ddec229-731c-46ed-8d08-9f770ece81d3" width="48%" />
</p>

<p align="center">
  <img src="https://github.com/user-attachments/assets/fe766650-56f8-4d7c-a710-bf55a255e51e" width="48%" />
  <img src="https://github.com/user-attachments/assets/6a5cd332-1c51-403f-b591-2b5bbc4f844f" width="48%" />
</p>

# Core Features

## Authentication & Security
- Email-based registration and login  
- Secure JWT access and refresh tokens  
- PIN-based protected actions  
- Password and PIN verification endpoints  
- Fully protected routes via dependency injection  

---

## Wallet Operations
- Add funds to wallet  
- Transfer money between users  
- Paginated transaction history
- Status and transaction-type tracking with Graphical analysis
- Strict server-side validation  

---

## Realtime Messaging
- Authenticated WebSocket channel  
- Two-way messaging between users  
- Presence tracking (online/offline)  
- Delivery and read receipts  
- Pending message delivery after reconnection  
- Chat history retrieval  

---

## Reliability & Stability
- Automatic WebSocket reconnection  
- Optimistic UI updates  
- Server-validated persistence  
- Asynchronous database operations  

---

# Technology Stack

## Frontend
- React (Vite)  
- React Query  
- Zustand  
- Axios  
- Native WebSockets  

## Backend
- FastAPI  
- SQLAlchemy (Async ORM)  
- Pydantic schemas  
- JWT authentication  
- WebSocket router  

## Infrastructure
- Vercel (Frontend hosting)  
- Render (Backend hosting)  
- Neon (Managed PostgreSQL)  

---

# API Documentation Summary

## Authentication Endpoints
| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | /auth/signup | Register a new user |
| POST | /auth/login | Authenticate and obtain tokens |
| POST | /auth/refresh | Refresh the access token |

---

## Wallet Endpoints
| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | /wallet/me | Retrieve wallet details |
| POST | /wallet/add-money | Add funds |
| POST | /wallet/transfer | Transfer money to another user |
| GET | /wallet/history | Paginated transaction history |

---

## Profile Endpoints
| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | /profile/ | Retrieve profile |
| PUT | /profile/ | Update profile |
| POST | /profile/verify-pin | Verify transaction PIN |
| POST | /profile/verify-password | Verify password |

---

## Messaging Endpoints (HTTP)
| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | /chat/users | List all users available for chat |
| GET | /chat/history/{identifier} | Retrieve two-way chat history |
| GET | /chat/all-messages | Fetch all messages |
| PUT | /chat/messages/{id}/read | Mark message as read |

---

## WebSocket Messaging

### WebSocket URL Format
wss://payment-wallet-chat-backend.onrender.com/api/v1/chat/ws/{user_email}?token=<jwt>&user_id=<id>


### Capabilities
- Realtime message send/receive  
- Delivery confirmations  
- Read receipts  
- Presence tracking  
- Automatic delivery of pending messages  

---

# Local Development Setup

## Frontend Setup
cd frontend
npm install
npm run dev


## Backend Setup
cd backend
pip install -r requirements.txt
uvicorn app.main:app --reload


---

# Deployment Guide

## Frontend Deployment (Vercel)
1. Import the GitHub repository  
2. Configure environment variables  
3. Build command:
npm run build
4. Output directory:
dist
---

## Backend Deployment (Render)
1. Deploy as a Web Service  
2. Add environment variables  
3. Start command:
gunicorn app.main:app -k uvicorn.workers.UvicornWorker -w 4

4. Connect Neon PostgreSQL database  

---
## Project Structure (Main Subfolders)

### Backend
- **backend/**
  - **app/**
    - api/ — Route handlers (auth, wallet, chat, profile)
    - core/ — Settings, security, config, dependencies
    - crud/ — Database access layer (CRUD operations)
    - db/ — Database session, initialization, migrations
    - models/ — SQLAlchemy ORM models
    - schemas/ — Pydantic request/response schemas
    - services/ — Business logic (wallet, messaging, auth)
  - Dockerfile — Backend container configuration

### Frontend
- **frontend/**
  - **src/**
    - api/ — Axios clients, API layer
    - components/ — Reusable UI components
    - pages/ — Route-level pages (Login, Wallet, Chat)
    - context/ — Global state (auth, user, theme)
  - vite.config.js — Frontend build configuration


---

# License
This project is licensed under the MIT License.
