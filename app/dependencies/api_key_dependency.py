from fastapi import Security, HTTPException, status, Request
from fastapi.security import APIKeyHeader
from typing import Optional

from app.core.config import settings

# Define API Key headers with auto_error=False to handle missing keys gracefully
accesskey_header = APIKeyHeader(name="accesskey", auto_error=False)
secretkey_header = APIKeyHeader(name="secretkey", auto_error=False)


async def verify_api_keys(
    request: Request,
    accesskey: Optional[str] = Security(accesskey_header),
    secretkey: Optional[str] = Security(secretkey_header),
):
    """
    Verify API keys from headers.
    This is used as a dependency for all protected endpoints.
    """
    
    # Skip for docs paths and static files
    public_paths = ["/docs", "/openapi.json", "/redoc", "/favicon.ico", "/"]
    
    # Skip static file paths (uploads)
    if (request.url.path in public_paths or 
        request.url.path.startswith("/uploads")):  # ← ADD THIS LINE
        return True
    
    # Check if keys are provided
    if not accesskey or not secretkey:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail={
                "success": 401,
                "message": "Missing API Keys - Please provide accesskey and secretkey in headers",
                "data": {}
            }
        )
    
    # Validate keys
    if accesskey != settings.ACCESS_KEY or secretkey != settings.SECRET_KEY_API:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail={
                "success": 401,
                "message": "Invalid API Keys",
                "data": {}
            }
        )
    
    return True
# from fastapi import Security, HTTPException, status, Request
# from fastapi.security import APIKeyHeader
# from typing import Optional

# from app.core.config import settings

# # Define API Key headers with auto_error=False to handle missing keys gracefully
# accesskey_header = APIKeyHeader(name="accesskey", auto_error=False)
# secretkey_header = APIKeyHeader(name="secretkey", auto_error=False)


# async def verify_api_keys(
#     request: Request,
#     accesskey: Optional[str] = Security(accesskey_header),
#     secretkey: Optional[str] = Security(secretkey_header),
# ):
#     """
#     Verify API keys from headers.
#     This is used as a dependency for all protected endpoints.
#     """
    
#     # Skip for docs paths
#     public_paths = ["/docs", "/openapi.json", "/redoc", "/favicon.ico", "/"]
    
#     if request.url.path in public_paths:
#         return True
    
#     # Check if keys are provided
#     if not accesskey or not secretkey:
#         raise HTTPException(
#             status_code=status.HTTP_401_UNAUTHORIZED,
#             detail={
#                 "success": 401,
#                 "message": "Missing API Keys - Please provide accesskey and secretkey in headers",
#                 "data": {}
#             }
#         )
    
#     # Validate keys
#     if accesskey != settings.ACCESS_KEY or secretkey != settings.SECRET_KEY_API:
#         raise HTTPException(
#             status_code=status.HTTP_401_UNAUTHORIZED,
#             detail={
#                 "success": 401,
#                 "message": "Invalid API Keys",
#                 "data": {}
#             }
#         )
    
#     return True