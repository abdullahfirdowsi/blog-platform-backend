import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from config import settings
import logging

logger = logging.getLogger(__name__)

class EmailService:
    def __init__(self):
        self.smtp_server = getattr(settings, 'SMTP_SERVER', 'smtp.gmail.com')
        self.smtp_port = getattr(settings, 'SMTP_PORT', 587)
        self.smtp_username = getattr(settings, 'SMTP_USERNAME', None)
        self.smtp_password = getattr(settings, 'SMTP_PASSWORD', None)
        self.from_email = getattr(settings, 'FROM_EMAIL', self.smtp_username)
        
    async def send_password_reset_email(self, to_email: str, reset_token: str, frontend_url: str = "http://localhost:4200"):
        """Send password reset email"""
        try:
            # Create the email content
            subject = "Password Reset Request - Blog Platform"
            
            # Create reset URL
            reset_url = f"{frontend_url}/reset-password?token={reset_token}"
            
            # HTML email template
            html_content = f"""
            <!DOCTYPE html>
            <html>
            <head>
                <style>
                    body {{ font-family: Arial, sans-serif; line-height: 1.6; color: #333; }}
                    .container {{ max-width: 600px; margin: 0 auto; padding: 20px; }}
                    .header {{ background-color: #007bff; color: white; padding: 20px; text-align: center; }}
                    .content {{ padding: 20px; background-color: #f9f9f9; }}
                    .button {{ display: inline-block; padding: 12px 24px; background-color: #007bff; color: white; text-decoration: none; border-radius: 5px; margin: 20px 0; }}
                    .footer {{ padding: 20px; text-align: center; color: #666; font-size: 12px; }}
                </style>
            </head>
            <body>
                <div class="container">
                    <div class="header">
                        <h1>Password Reset Request</h1>
                    </div>
                    <div class="content">
                        <p>Hello,</p>
                        <p>You have requested to reset your password for your Blog Platform account.</p>
                        <p>Click the button below to reset your password:</p>
                        <a href="{reset_url}" class="button">Reset Password</a>
                        <p>Or copy and paste this link in your browser:</p>
                        <p><a href="{reset_url}">{reset_url}</a></p>
                        <p><strong>This link will expire in 1 hour.</strong></p>
                        <p>If you didn't request this password reset, please ignore this email.</p>
                    </div>
                    <div class="footer">
                        <p>This is an automated email from Blog Platform. Please do not reply to this email.</p>
                    </div>
                </div>
            </body>
            </html>
            """
            
            # Plain text version
            text_content = f"""
            Password Reset Request - Blog Platform
            
            Hello,
            
            You have requested to reset your password for your Blog Platform account.
            
            Click the link below to reset your password:
            {reset_url}
            
            This link will expire in 1 hour.
            
            If you didn't request this password reset, please ignore this email.
            
            ---
            This is an automated email from Blog Platform.
            """
            
            # Create message
            msg = MIMEMultipart('alternative')
            msg['Subject'] = subject
            msg['From'] = self.from_email
            msg['To'] = to_email
            
            # Create text and HTML parts
            text_part = MIMEText(text_content, 'plain')
            html_part = MIMEText(html_content, 'html')
            
            # Add parts to message
            msg.attach(text_part)
            msg.attach(html_part)
            
            # Send email if SMTP is configured
            if self.smtp_username and self.smtp_password:
                with smtplib.SMTP(self.smtp_server, self.smtp_port) as server:
                    server.starttls()
                    server.login(self.smtp_username, self.smtp_password)
                    server.send_message(msg)
                logger.info(f"Password reset email sent to {to_email}")
                return True
            else:
                # For development - just log the reset URL
                logger.warning(f"SMTP not configured. Password reset URL for {to_email}: {reset_url}")
                print(f"\n=== PASSWORD RESET EMAIL ===")
                print(f"To: {to_email}")
                print(f"Subject: {subject}")
                print(f"Reset URL: {reset_url}")
                print(f"=== END EMAIL ===\n")
                return True
                
        except Exception as e:
            logger.error(f"Failed to send password reset email to {to_email}: {str(e)}")
            return False
            
    def is_configured(self):
        """Check if email service is properly configured"""
        return bool(self.smtp_username and self.smtp_password)

# Create a singleton instance
email_service = EmailService()

