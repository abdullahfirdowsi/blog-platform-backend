# Development Google OAuth Setup

## Quick Fix for Development

The current Google Client ID is not configured for localhost origins. Follow these steps to create your own development OAuth credentials:

### 1. Create Your Own Google Cloud Project

1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Click "New Project" and create a project named "Blog Platform Dev"
3. Select your new project

### 2. Enable Google Identity Services

1. Go to **APIs & Services** > **Library**
2. Search for "Google Identity Services" or "Google+ API"
3. Click **Enable**

### 3. Create OAuth 2.0 Credentials

1. Go to **APIs & Services** > **Credentials**
2. Click **Create Credentials** > **OAuth 2.0 Client IDs**
3. If prompted, configure the OAuth consent screen:
   - Choose "External" user type
   - Fill in the required fields:
     - App name: "Blog Platform Dev"
     - User support email: your email
     - Developer contact information: your email
   - Add your email to "Test users" section
4. Create the OAuth Client ID:
   - Application type: **Web application**
   - Name: "Blog Platform Dev Client"
   - **Authorized JavaScript origins**:
     - `http://localhost:4200`
     - `http://127.0.0.1:4200`
   - **Authorized redirect URIs**:
     - `http://localhost:8000/api/v1/auth/google/callback`
     - `http://127.0.0.1:8000/api/v1/auth/google/callback`

### 4. Update Your Configuration

1. Copy the **Client ID** and **Client Secret**
2. Update `.env` file:
   ```env
   GOOGLE_CLIENT_ID=your-new-client-id.apps.googleusercontent.com
   GOOGLE_CLIENT_SECRET=your-new-client-secret
   ```

3. Update frontend environment files:
   ```typescript
   // frontend/src/environments/environment.ts
   export const environment = {
     production: false,
     apiUrl: 'http://127.0.0.1:8000/api/v1',
     googleClientId: 'your-new-client-id.apps.googleusercontent.com'
   };
   ```

### 5. Restart Services

1. Restart the backend server
2. Restart the Angular dev server
3. Clear browser cache and cookies

## Alternative: Update Existing Credentials

If you have access to the existing Google Cloud project:

1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Find the project with Client ID: `329687636290-td9b17rf39nv5ksk06d5geblcplgt3uv`
3. Go to **APIs & Services** > **Credentials**
4. Edit the OAuth 2.0 Client ID
5. Add these **Authorized JavaScript origins**:
   - `http://localhost:4200`
   - `http://127.0.0.1:4200`
6. Save changes and wait 5-10 minutes for propagation

## Testing

After updating the credentials:

1. Clear browser cache and cookies
2. Try the Google Sign-In button
3. Check browser console for any remaining errors

## Expected Behavior

✅ No "origin not allowed" errors  
✅ No Cross-Origin-Opener-Policy errors  
✅ Google Sign-In popup opens successfully  
✅ User can authenticate and is redirected to /home  
✅ Backend receives valid Google ID token  
✅ Access and refresh tokens are issued  