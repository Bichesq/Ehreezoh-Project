# Authentication Testing Guide

## Overview

The authentication system is now fully implemented with Firebase Phone Authentication and JWT tokens.

## Endpoints

### 1. Register New User
**POST** `/api/v1/auth/register`

**Request Body:**
```json
{
  "firebase_token": "eyJhbGciOiJSUzI1NiIsImtpZCI6...",
  "full_name": "John Doe",
  "email": "john@example.com",
  "language_preference": "fr"
}
```

**Response:**
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer",
  "user": {
    "id": "uuid-here",
    "phone_number": "+237123456789",
    "full_name": "John Doe",
    "email": "john@example.com",
    "is_passenger": true,
    "is_driver": false,
    "is_verified": true
  }
}
```

---

### 2. Login Existing User
**POST** `/api/v1/auth/login`

**Request Body:**
```json
{
  "firebase_token": "eyJhbGciOiJSUzI1NiIsImtpZCI6..."
}
```

**Response:**
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer",
  "user": {
    "id": "uuid-here",
    "phone_number": "+237123456789",
    "full_name": "John Doe"
  }
}
```

---

### 3. Get Current User Profile
**GET** `/api/v1/auth/me`

**Headers:**
```
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
```

**Response:**
```json
{
  "id": "uuid-here",
  "phone_number": "+237123456789",
  "full_name": "John Doe",
  "email": "john@example.com",
  "language_preference": "fr",
  "is_passenger": true,
  "is_driver": false,
  "is_verified": true,
  "created_at": "2025-12-18T23:00:00"
}
```

---

### 4. Update User Profile
**PATCH** `/api/v1/auth/me`

**Headers:**
```
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
```

**Request Body:**
```json
{
  "full_name": "Jane Doe",
  "email": "jane@example.com",
  "language_preference": "en"
}
```

---

## Testing with Swagger UI

1. Open http://localhost:8000/api/docs
2. You'll see the new Authentication endpoints
3. Click "Authorize" button (lock icon)
4. Enter: `Bearer YOUR_JWT_TOKEN`
5. Test protected endpoints

---

## Testing Flow

### Option 1: With Real Firebase (Production)

1. **Set up Firebase in your mobile app/web client**
2. **Authenticate user with Firebase Phone Auth**
3. **Get Firebase ID token from client**
4. **Send to `/api/v1/auth/register` or `/api/v1/auth/login`**
5. **Receive JWT token**
6. **Use JWT token for all subsequent API calls**

### Option 2: Testing Without Firebase (Development)

For testing purposes, you can temporarily bypass Firebase verification:

**Create a test endpoint** (development only):

```python
# In app/api/auth.py - FOR TESTING ONLY
@router.post("/test-login")
async def test_login(phone_number: str, db: Session = Depends(get_db)):
    """TEST ONLY - Login without Firebase"""
    user = db.query(User).filter(User.phone_number == phone_number).first()
    if not user:
        # Create test user
        user = User(
            phone_number=phone_number,
            phone_hash=hash_phone_number(phone_number),
            firebase_uid=f"test_{phone_number}",
            full_name="Test User",
            is_passenger=True
        )
        db.add(user)
        db.commit()
        db.refresh(user)
    
    access_token = create_access_token(data={"sub": user.id})
    return {"access_token": access_token, "token_type": "bearer"}
```

---

## Using Protected Routes

Any endpoint can now be protected by adding the dependency:

```python
from app.core.auth import get_current_user
from app.models.user import User

@router.get("/protected-endpoint")
async def protected_route(current_user: User = Depends(get_current_user)):
    return {"message": f"Hello {current_user.full_name}!"}
```

---

## Environment Variables

Make sure these are set in `.env`:

```bash
# Firebase
FIREBASE_CREDENTIALS_PATH=./firebase-credentials.json
FIREBASE_PROJECT_ID=ehreezoh

# JWT
JWT_SECRET_KEY=your-secret-key-change-this
JWT_ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=10080  # 7 days
```

---

## Next Steps

1. ✅ Test authentication endpoints in Swagger UI
2. ✅ Integrate with mobile app/PWA frontend
3. ✅ Implement driver registration endpoint
4. ✅ Add protected ride endpoints

---

## Security Notes

- Firebase tokens are verified server-side
- JWT tokens expire after 7 days (configurable)
- Phone numbers are hashed in database
- Inactive/banned users cannot authenticate
- All protected routes require valid JWT token

---

**Status:** Authentication system fully implemented and ready for testing! 🎉
