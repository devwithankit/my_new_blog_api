from fastapi import FastAPI, Depends
from fastapi.openapi.utils import get_openapi
from fastapi.security import HTTPBearer, APIKeyHeader
from app.api.v1.auth.routes import router as auth_router
from app.api.v1.blog.routes import router as blog_router
from app.core.middleware import APIKeyMiddleware
from app.db.base import Base
from app.db.session import engine
from fastapi.staticfiles import StaticFiles 
import os
from pathlib import Path

# Import models
from app.models.user_model import User
from app.models.blog_model import Blog


def create_app() -> FastAPI:
    app = FastAPI(
        title="Blog Management API",
        version="1.0.0",
        docs_url="/docs",
        redoc_url="/redoc",
        swagger_ui_parameters={
            "persistAuthorization": True,
            "displayRequestDuration": True,
        }
    )

    # FIRST: Mount static files BEFORE adding middleware
    # Create uploads directory if it doesn't exist
    uploads_dir = Path("uploads")
    uploads_dir.mkdir(exist_ok=True)
    blog_images_dir = uploads_dir / "blog_images"
    blog_images_dir.mkdir(exist_ok=True)
    
    # Mount static files
    app.mount("/uploads", StaticFiles(directory="uploads"), name="uploads")
    
    # THEN: Add middleware (AFTER mounting static files)
    app.add_middleware(APIKeyMiddleware)
    
    # Include routers
    app.include_router(auth_router)
    app.include_router(blog_router)

    # Custom OpenAPI schema
    def custom_openapi():
        if app.openapi_schema:
            return app.openapi_schema

        openapi_schema = get_openapi(
            title="Blog Management API",
            version="1.0.0",
            description="""
            ## Blog Management API with Multi-Level Authentication
            
            ### 🔐 Authentication Flow:
            
            #### 1. **API Keys** (Required for ALL endpoints)
            - Add `accesskey` and `secretkey` in headers
            - Click "Authorize" button and add both keys
            - Access Key: `myaccesskey`
            - Secret Key: `mysecretkey`
            
            #### 2. **JWT Token** (Required for CREATE, UPDATE, DELETE operations)
            - Register a new user at `/auth/register`
            - Login at `/auth/login` to get JWT token
            - Click "Authorize" again and add Bearer token
            
            ### 📝 Notes:
            - GET endpoints only need API keys
            - POST/PUT/DELETE endpoints need API keys + JWT token
            - All requests automatically include API keys from Authorize button
            """,
            routes=app.routes,
        )

        # Security Schemes - Configured properly for Swagger
        openapi_schema["components"]["securitySchemes"] = {
            "APIKeyAccess": {
                "type": "apiKey",
                "in": "header",
                "name": "accesskey",
                "description": "Enter your Access Key: myaccesskey"
            },
            "APIKeySecret": {
                "type": "apiKey",
                "in": "header",
                "name": "secretkey",
                "description": "Enter your Secret Key: mysecretkey"
            },
            "BearerAuth": {
                "type": "http",
                "scheme": "bearer",
                "bearerFormat": "JWT",
                "description": "Enter your JWT token from login"
            }
        }

        # Apply API keys security to ALL paths by default
        openapi_schema["security"] = [
            {"APIKeyAccess": [], "APIKeySecret": []}
        ]

        # Customize security for specific endpoints
        if "paths" in openapi_schema:
            # All blog endpoints (GET, POST, PUT, DELETE) need API keys
            for path in openapi_schema["paths"]:
                if path.startswith("/blogs"):
                    for method in openapi_schema["paths"][path]:
                        # For POST, PUT, DELETE - add Bearer token requirement
                        if method in ["post", "put", "delete"]:
                            openapi_schema["paths"][path][method]["security"] = [
                                {"APIKeyAccess": [], "APIKeySecret": [], "BearerAuth": []}
                            ]
                        # For GET - only API keys needed
                        elif method == "get":
                            openapi_schema["paths"][path][method]["security"] = [
                                {"APIKeyAccess": [], "APIKeySecret": []}
                            ]
            
            # Auth endpoints also need API keys
            for path in openapi_schema["paths"]:
                if path.startswith("/auth"):
                    for method in openapi_schema["paths"][path]:
                        openapi_schema["paths"][path][method]["security"] = [
                            {"APIKeyAccess": [], "APIKeySecret": []}
                        ]

        app.openapi_schema = openapi_schema
        return app.openapi_schema

    app.openapi = custom_openapi
    return app


app = create_app()


@app.on_event("startup")
def on_startup():
    Base.metadata.create_all(bind=engine)
    print("=" * 50)
    print("✅ Blog Management API Started Successfully")
    print("=" * 50)
    print("📊 Database tables created successfully")
    print("🔑 API Keys:")
    print("   - Access Key: myaccesskey")
    print("   - Secret Key: mysecretkey")
    print("📁 Upload directory: uploads/blog_images")
    print("🌐 Swagger UI: http://localhost:8000/docs")
    print("📖 ReDoc: http://localhost:8000/redoc")
    print("=" * 50)


@app.get("/")
def root():
    return {
        "message": "Blog Management API",
        "version": "1.0.0",
        "docs": "/docs",
        "redoc": "/redoc",
        "api_keys": {
            "accesskey": "myaccesskey",
            "secretkey": "mysecretkey"
        }
    }
