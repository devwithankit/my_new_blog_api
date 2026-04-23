from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from fastapi.responses import JSONResponse
from app.core.config import settings


class APIKeyMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        # Public paths that don't require API keys
        public_paths = [
            "/docs",
            "/openapi.json",
            "/redoc",
            "/favicon.ico",
            "/"
        ]
        
        # Check if path is public (including /uploads for static files)
        if (request.url.path in public_paths or 
            request.url.path.startswith("/docs") or
            request.url.path.startswith("/uploads")):  # ← ADD THIS LINE
            return await call_next(request)

        # Get API keys from headers
        access_key = request.headers.get("accesskey")
        secret_key = request.headers.get("secretkey")

        # Validate API keys
        if not access_key or not secret_key:
            return JSONResponse(
                status_code=401,
                content={
                    "success": 401,
                    "message": "Missing API Keys - Please provide accesskey and secretkey in headers",
                    "data": {}
                }
            )
        
        if access_key != settings.ACCESS_KEY or secret_key != settings.SECRET_KEY_API:
            return JSONResponse(
                status_code=401,
                content={
                    "success": 401,
                    "message": "Invalid API Keys",
                    "data": {}
                }
            )

        return await call_next(request)
# from starlette.middleware.base import BaseHTTPMiddleware
# from starlette.requests import Request
# from fastapi.responses import JSONResponse
# from app.core.config import settings


# class APIKeyMiddleware(BaseHTTPMiddleware):
#     async def dispatch(self, request: Request, call_next):
#         # Public paths that don't require API keys
#         public_paths = [
#             "/docs",
#             "/openapi.json",
#             "/redoc",
#             "/favicon.ico",
#             "/"
#         ]
        
#         # Check if path is public
#         if request.url.path in public_paths or request.url.path.startswith("/docs"):
#             return await call_next(request)

#         # Get API keys from headers
#         access_key = request.headers.get("accesskey")
#         secret_key = request.headers.get("secretkey")

#         # Validate API keys
#         if not access_key or not secret_key:
#             return JSONResponse(
#                 status_code=401,
#                 content={
#                     "success": 401,
#                     "message": "Missing API Keys - Please provide accesskey and secretkey in headers",
#                     "data": {}
#                 }
#             )
        
#         if access_key != settings.ACCESS_KEY or secret_key != settings.SECRET_KEY_API:
#             return JSONResponse(
#                 status_code=401,
#                 content={
#                     "success": 401,
#                     "message": "Invalid API Keys",
#                     "data": {}
#                 }
#             )

#         return await call_next(request)