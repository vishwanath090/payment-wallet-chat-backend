from fastapi import FastAPI
from fastapi.openapi.utils import get_openapi
from fastapi.middleware.cors import CORSMiddleware

from app.api.v1.auth.routes import router as auth_router
from app.api.v1.wallet.routes import router as wallet_router
from app.api.v1.profile.routes import router as profile_router
from app.api.v1.user.routes import router as user_router
from app.api.v1.chat.routes import router as chat_router

app = FastAPI(title="Payment Wallet API")

# Correct CORS configuration
origins = [
    "http://localhost:5173",   # Local dev
    "http://localhost:3000",   # Optional local React port
    "https://payment-wallet-chat-frontend.vercel.app",  # Vercel frontend (NO /login)
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

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
