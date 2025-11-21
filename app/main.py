from fastapi import FastAPI
from fastapi.openapi.utils import get_openapi
from fastapi.middleware.cors import CORSMiddleware
from app.api.v1.auth.routes import router as auth_router
from app.api.v1.wallet.routes import router as wallet_router
from app.api.v1.profile.routes import router as profile_router
from app.api.v1.user.routes import router as user_router
app = FastAPI(title="Payment Wallet API")
from fastapi import APIRouter, Depends
from fastapi.security import OAuth2PasswordBearer
from app.core.jwt import get_current_user
from app.schemas.wallet import WalletRead
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.session import get_db
from sqlalchemy import select
from app.models.wallet import Wallet
# Create the FastAPI app
app = FastAPI(title="Payment Wallet API")

# CORS configuration
origins = [
    "http://localhost:5173",             # Local frontend
    "http://localhost:3000",             # Optional local port
    "https://payment-wallet-chat-frontend.vercel.app",  # Replace with your real Vercel URL
]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],  # Enable all HTTP methods
    allow_headers=["*"],  # Allow all headers
)

# Add this import
from app.api.v1.chat.routes import router as chat_router

# Add this to your router includes


# Include API routers
app.include_router(auth_router, prefix="/api/v1")
app.include_router(wallet_router, prefix="/api/v1")
app.include_router(profile_router, prefix="/api/v1")
app.include_router(user_router, prefix="/api/v1")
app.include_router(chat_router, prefix="/api/v1")

def custom_openapi():
    if app.openapi_schema:
        return app.openapi_schema

    openapi_schema = get_openapi(
        title="Payment Wallet API",
        version="1.0",
        routes=app.routes,
    )

    # 👉 MUST define BearerAuth
    openapi_schema["components"]["securitySchemes"] = {
        "BearerAuth": {
            "type": "http",
            "scheme": "bearer",
            "bearerFormat": "JWT"
        }
    }

    # 👉 MUST add global security
    openapi_schema["security"] = [{"BearerAuth": []}]

    app.openapi_schema = openapi_schema
    return app.openapi_schema
