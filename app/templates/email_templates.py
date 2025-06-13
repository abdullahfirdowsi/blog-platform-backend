"""Email templates for the blog platform"""

from app.core.config import settings

def get_password_reset_email_template(reset_link: str) -> str:
    """
    Get the HTML template for password reset email
    Modern design with gradient header and structured layout
    """
    return f"""
<!DOCTYPE html>
<html>
<head>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <title>Password Reset - Blog Platform</title>
    <style>
        * {{
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }}
        body {{
            font-family: 'Inter', sans-serif;
            line-height: 1.6;
            color: #ffffff;
            background: linear-gradient(135deg, #0a0a0a 0%, #1a1a1a 50%, #0a0a0a 100%);
            margin: 0;
            padding: 20px;
        }}
        .email-container {{
            max-width: 600px;
            margin: 0 auto;
            background: rgba(17, 24, 39, 0.8);
            border-radius: 16px;
            overflow: hidden;
            box-shadow: 0 20px 25px -5px rgba(0, 0, 0, 0.3);
            border: 1px solid rgba(75, 85, 99, 0.3);
        }}
        .header {{
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            padding: 40px 30px;
            text-align: center;
            position: relative;
        }}
        .logo {{
            width: 48px;
            height: 48px;
            margin: 0 auto 20px;
            background: rgba(255, 255, 255, 0.1);
            border-radius: 12px;
            display: flex;
            align-items: center;
            justify-content: center;
        }}
        .header h1 {{
            font-size: 28px;
            font-weight: 300;
            color: #ffffff;
            margin: 0;
            letter-spacing: -0.02em;
        }}
        .header p {{
            font-size: 16px;
            color: rgba(255, 255, 255, 0.8);
            margin: 10px 0 0 0;
        }}
        .content {{
            padding: 40px 30px;
            background: rgba(31, 41, 55, 0.5);
        }}
        .greeting {{
            font-size: 18px;
            color: #d1d5db;
            margin-bottom: 20px;
        }}
        .message {{
            font-size: 16px;
            color: #9ca3af;
            margin-bottom: 30px;
            line-height: 1.6;
        }}
        .reset-button {{
            display: inline-block;
            padding: 16px 32px;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: #ffffff !important;
            text-decoration: none;
            border-radius: 12px;
            font-weight: 500;
            font-size: 16px;
            margin: 20px 0;
            transition: all 0.3s ease;
            box-shadow: 0 4px 15px rgba(102, 126, 234, 0.2);
            border: none;
        }}
        .reset-button:hover {{
            transform: translateY(-2px);
            box-shadow: 0 8px 25px rgba(102, 126, 234, 0.3);
        }}
        .link-fallback {{
            margin: 20px 0;
            padding: 20px;
            background: rgba(75, 85, 99, 0.2);
            border-radius: 8px;
            border: 1px solid rgba(75, 85, 99, 0.3);
        }}
        .link-fallback p {{
            margin: 0 0 10px 0;
            color: #9ca3af;
            font-size: 14px;
        }}
        .link-text {{
            color: #667eea;
            word-break: break-all;
            font-size: 14px;
        }}
        .warning {{
            background: rgba(239, 68, 68, 0.1);
            border: 1px solid rgba(239, 68, 68, 0.3);
            border-radius: 8px;
            padding: 16px;
            margin: 20px 0;
        }}
        .warning p {{
            color: #fca5a5;
            margin: 0;
            font-size: 14px;
            font-weight: 500;
        }}
        .footer {{
            padding: 30px;
            text-align: center;
            background: rgba(17, 24, 39, 0.8);
            border-top: 1px solid rgba(75, 85, 99, 0.3);
        }}
        .footer p {{
            color: #6b7280;
            font-size: 12px;
            margin: 5px 0;
        }}
        .security-note {{
            margin-top: 20px;
            color: #9ca3af;
            font-size: 14px;
        }}
        @media (max-width: 600px) {{
            .email-container {{
                margin: 10px;
                border-radius: 12px;
            }}
            .header {{
                padding: 30px 20px;
            }}
            .content {{
                padding: 30px 20px;
            }}
            .footer {{
                padding: 20px;
            }}
            .reset-button {{
                width: 100%;
                text-align: center;
            }}
        }}
    </style>
</head>
<body>
    <div class="email-container">
        <div class="header">
            <div class="logo">
                <svg width="24" height="24" viewBox="0 0 24 24" fill="none">
                    <rect width="24" height="24" rx="6" fill="white" opacity="0.2"/>
                    <path d="M8 9h8M8 12h6M8 15h4" stroke="white" stroke-width="1" stroke-linecap="round"/>
                </svg>
            </div>
            <h1>Password Reset Request</h1>
            <p>Secure access to your Blog Platform account</p>
        </div>
        
        <div class="content">
            <div class="greeting">Hello there!</div>
            
            <div class="message">
                You've requested to reset your password for your Blog Platform account. We're here to help you regain access securely.
            </div>
            
            <div style="text-align: center; margin: 30px 0;">
                <a href="{reset_link}" class="reset-button" target="_blank">Reset Your Password</a>
            </div>
            
            <div class="link-fallback">
                <p>If the button above doesn't work, copy and paste this link into your browser:</p>
                <div class="link-text">{reset_link}</div>
            </div>
            
            <div class="warning">
                <p>⚠️ This link will expire in {settings.RESET_TOKEN_EXPIRE_MINUTES} minutes for your security.</p>
            </div>
            
            <div class="security-note">
                <p>If you didn't request this password reset, please ignore this email. Your account remains secure.</p>
            </div>
        </div>
        
        <div class="footer">
            <p><strong>{settings.EMAIL_FROM_NAME}</strong></p>
            <p>This is an automated email. Please do not reply to this message.</p>
            <p>© 2025 {settings.EMAIL_FROM_NAME}. All rights reserved.</p>
        </div>
    </div>
</body>
</html>"""


