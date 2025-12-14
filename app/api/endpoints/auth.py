from fastapi import APIRouter, Depends, HTTPException, status, Request
from sqlalchemy.orm import Session
from ...db.database import get_db
from ...services.auth_service import AuthService
from ...services.google_oauth_service import GoogleOAuthService
from ...schemas.user import Token, User
from ...core.deps import get_current_active_user

router = APIRouter()


@router.get("/google")
async def google_auth():
    """Get Google OAuth authorization URL"""
    google_service = GoogleOAuthService()
    auth_url = google_service.get_authorization_url()
    return {"auth_url": auth_url}


@router.get("/google/callback")
async def google_callback(
    code: str,
    db: Session = Depends(get_db)
):
    """Handle Google OAuth callback"""
    try:
        google_service = GoogleOAuthService()
        user_info = await google_service.authenticate_with_code(code)
        
        auth_service = AuthService(db)
        user = auth_service.get_or_create_user(
            name=user_info["name"],
            oidc_sub=user_info["google_id"]
        )
        
        token = auth_service.create_access_token_for_user(user)
        
        # Возвращаем HTML страницу с автоматическим сохранением токена и редиректом
        html_content = f"""
        <!DOCTYPE html>
        <html lang="ru">
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>Авторизация успешна - T-Prep</title>
            <style>
                body {{
                    font-family: Arial, sans-serif;
                    max-width: 600px;
                    margin: 50px auto;
                    padding: 20px;
                    background-color: #f5f5f5;
                }}
                .container {{
                    background: white;
                    padding: 30px;
                    border-radius: 10px;
                    box-shadow: 0 2px 10px rgba(0,0,0,0.1);
                    text-align: center;
                }}
                .success {{
                    color: #2e7d32;
                    font-size: 18px;
                    margin-bottom: 20px;
                }}
                .loading {{
                    color: #666;
                    font-size: 14px;
                }}
                .spinner {{
                    border: 4px solid #f3f3f3;
                    border-top: 4px solid #4285f4;
                    border-radius: 50%;
                    width: 30px;
                    height: 30px;
                    animation: spin 1s linear infinite;
                    margin: 20px auto;
                }}
                @keyframes spin {{
                    0% {{ transform: rotate(0deg); }}
                    100% {{ transform: rotate(360deg); }}
                }}
            </style>
        </head>
        <body>
            <div class="container">
                <div class="success">✅ Авторизация успешна!</div>
                <p>Добро пожаловать, <strong>{user.name}</strong>!</p>
                <div class="spinner"></div>
                <div class="loading">Перенаправление на тестовую страницу...</div>
            </div>
            
            <script>
                // Сохраняем токен в localStorage
                localStorage.setItem('authToken', '{token.access_token}');
                
                // Перенаправляем на тестовую страницу через 2 секунды
                setTimeout(function() {{
                    window.location.href = '/test_web.html';
                }}, 2000);
            </script>
        </body>
        </html>
        """
        
        from fastapi.responses import HTMLResponse
        return HTMLResponse(content=html_content)
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Authentication failed: {str(e)}"
        )

@router.get("/google/callback/test")
async def google_callback(
    db: Session = Depends(get_db)
):
    """Handle Google OAuth callback"""
    try:
        google_service = MockOAuthService()
        user_info = await google_service.authenticate_with_code("code")
        
        auth_service = AuthService(db)
        user = auth_service.get_or_create_user(
            name=user_info["name"],
            oidc_sub=user_info["google_id"]
        )
        
        token = auth_service.create_access_token_for_user(user)
        
        # Возвращаем HTML страницу с автоматическим сохранением токена и редиректом
        html_content = f"""
        <!DOCTYPE html>
        <html lang="ru">
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>Авторизация успешна - T-Prep</title>
            <style>
                body {{
                    font-family: Arial, sans-serif;
                    max-width: 600px;
                    margin: 50px auto;
                    padding: 20px;
                    background-color: #f5f5f5;
                }}
                .container {{
                    background: white;
                    padding: 30px;
                    border-radius: 10px;
                    box-shadow: 0 2px 10px rgba(0,0,0,0.1);
                    text-align: center;
                }}
                .success {{
                    color: #2e7d32;
                    font-size: 18px;
                    margin-bottom: 20px;
                }}
                .loading {{
                    color: #666;
                    font-size: 14px;
                }}
                .spinner {{
                    border: 4px solid #f3f3f3;
                    border-top: 4px solid #4285f4;
                    border-radius: 50%;
                    width: 30px;
                    height: 30px;
                    animation: spin 1s linear infinite;
                    margin: 20px auto;
                }}
                @keyframes spin {{
                    0% {{ transform: rotate(0deg); }}
                    100% {{ transform: rotate(360deg); }}
                }}
            </style>
        </head>
        <body>
            <div class="container">
                <div class="success">✅ Авторизация успешна!</div>
                <p>Добро пожаловать, <strong>{user.name}</strong>!</p>
                <div class="spinner"></div>
                <div class="loading">Перенаправление на тестовую страницу...</div>
            </div>
            
            <script>
                // Сохраняем токен в localStorage
                localStorage.setItem('authToken', '{token.access_token}');
                
                // Перенаправляем на тестовую страницу через 2 секунды
                setTimeout(function() {{
                    window.location.href = '/test_web.html';
                }}, 2000);
            </script>
        </body>
        </html>
        """
        
        from fastapi.responses import HTMLResponse
        return HTMLResponse(content=html_content)
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Authentication failed: {str(e)}"
        )

@router.get("/me", response_model=User)
async def get_current_user_info(
    current_user: User = Depends(get_current_active_user)
):
    """Get current user information"""
    return current_user


@router.post("/google/android")
async def google_android_auth(
    id_token: str,
    db: Session = Depends(get_db)
):
    """Handle Google OAuth for Android app using ID token"""
    try:
        google_service = GoogleOAuthService()
        user_info = await google_service.verify_android_token(id_token)
        
        auth_service = AuthService(db)
        user = auth_service.get_or_create_user(
            name=user_info["name"],
            oidc_sub=user_info["google_id"]  # Google ID используется как OIDC sub
        )
        
        token = auth_service.create_access_token_for_user(user)
        return token
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Android authentication failed: {str(e)}"
        )


@router.post("/logout")
async def logout():
    """Logout user (client should discard token)"""
    return {"message": "Successfully logged out"}
