# Angular Google OAuth Integration Guide

## The errors you're seeing are fixed by:

### 1. Backend Changes (✅ DONE)
- Updated CORS headers to include Google OAuth specific headers
- Added `Cross-Origin-Opener-Policy: same-origin-allow-popups`
- Added `Cross-Origin-Embedder-Policy: unsafe-none`

### 2. Google Cloud Console (✅ DONE)
- Added `http://localhost:4200` to Authorized JavaScript origins
- Configured proper redirect URIs

### 3. Frontend Angular Implementation

#### Install Dependencies
```bash
npm install gapi-script
```

#### Environment Configuration (environment.ts)
```typescript
export const environment = {
  production: false,
  apiUrl: 'http://localhost:8000/api/v1',
  googleClientId: '329687636290-td9b17rf39nv5ksk06d5geblcplgt3uv.apps.googleusercontent.com'
};
```

#### Google OAuth Service (google-auth.service.ts)
```typescript
import { Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { environment } from '../environments/environment';

declare const google: any;

@Injectable({
  providedIn: 'root'
})
export class GoogleAuthService {
  constructor(private http: HttpClient) {}

  async initializeGoogleSignIn() {
    return new Promise<void>((resolve) => {
      google.accounts.id.initialize({
        client_id: environment.googleClientId,
        callback: (response: any) => this.handleCredentialResponse(response),
        auto_select: false,
        cancel_on_tap_outside: true
      });
      resolve();
    });
  }

  renderSignInButton(elementId: string) {
    google.accounts.id.renderButton(
      document.getElementById(elementId),
      {
        theme: 'outline',
        size: 'large',
        width: 300
      }
    );
  }

  handleCredentialResponse(response: any) {
    // Send the ID token to your backend
    this.http.post(`${environment.apiUrl}/auth/google`, {
      token: response.credential
    }).subscribe({
      next: (result: any) => {
        console.log('Google login successful:', result);
        // Store the access token
        localStorage.setItem('access_token', result.access_token);
        // Redirect to dashboard or home page
        window.location.href = '/dashboard';
      },
      error: (error) => {
        console.error('Google login failed:', error);
      }
    });
  }

  signOut() {
    google.accounts.id.disableAutoSelect();
  }
}
```

#### Component Implementation (login.component.ts)
```typescript
import { Component, OnInit, AfterViewInit } from '@angular/core';
import { GoogleAuthService } from '../services/google-auth.service';

@Component({
  selector: 'app-login',
  template: `
    <div class="login-container">
      <h2>Login to Blog Platform</h2>
      
      <!-- Traditional Login Form -->
      <form (ngSubmit)="onLogin()">
        <input type="email" [(ngModel)]="email" placeholder="Email" required>
        <input type="password" [(ngModel)]="password" placeholder="Password" required>
        <button type="submit">Login</button>
      </form>
      
      <div class="divider">OR</div>
      
      <!-- Google Sign-In Button -->
      <div id="google-signin-button"></div>
    </div>
  `
})
export class LoginComponent implements OnInit, AfterViewInit {
  email = '';
  password = '';

  constructor(private googleAuth: GoogleAuthService) {}

  async ngOnInit() {
    await this.googleAuth.initializeGoogleSignIn();
  }

  ngAfterViewInit() {
    this.googleAuth.renderSignInButton('google-signin-button');
  }

  onLogin() {
    // Your traditional email/password login logic
  }
}
```

#### Update index.html
Add the Google Identity Services script:
```html
<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <title>Blog Platform</title>
  <base href="/">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <link rel="icon" type="image/x-icon" href="favicon.ico">
  <script src="https://accounts.google.com/gsi/client" async defer></script>
</head>
<body>
  <app-root></app-root>
</body>
</html>
```

## Testing the Fix

1. **Restart your backend server** (already running)
2. **Clear browser cache** (important for Google OAuth)
3. **Try the Google Sign-In button** in your Angular app

The errors should now be resolved:
- ✅ CORS policy error fixed
- ✅ Origin mismatch error fixed  
- ✅ Cross-Origin-Opener-Policy error fixed

## If you still see errors:

1. **Check browser console** for specific error messages
2. **Verify Google Cloud Console** has the exact origins:
   - `http://localhost:4200`
   - `http://127.0.0.1:4200`
3. **Clear browser cookies** and try again
4. **Wait 5-10 minutes** for Google Cloud changes to propagate

## Available Backend Endpoints:

- `GET /api/v1/auth/google` - Get OAuth URL (for manual flow)
- `POST /api/v1/auth/google` - Authenticate with Google ID token
- `GET /api/v1/auth/callback` - Handle OAuth callback