def get_email_verification_template(verification_link: str) -> str:
    """
    Get the HTML template for email verification
    Modern design with purple gradient header matching the provided design
    """
    return f"""
<!DOCTYPE html>
<html>
<head>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <title>Verify Your Email - {settings.EMAIL_FROM_NAME}</title>
    <style>
        * {{
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }}
        body {{
            font-family: 'Inter', sans-serif;
            line-height: 1.6;
            color: #ffffff;
            background: linear-gradient(135deg, #0a0a0a 0%, #1a1a1a 50%, #0a0a0a 100%);
            margin: 0;
            padding: 20px;
        }}
        .email-container {{
            max-width: 600px;
            margin: 0 auto;
            background: rgba(17, 24, 39, 0.8);
            border-radius: 16px;
            overflow: hidden;
            box-shadow: 0 20px 25px -5px rgba(0, 0, 0, 0.3);
            border: 1px solid rgba(75, 85, 99, 0.3);
        }}
        .header {{
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            padding: 40px 30px;
            text-align: center;
            position: relative;
        }}
        .logo {{
            width: 48px;
            height: 48px;
            margin: 0 auto 20px;
            background: rgba(255, 255, 255, 0.1);
            border-radius: 12px;
            display: flex;
            align-items: center;
            justify-content: center;
        }}
        .header h1 {{
            font-size: 28px;
            font-weight: 300;
            color: #ffffff;
            margin: 0;
            letter-spacing: -0.02em;
        }}
        .header p {{
            font-size: 16px;
            color: rgba(255, 255, 255, 0.8);
            margin: 10px 0 0 0;
        }}
        .content {{
            padding: 40px 30px;
            background: rgba(31, 41, 55, 0.5);
        }}
        .greeting {{
            font-size: 18px;
            color: #d1d5db;
            margin-bottom: 20px;
        }}
        .message {{
            font-size: 16px;
            color: #9ca3af;
            margin-bottom: 30px;
            line-height: 1.6;
        }}
        .verify-button {{
            display: inline-block;
            padding: 16px 32px;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: #ffffff !important;
            text-decoration: none;
            border-radius: 12px;
            font-weight: 500;
            font-size: 16px;
            margin: 20px 0;
            transition: all 0.3s ease;
            box-shadow: 0 4px 15px rgba(102, 126, 234, 0.2);
            border: none;
        }}
        .verify-button:hover {{
            transform: translateY(-2px);
            box-shadow: 0 8px 25px rgba(102, 126, 234, 0.3);
        }}
        .link-fallback {{
            margin: 20px 0;
            padding: 20px;
            background: rgba(75, 85, 99, 0.2);
            border-radius: 8px;
            border: 1px solid rgba(75, 85, 99, 0.3);
        }}
        .link-fallback p {{
            margin: 0 0 10px 0;
            color: #9ca3af;
            font-size: 14px;
        }}
        .link-text {{
            color: #667eea;
            word-break: break-all;
            font-size: 14px;
        }}
        .warning {{
            background: rgba(239, 68, 68, 0.1);
            border: 1px solid rgba(239, 68, 68, 0.3);
            border-radius: 8px;
            padding: 16px;
            margin: 20px 0;
        }}
        .warning p {{
            color: #fca5a5;
            margin: 0;
            font-size: 14px;
            font-weight: 500;
        }}
        .footer {{
            padding: 30px;
            text-align: center;
            background: rgba(17, 24, 39, 0.8);
            border-top: 1px solid rgba(75, 85, 99, 0.3);
        }}
        .footer p {{
            color: #6b7280;
            font-size: 12px;
            margin: 5px 0;
        }}
        .security-note {{
            margin-top: 20px;
            color: #9ca3af;
            font-size: 14px;
        }}
        @media (max-width: 600px) {{
            .email-container {{
                margin: 10px;
                border-radius: 12px;
            }}
            .header {{
                padding: 30px 20px;
            }}
            .content {{
                padding: 30px 20px;
            }}
            .footer {{
                padding: 20px;
            }}
            .verify-button {{
                width: 100%;
                text-align: center;
            }}
        }}
    </style>
</head>
<body>
    <div class="email-container">
        <div class="header">
            <div class="logo">
                <svg width="24" height="24" viewBox="0 0 24 24" fill="none">
                    <rect width="20" height="16" x="2" y="4" rx="2" stroke="white" stroke-width="2" fill="none"/>
                    <path d="m2 7 8.586 5.586a2 2 0 0 0 2.828 0L22 7" stroke="white" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
                </svg>
            </div>
            <h1>Verify Your Email</h1>
            <p>Welcome to Blog Platform!</p>
        </div>
        
        <div class="content">
            <div class="greeting">Hello there!</div>
            
            <div class="message">
                Thank you for registering with Blog Platform! To complete your account setup and start using our platform, please verify your email address.
            </div>
            
            <div style="text-align: center; margin: 30px 0;">
                <a href="{verification_link}" class="verify-button" target="_blank">Verify Your Email</a>
            </div>
            
            <div class="link-fallback">
                <p>If the button above doesn't work, copy and paste this link into your browser:</p>
                <div class="link-text">{verification_link}</div>
            </div>
            
            <div class="warning">
                <p>⚠️ This verification link will expire in 24 hours for your security.</p>
            </div>
            
            <div class="security-note">
                <p>If you didn't create an account with us, please ignore this email. No account was created.</p>
            </div>
        </div>
        
        <div class="footer">
            <p><strong>Blog Platform</strong></p>
            <p>This is an automated email. Please do not reply to this message.</p>
            <p>© 2025 Blog Platform. All rights reserved.</p>
        </div>
    </div>
</body>
</html>"""


