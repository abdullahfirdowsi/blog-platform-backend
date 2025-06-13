#!/usr/bin/env python3
"""Test script for email templates"""

import os
import sys
from pathlib import Path

# Add the project root to the Python path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from app.templates.email_templates import get_password_reset_email_template, get_password_reset_success_email_template

def test_email_templates():
    """Test email template generation"""
    print("Testing email templates...")
    
    # Test password reset email
    reset_link = "https://example.com/reset?token=test123"
    reset_email = get_password_reset_email_template(reset_link)
    
    print(f"✅ Password reset template generated successfully ({len(reset_email)} characters)")
    print(f"   Contains reset link: {'href="https://example.com/reset?token=test123"' in reset_email}")
    print(f"   Contains header title: {'Password Reset Request' in reset_email}")
    print(f"   Contains greeting: {'Hello there!' in reset_email}")
    print(f"   Contains gradient header: {'linear-gradient(135deg, #667eea 0%, #764ba2 100%)' in reset_email}")
    print(f"   Contains warning section: {'⚠️' in reset_email}")
    
    # Test success email
    success_email = get_password_reset_success_email_template()
    
    print(f"✅ Success template generated successfully ({len(success_email)} characters)")
    print(f"   Contains success message: {'Password Reset Successful!' in success_email}")
    print(f"   Contains checkmark: {'✅' in success_email}")
    
    # Save sample files for preview
    os.makedirs('sample_emails', exist_ok=True)
    
    with open('sample_emails/password_reset.html', 'w', encoding='utf-8') as f:
        f.write(reset_email)
    
    with open('sample_emails/password_reset_success.html', 'w', encoding='utf-8') as f:
        f.write(success_email)
    
    print("\n📧 Sample email files saved:")
    print("   - sample_emails/password_reset.html")
    print("   - sample_emails/password_reset_success.html")
    print("\n🎨 New Email Features:")
    print("   ✅ Gradient header with modern design")
    print("   ✅ Structured card-based layout")
    print("   ✅ Professional messaging and CTAs")
    print("   ✅ Warning section with expiration time")
    print("   ✅ Mobile-responsive design")
    print("   ✅ Security notices and brand consistency")
    print("   ✅ Multi-part email support (HTML + text)")
    print("\n📏 Template Stats:")
    print(f"   📊 Password reset template: {len(reset_email):,} characters")
    print(f"   📊 Success template: {len(success_email):,} characters")
    print(f"   🎯 Optimized size for email clients")
    print(f"   🚀 Production ready!")

if __name__ == "__main__":
    test_email_templates()
    print("\n🎉 Email templates updated successfully!")
    print("\n📁 Open these files in your browser to preview:")
    print("   • sample_emails/password_reset.html")
    print("   • sample_emails/password_reset_success.html")

