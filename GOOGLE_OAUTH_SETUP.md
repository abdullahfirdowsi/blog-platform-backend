# Google OAuth Setup Guide

## 1. Create Google Cloud Project

1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Create a new project or select an existing one
3. Enable the Google+ API (or Google Identity Services)

## 2. Create OAuth 2.0 Credentials

1. Go to **APIs & Services** > **Credentials**
2. Click **Create Credentials** > **OAuth 2.0 Client IDs**
3. Choose **Web application** as the application type
4. Add these authorized origins:
   - `http://localhost:4200` (for Angular frontend)
   - `http://localhost:8000` (for backend)
5. Add these authorized redirect URIs:
   - `http://localhost:8000/api/v1/auth/google/callback`
6. Save and copy the **Client ID** and **Client Secret**

## 3. Configure Environment Variables

1. Copy `.env.example` to `.env`:
   ```bash
   cp .env.example .env
   ```

2. Update your `.env` file with the Google OAuth credentials:
   ```env
   GOOGLE_CLIENT_ID=your-actual-client-id.googleusercontent.com
   GOOGLE_CLIENT_SECRET=your-actual-client-secret
   ```

## 4. Test the Implementation

1. Start your backend server:
   ```bash
   python main.py
   ```

2. Test the Google OAuth endpoints:
   - GET `/api/v1/auth/google` - Get Google OAuth URL
   - POST `/api/v1/auth/google` - Authenticate with Google ID token
   - GET `/api/v1/auth/google/callback` - Handle OAuth callback

## 5. Frontend Integration

For your Angular frontend, you'll need to:

1. Install Google Sign-In library:
   ```bash
   npm install @google-cloud/local-auth gapi-script
   ```

2. Configure Google Sign-In in your Angular component
3. Send the ID token to your backend's `/api/v1/auth/google` endpoint

## Available Endpoints

- **GET /api/v1/auth/google** - Initiate Google OAuth flow
- **POST /api/v1/auth/google** - Authenticate with Google ID token
- **GET /api/v1/auth/google/callback** - Handle OAuth callback (for web flow)

## Security Notes

- The Google Client Secret should never be exposed to the frontend
- ID tokens are verified server-side for security
- Users created via Google OAuth don't have passwords (OAuth-only accounts)
- Existing users can link their Google accounts

## Troubleshooting

1. **Origin mismatch error**: Make sure `http://localhost:4200` is added to authorized origins
2. **Redirect URI mismatch**: Ensure the callback URL matches exactly
3. **Invalid client error**: Double-check your Client ID and Secret in `.env`