def get_email_verification_success_template() -> str:
    """
    Get the HTML template for successful email verification
    """
    return f"""
<!DOCTYPE html>
<html>
<head>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <title>Email Verified Successfully - {settings.EMAIL_FROM_NAME}</title>
    <style>
        * {{
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }}
        body {{
            font-family: 'Inter', sans-serif;
            line-height: 1.6;
            color: #ffffff;
            background: linear-gradient(135deg, #0a0a0a 0%, #1a1a1a 50%, #0a0a0a 100%);
            margin: 0;
            padding: 20px;
        }}
        .email-container {{
            max-width: 600px;
            margin: 0 auto;
            background: rgba(17, 24, 39, 0.8);
            border-radius: 16px;
            overflow: hidden;
            box-shadow: 0 20px 25px -5px rgba(0, 0, 0, 0.3);
            border: 1px solid rgba(75, 85, 99, 0.3);
        }}
        .header {{
            background: linear-gradient(135deg, #22c55e 0%, #16a34a 100%);
            padding: 40px 30px;
            text-align: center;
            position: relative;
        }}
        .logo {{
            width: 48px;
            height: 48px;
            margin: 0 auto 20px;
            background: rgba(255, 255, 255, 0.1);
            border-radius: 12px;
            display: flex;
            align-items: center;
            justify-content: center;
        }}
        .header h1 {{
            font-size: 28px;
            font-weight: 300;
            color: #ffffff;
            margin: 0;
            letter-spacing: -0.02em;
        }}
        .header p {{
            font-size: 16px;
            color: rgba(255, 255, 255, 0.8);
            margin: 10px 0 0 0;
        }}
        .content {{
            padding: 40px 30px;
            background: rgba(31, 41, 55, 0.5);
            text-align: center;
        }}
        .success-icon {{
            width: 80px;
            height: 80px;
            margin: 0 auto 30px;
            background: linear-gradient(135deg, #22c55e 0%, #16a34a 100%);
            border-radius: 50%;
            display: flex;
            align-items: center;
            justify-content: center;
            box-shadow: 0 8px 32px rgba(34, 197, 94, 0.3);
        }}
        .success-icon svg {{
            width: 40px;
            height: 40px;
            color: #ffffff;
        }}
        .greeting {{
            font-size: 18px;
            color: #d1d5db;
            margin-bottom: 20px;
        }}
        .message {{
            font-size: 16px;
            color: #9ca3af;
            margin-bottom: 30px;
            line-height: 1.6;
        }}
        .success-details {{
            background: rgba(34, 197, 94, 0.1);
            border: 1px solid rgba(34, 197, 94, 0.3);
            border-radius: 12px;
            padding: 20px;
            margin: 30px 0;
        }}
        .success-details h3 {{
            color: #22c55e;
            font-size: 16px;
            font-weight: 600;
            margin-bottom: 10px;
        }}
        .success-details p {{
            color: #86efac;
            font-size: 14px;
            margin: 0;
        }}
        .login-button {{
            display: inline-block;
            padding: 16px 32px;
            background: linear-gradient(135deg, #22c55e 0%, #16a34a 100%);
            color: #ffffff !important;
            text-decoration: none;
            border-radius: 12px;
            font-weight: 500;
            font-size: 16px;
            margin: 20px 0;
            transition: all 0.3s ease;
            box-shadow: 0 4px 15px rgba(34, 197, 94, 0.2);
            border: none;
        }}
        .login-button:hover {{
            transform: translateY(-2px);
            box-shadow: 0 8px 25px rgba(34, 197, 94, 0.3);
        }}
        .footer {{
            padding: 30px;
            text-align: center;
            background: rgba(17, 24, 39, 0.8);
            border-top: 1px solid rgba(75, 85, 99, 0.3);
        }}
        .footer p {{
            color: #6b7280;
            font-size: 12px;
            margin: 5px 0;
        }}
        @media (max-width: 600px) {{
            .email-container {{
                margin: 10px;
                border-radius: 12px;
            }}
            .header {{
                padding: 30px 20px;
            }}
            .content {{
                padding: 30px 20px;
            }}
            .footer {{
                padding: 20px;
            }}
            .login-button {{
                width: 100%;
                text-align: center;
            }}
        }}
    </style>
</head>
<body>
    <div class="email-container">
        <div class="header">
            <div class="logo">
                <svg width="24" height="24" viewBox="0 0 24 24" fill="none">
                    <path d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" stroke="white" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
                </svg>
            </div>
            <h1>Email Verified Successfully!</h1>
            <p>Your account is now active</p>
        </div>
        
        <div class="content">
            <div class="success-icon">
                <svg viewBox="0 0 20 20" fill="currentColor">
                    <path fill-rule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z" clip-rule="evenodd"/>
                </svg>
            </div>
            
            <div class="greeting">Congratulations!</div>
            
            <div class="message">
                Your email has been successfully verified. You can now enjoy full access to all {settings.EMAIL_FROM_NAME} features.
            </div>
            
            <div class="success-details">
                <h3>✅ What's next?</h3>
                <p>You can now sign in to your account and start exploring our platform. Create your first blog post and connect with our community!</p>
            </div>
            
            <div style="text-align: center; margin: 30px 0;">
                <a href="{settings.FRONTEND_URL}/auth/login" class="login-button" target="_blank">Sign In to Your Account</a>
            </div>
        </div>
        
        <div class="footer">
            <p><strong>{settings.EMAIL_FROM_NAME}</strong></p>
            <p>Welcome to our community!</p>
            <p>© 2025 {settings.EMAIL_FROM_NAME}. All rights reserved.</p>
        </div>
    </div>
</body>
</html>"""


