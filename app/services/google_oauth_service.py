import httpx
from typing import Dict, Any
from ..core.config import settings


class GoogleOAuthService:
    def __init__(self):
        self.client_id = settings.google_client_id
        self.client_secret = settings.google_client_secret
        self.redirect_uri = settings.google_redirect_uri
        self.android_client_id = settings.android_client_id

    def get_authorization_url(self) -> str:
        """Generate Google OAuth authorization URL"""
        scope = "openid email profile"
        auth_url = (
            f"https://accounts.google.com/o/oauth2/v2/auth?"
            f"client_id={self.client_id}&"
            f"redirect_uri={self.redirect_uri}&"
            f"scope={scope}&"
            f"response_type=code&"
            f"access_type=offline"
        )
        return auth_url

    async def exchange_code_for_token(self, code: str) -> Dict[str, Any]:
        """Exchange authorization code for access token"""
        token_url = "https://oauth2.googleapis.com/token"
        
        data = {
            "client_id": self.client_id,
            "client_secret": self.client_secret,
            "code": code,
            "grant_type": "authorization_code",
            "redirect_uri": self.redirect_uri,
        }

        async with httpx.AsyncClient() as client:
            response = await client.post(token_url, data=data)
            response.raise_for_status()
            return response.json()

    async def get_user_info(self, access_token: str) -> Dict[str, Any]:
        """Get user information from Google API"""
        user_info_url = "https://www.googleapis.com/oauth2/v2/userinfo"
        
        headers = {"Authorization": f"Bearer {access_token}"}
        
        async with httpx.AsyncClient() as client:
            response = await client.get(user_info_url, headers=headers)
            response.raise_for_status()
            return response.json()

    async def authenticate_with_code(self, code: str) -> Dict[str, Any]:
        """Complete OAuth flow with authorization code"""
        # Exchange code for token
        token_data = await self.exchange_code_for_token(code)
        access_token = token_data.get("access_token")
        
        if not access_token:
            raise ValueError("No access token received")
        
        # Get user info
        user_info = await self.get_user_info(access_token)
        
        return {
            "email": user_info.get("email"),
            "name": user_info.get("name"),
            "google_id": user_info.get("id"),
            "picture": user_info.get("picture"),
        }

    async def verify_android_token(self, id_token: str) -> Dict[str, Any]:
        """Verify Android Google ID token"""
        verify_url = "https://oauth2.googleapis.com/tokeninfo"
        
        params = {
            "id_token": id_token
        }
        
        async with httpx.AsyncClient() as client:
            response = await client.get(verify_url, params=params)
            response.raise_for_status()
            token_info = response.json()
            
            # Verify the token is for our Android app
            if token_info.get("azp") != self.android_client_id:
                raise ValueError("Invalid audience for Android token")
            
            return {
                "email": token_info.get("email"),
                "name": token_info.get("name"),
                "google_id": token_info.get("sub"),
                "picture": token_info.get("picture"),
            }

class MockOAuthService:
    def __init__(self):
        pass
    
    async def authenticate_with_code(self, code: str) -> Dict[str, Any]:
        return {
            "email": "ohtuzeyb@hi2.in",
            "name": "desantura",
            "google_id": "123",
        }