# from fastapi import FastAPI, Depends
# from fastapi.openapi.utils import get_openapi
# from fastapi.openapi.models import SecurityScheme, APIKey, APIKeyIn
# from fastapi.security import HTTPBearer, APIKeyHeader
# from app.api.v1.auth.routes import router as auth_router
# from app.api.v1.blog.routes import router as blog_router
# from app.core.middleware import APIKeyMiddleware
# from app.db.base import Base
# from app.db.session import engine
# from fastapi.staticfiles import StaticFiles 
# import os
# # Import models
# from app.models.user_model import User
# from app.models.blog_model import Blog


# def create_app() -> FastAPI:
#     app = FastAPI(
#         title="Blog Management API",
#         version="1.0.0",
#         docs_url="/docs",
#         redoc_url="/redoc",
#         swagger_ui_parameters={
#             "persistAuthorization": True,  # This keeps authorization across requests
#             "displayRequestDuration": True,
#         }
#     )

#     # Add middleware
#     app.add_middleware(APIKeyMiddleware)
#     # create uploads directory if not exists
#     if not os.path.exists("uploads"):
#         os.makedirs("uploads")
#     app.mount("/uploads", StaticFiles(directory="uploads"), name="uploads")
#     # Include routers
#     app.include_router(auth_router)
#     app.include_router(blog_router)

#     # Custom OpenAPI schema
#     def custom_openapi():
#         if app.openapi_schema:
#             return app.openapi_schema

#         openapi_schema = get_openapi(
#             title="Blog Management API",
#             version="1.0.0",
#             description="""
#             ## Blog Management API with Multi-Level Authentication
            
#             ### 🔐 Authentication Flow:
            
#             #### 1. **API Keys** (Required for ALL endpoints)
#             - Add `accesskey` and `secretkey` in headers
#             - Click "Authorize" button and add both keys
#             - Access Key: `myaccesskey`
#             - Secret Key: `mysecretkey`
            
#             #### 2. **JWT Token** (Required for CREATE, UPDATE, DELETE operations)
#             - Register a new user at `/auth/register`
#             - Login at `/auth/login` to get JWT token
#             - Click "Authorize" again and add Bearer token
            
#             ### 📝 Notes:
#             - GET endpoints only need API keys
#             - POST/PUT/DELETE endpoints need API keys + JWT token
#             - All requests automatically include API keys from Authorize button
#             """,
#             routes=app.routes,
#         )

#         # Security Schemes - Configured properly for Swagger
#         openapi_schema["components"]["securitySchemes"] = {
#             "APIKeyAccess": {
#                 "type": "apiKey",
#                 "in": "header",
#                 "name": "accesskey",
#                 "description": "Enter your Access Key: myaccesskey"
#             },
#             "APIKeySecret": {
#                 "type": "apiKey",
#                 "in": "header",
#                 "name": "secretkey",
#                 "description": "Enter your Secret Key: mysecretkey"
#             },
#             "BearerAuth": {
#                 "type": "http",
#                 "scheme": "bearer",
#                 "bearerFormat": "JWT",
#                 "description": "Enter your JWT token from login"
#             }
#         }

#         # Apply API keys security to ALL paths by default
#         openapi_schema["security"] = [
#             {"APIKeyAccess": [], "APIKeySecret": []}
#         ]

#         # Customize security for specific endpoints
#         if "paths" in openapi_schema:
#             # All blog endpoints (GET, POST, PUT, DELETE) need API keys
#             for path in openapi_schema["paths"]:
#                 if path.startswith("/blogs"):
#                     for method in openapi_schema["paths"][path]:
#                         # For POST, PUT, DELETE - add Bearer token requirement
#                         if method in ["post", "put", "delete"]:
#                             openapi_schema["paths"][path][method]["security"] = [
#                                 {"APIKeyAccess": [], "APIKeySecret": [], "BearerAuth": []}
#                             ]
#                         # For GET - only API keys needed
#                         elif method == "get":
#                             openapi_schema["paths"][path][method]["security"] = [
#                                 {"APIKeyAccess": [], "APIKeySecret": []}
#                             ]
            
#             # Auth endpoints also need API keys
#             for path in openapi_schema["paths"]:
#                 if path.startswith("/auth"):
#                     for method in openapi_schema["paths"][path]:
#                         openapi_schema["paths"][path][method]["security"] = [
#                             {"APIKeyAccess": [], "APIKeySecret": []}
#                         ]

#         app.openapi_schema = openapi_schema
#         return app.openapi_schema

#     app.openapi = custom_openapi
#     return app


# app = create_app()


# @app.on_event("startup")
# def on_startup():
#     Base.metadata.create_all(bind=engine)
#     print("✅ Database tables created successfully")
#     print("✅ API Keys - Access Key:", "myaccesskey")
#     print("✅ API Keys - Secret Key:", "mysecretkey")
#     print("✅ Swagger UI: http://localhost:8000/docs")


# @app.get("/")
# def root():
#     return {
#         "message": "Blog Management API",
#         "version": "1.0.0",
#         "docs": "/docs",
#         "redoc": "/redoc",
#         "api_keys": {
#             "accesskey": "myaccesskey",
#             "secretkey": "mysecretkey"
#         }
#     }