def get_password_reset_success_email_template() -> str:
    """
    Get the HTML template for password reset success confirmation email
    Modern design matching the frontend UI with gradient header and structured layout
    """
    return f"""
<!DOCTYPE html>
<html>
<head>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <title>Password Reset Successful - {settings.EMAIL_FROM_NAME}</title>
    <style>
        * {{
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }}
        body {{
            font-family: 'Inter', sans-serif;
            line-height: 1.6;
            color: #ffffff;
            background: linear-gradient(135deg, #0a0a0a 0%, #1a1a1a 50%, #0a0a0a 100%);
            margin: 0;
            padding: 20px;
        }}
        .email-container {{
            max-width: 600px;
            margin: 0 auto;
            background: rgba(17, 24, 39, 0.8);
            border-radius: 16px;
            overflow: hidden;
            box-shadow: 0 20px 25px -5px rgba(0, 0, 0, 0.3);
            border: 1px solid rgba(75, 85, 99, 0.3);
        }}
        .header {{
            background: linear-gradient(135deg, #22c55e 0%, #16a34a 100%);
            padding: 40px 30px;
            text-align: center;
            position: relative;
        }}
        .logo {{
            width: 48px;
            height: 48px;
            margin: 0 auto 20px;
            background: rgba(255, 255, 255, 0.1);
            border-radius: 12px;
            display: flex;
            align-items: center;
            justify-content: center;
        }}
        .header h1 {{
            font-size: 28px;
            font-weight: 300;
            color: #ffffff;
            margin: 0;
            letter-spacing: -0.02em;
        }}
        .header p {{
            font-size: 16px;
            color: rgba(255, 255, 255, 0.8);
            margin: 10px 0 0 0;
        }}
        .content {{
            padding: 40px 30px;
            background: rgba(31, 41, 55, 0.5);
            text-align: center;
        }}
        .success-icon {{
            width: 80px;
            height: 80px;
            margin: 0 auto 30px;
            background: linear-gradient(135deg, #22c55e 0%, #16a34a 100%);
            border-radius: 50%;
            display: flex;
            align-items: center;
            justify-content: center;
            box-shadow: 0 8px 32px rgba(34, 197, 94, 0.3);
        }}
        .success-icon svg {{
            width: 40px;
            height: 40px;
            color: #ffffff;
        }}
        .greeting {{
            font-size: 18px;
            color: #d1d5db;
            margin-bottom: 20px;
        }}
        .message {{
            font-size: 16px;
            color: #9ca3af;
            margin-bottom: 30px;
            line-height: 1.6;
        }}
        .success-details {{
            background: rgba(34, 197, 94, 0.1);
            border: 1px solid rgba(34, 197, 94, 0.3);
            border-radius: 12px;
            padding: 20px;
            margin: 30px 0;
        }}
        .success-details h3 {{
            color: #22c55e;
            font-size: 16px;
            font-weight: 600;
            margin-bottom: 10px;
        }}
        .success-details p {{
            color: #86efac;
            font-size: 14px;
            margin: 0;
        }}
        .login-button {{
            display: inline-block;
            padding: 16px 32px;
            background: linear-gradient(135deg, #22c55e 0%, #16a34a 100%);
            color: #ffffff !important;
            text-decoration: none;
            border-radius: 12px;
            font-weight: 500;
            font-size: 16px;
            margin: 20px 0;
            transition: all 0.3s ease;
            box-shadow: 0 4px 15px rgba(34, 197, 94, 0.2);
            border: none;
        }}
        .login-button:hover {{
            transform: translateY(-2px);
            box-shadow: 0 8px 25px rgba(34, 197, 94, 0.3);
        }}
        .security-note {{
            margin-top: 30px;
            padding: 20px;
            background: rgba(75, 85, 99, 0.2);
            border-radius: 8px;
            border: 1px solid rgba(75, 85, 99, 0.3);
        }}
        .security-note h4 {{
            color: #f3f4f6;
            font-size: 14px;
            font-weight: 600;
            margin-bottom: 8px;
        }}
        .security-note p {{
            color: #9ca3af;
            font-size: 13px;
            margin: 0;
            line-height: 1.5;
        }}
        .footer {{
            padding: 30px;
            text-align: center;
            background: rgba(17, 24, 39, 0.8);
            border-top: 1px solid rgba(75, 85, 99, 0.3);
        }}
        .footer p {{
            color: #6b7280;
            font-size: 12px;
            margin: 5px 0;
        }}
        @media (max-width: 600px) {{
            .email-container {{
                margin: 10px;
                border-radius: 12px;
            }}
            .header {{
                padding: 30px 20px;
            }}
            .content {{
                padding: 30px 20px;
            }}
            .footer {{
                padding: 20px;
            }}
            .login-button {{
                width: 100%;
                text-align: center;
            }}
        }}
    </style>
</head>
<body>
    <div class="email-container">
        <div class="header">
            <div class="logo">
                <svg width="24" height="24" viewBox="0 0 24 24" fill="none">
                    <path d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" stroke="white" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
                </svg>
            </div>
            <h1>Password Successfully Updated!</h1>
            <p>Your account security has been enhanced</p>
        </div>
        
        <div class="content">
            <div class="success-icon">
                <svg viewBox="0 0 20 20" fill="currentColor">
                    <path fill-rule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z" clip-rule="evenodd"/>
                </svg>
            </div>
            
            <div class="greeting">Great news!</div>
            
            <div class="message">
                Your password has been successfully updated. Your {settings.EMAIL_FROM_NAME} account is now secure with your new password.
            </div>
            
            <div class="success-details">
                <h3>✅ What happened?</h3>
                <p>Your password was changed successfully and all previous reset tokens have been invalidated for security.</p>
            </div>
            
            <div style="text-align: center; margin: 30px 0;">
                <a href="{settings.FRONTEND_URL}/auth/login" class="login-button" target="_blank">Sign In Now</a>
            </div>
            
            <div class="security-note">
                <h4>🔐 Security Notice</h4>
                <p>If you didn't make this change, please contact our support team immediately. For your security, we recommend using a strong, unique password and enabling two-factor authentication if available.</p>
            </div>
        </div>
        
        <div class="footer">
            <p><strong>{settings.EMAIL_FROM_NAME}</strong></p>
            <p>This is an automated security notification. Please do not reply to this message.</p>
            <p>© 2025 {settings.EMAIL_FROM_NAME}. All rights reserved.</p>
        </div>
    </div>
</body>
</html>"""

