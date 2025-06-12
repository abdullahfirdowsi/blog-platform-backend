import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from typing import List
import logging
from ..core.config import settings

logger = logging.getLogger(__name__)

class EmailService:
    def __init__(self):
        self.smtp_host = settings.SMTP_HOST
        self.smtp_port = settings.SMTP_PORT
        self.smtp_username = settings.SMTP_USERNAME
        self.smtp_password = settings.SMTP_PASSWORD
        self.from_name = settings.EMAIL_FROM_NAME
        self.from_address = settings.EMAIL_FROM_ADDRESS

    async def send_email(
        self,
        to_email: str,
        subject: str,
        body: str,
        is_html: bool = False
    ) -> bool:
        """
        Send an email to the specified recipient
        """
        try:
            # Create message
            msg = MIMEMultipart('alternative')
            msg['From'] = f"{self.from_name} <{self.from_address}>"
            msg['To'] = to_email
            msg['Subject'] = subject

            # Add body to email
            if is_html:
                # Add plain text version first
                text_part = MIMEText(f"Email from {self.from_name}\n\nPlease visit the link provided in the HTML version of this email.\n\nBest regards,\n{self.from_name}", 'plain')
                msg.attach(text_part)
                # Add HTML version
                html_part = MIMEText(body, 'html')
                msg.attach(html_part)
            else:
                msg.attach(MIMEText(body, 'plain'))

            # Create SMTP session
            server = smtplib.SMTP(self.smtp_host, self.smtp_port)
            server.starttls()  # Enable TLS
            server.login(self.smtp_username, self.smtp_password)
            
            # Send email
            text = msg.as_string()
            server.sendmail(self.from_address, to_email, text)
            server.quit()
            
            logger.info(f"Email sent successfully to {to_email}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to send email to {to_email}: {str(e)}")
            return False

    async def send_password_reset_email(self, to_email: str, reset_token: str) -> bool:
        """
        Send password reset email with reset link using professional template
        """
        from app.templates.email_templates import get_password_reset_email_template
        
        reset_link = f"{settings.FRONTEND_URL}/auth/reset-password?token={reset_token}"
        subject = "Password Reset Request - Blog Platform"
        
        # Use professional template with new design
        html_body = get_password_reset_email_template(reset_link)
        
        # Plain text fallback
        text_body = f"""
Password Reset Request - Blog Platform

Hello,

You have requested to reset your password for your Blog Platform account.

Click the link below to reset your password:
{reset_link}

This link will expire in {settings.RESET_TOKEN_EXPIRE_MINUTES} minutes.

If you didn't request this password reset, please ignore this email. Your account remains secure.

---
This is an automated email from {settings.EMAIL_FROM_NAME}.
"""
        
        return await self.send_email(to_email, subject, html_body, is_html=True)
    
    async def send_password_reset_success_email(self, to_email: str) -> bool:
        """
        Send password reset success confirmation email
        """
        from app.templates.email_templates import get_password_reset_success_email_template
        
        subject = "Password Reset Successful"
        html_body = get_password_reset_success_email_template()
        
        return await self.send_email(to_email, subject, html_body, is_html=True)
    
    async def send_email_verification_email(self, to_email: str, verification_token: str) -> bool:
        """
        Send email verification email with verification link
        """
        from app.templates.email_templates import get_email_verification_template
        
        verification_link = f"{settings.FRONTEND_URL}/auth/verify-email?token={verification_token}"
        subject = f"Verify Your Email - {settings.EMAIL_FROM_NAME}"
        
        # Use professional template
        html_body = get_email_verification_template(verification_link)
        
        # Plain text fallback
        text_body = f"""
Email Verification - {settings.EMAIL_FROM_NAME}

Hello,

Thank you for registering with {settings.EMAIL_FROM_NAME}! To complete your account setup and start using our platform, please verify your email address.

Click the link below to verify your email:
{verification_link}

This link will expire in {settings.EMAIL_VERIFICATION_TOKEN_EXPIRE_MINUTES // 60} hours for your security.

If you didn't create an account with us, please ignore this email. No account was created.

---
This is an automated email from {settings.EMAIL_FROM_NAME}.
"""
        
        return await self.send_email(to_email, subject, html_body, is_html=True)
    
    async def send_email_verification_success_email(self, to_email: str) -> bool:
        """
        Send email verification success confirmation email
        """
        from app.templates.email_templates import get_email_verification_success_template
        
        subject = f"Email Verified Successfully - {settings.EMAIL_FROM_NAME}"
        html_body = get_email_verification_success_template()
        
        return await self.send_email(to_email, subject, html_body, is_html=True)

# Create a global instance
email_service = EmailService()

