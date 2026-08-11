from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import Response

class SecurityHeadersMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next) -> Response:
        response = await call_next(request)
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["X-Frame-Options"] = "DENY"
        response.headers["X-XSS-Protection"] = "1; mode=block"
        response.headers["Strict-Transport-Security"] = "max-age=31536000; includeSubDomains"
        # Content-Security-Policy is often handled in frontend/nginx, but we can set a basic one here
        # response.headers["Content-Security-Policy"] = "default-src 'self'"
        return response
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import Response

class GlobalScaleMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        # Add a simulated request edge timing
        response = await call_next(request)
        
        # In a real global scale architecture (Phase 43), this middleware would:
        # 1. Determine read-replica routing based on geolocation
        # 2. Add CDN/Edge caching hints for immutable resources
        # 3. Track cross-region latency
        
        response.headers["X-Edge-Location"] = "simulated-edge-node"
        
        # Only cache safe GET requests for global scale
        if request.method == "GET" and not response.headers.get("Cache-Control"):
            # A fallback safe cache hint (e.g. 10 seconds for edge consistency)
            response.headers["Cache-Control"] = "public, max-age=10, s-maxage=10"
            
        return response
