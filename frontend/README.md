# Ehreezoh Frontend - Next.js Web Application

> Modern web interface for the Ehreezoh mobility platform

## 🚀 Quick Start

### Prerequisites

- **Node.js:** 18.x or higher
- **Package Manager:** Yarn (recommended) or npm
- **Backend:** Ensure the backend server is running on `http://localhost:8000`

### 1. Install Dependencies

```bash
# Using Yarn (recommended)
yarn install

# Or using npm
npm install
```

### 2. Configure Environment Variables

```bash
# Copy the example environment file
copy .env.local.example .env.local

# Edit .env.local and configure:
# - Firebase credentials (for authentication)
# - API URLs (backend connection)
```

**Required Environment Variables:**

| Variable | Description | Example |
|----------|-------------|---------|
| `NEXT_PUBLIC_API_URL` | Backend API base URL | `http://localhost:8000/api/v1` |
| `NEXT_PUBLIC_WS_URL` | WebSocket URL for real-time features | `ws://localhost:8000/api/v1/ws` |
| `NEXT_PUBLIC_FIREBASE_API_KEY` | Firebase API key | Your Firebase API key |
| `NEXT_PUBLIC_FIREBASE_AUTH_DOMAIN` | Firebase auth domain | `your-project.firebaseapp.com` |
| `NEXT_PUBLIC_FIREBASE_PROJECT_ID` | Firebase project ID | `your-project-id` |
| `NEXT_PUBLIC_FIREBASE_STORAGE_BUCKET` | Firebase storage bucket | `your-project.appspot.com` |
| `NEXT_PUBLIC_FIREBASE_MESSAGING_SENDER_ID` | Firebase messaging sender ID | Your sender ID |
| `NEXT_PUBLIC_FIREBASE_APP_ID` | Firebase app ID | Your app ID |

### 3. Set Up Firebase Authentication

1. Go to [Firebase Console](https://console.firebase.google.com/)
2. Select your project (or create a new one)
3. Go to **Project Settings** (gear icon)
4. Scroll to **"Your apps"** section
5. Click **Web app** icon (`</>`)
6. Copy the configuration values to `.env.local`

**Enable Phone Authentication:**
1. In Firebase Console, go to **Authentication**
2. Click **Sign-in method** tab
3. Enable **Phone** provider
4. Add your domain to authorized domains (localhost is already there)

**Optional - Add Test Phone Numbers:**
1. Go to Authentication → Sign-in method → Phone
2. Scroll to **"Phone numbers for testing"**
3. Add test numbers with verification codes (e.g., `+237 600000000` → `123456`)
4. This allows testing without sending real SMS messages

### 4. Start Development Server

```bash
# Using Yarn
yarn dev

# Or using npm
npm run dev
```

The application will be available at: **http://localhost:3000**

---

## 📦 Available Scripts

| Script | Command | Description |
|--------|---------|-------------|
| **Development** | `yarn dev` or `npm run dev` | Start development server with hot reload |
| **Build** | `yarn build` or `npm run build` | Create production build |
| **Production** | `yarn start` or `npm start` | Start production server (requires build first) |
| **Lint** | `yarn lint` or `npm run lint` | Run ESLint to check code quality |

---

## 🛠️ Technology Stack

- **Framework:** Next.js 14.2.0 (React 18.3)
- **Language:** TypeScript 5
- **Styling:** TailwindCSS 3.4
- **HTTP Client:** Axios 1.13.2
- **Authentication:** Firebase 12.7.0
- **Build Tools:** PostCSS, Autoprefixer

---

## 📂 Project Structure

```
frontend/
├── app/                    # Next.js App Router
│   ├── layout.tsx         # Root layout component
│   ├── page.tsx           # Home page
│   └── ...                # Other pages and routes
│
├── components/            # Reusable React components
│   ├── ui/               # UI components (buttons, inputs, etc.)
│   ├── forms/            # Form components
│   └── ...               # Feature-specific components
│
├── services/             # API services and utilities
│   ├── api.ts           # Axios instance and API configuration
│   ├── firebase.ts      # Firebase configuration
│   └── ...              # Other service modules
│
├── public/              # Static assets (images, icons, etc.)
│
├── .env.local           # Environment variables (gitignored)
├── .env.local.example   # Example environment file
├── next.config.mjs      # Next.js configuration
├── tailwind.config.ts   # TailwindCSS configuration
├── tsconfig.json        # TypeScript configuration
└── package.json         # Dependencies and scripts
```

---

## 🔗 Backend Integration

The frontend connects to the FastAPI backend running on `http://localhost:8000`.

**Ensure the backend is running:**
```bash
cd ../backend
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

**API Documentation:** http://localhost:8000/api/docs

---

## 🧪 Testing

### Manual Testing Checklist

- [ ] Authentication flow (phone number login)
- [ ] API connectivity to backend
- [ ] Real-time features (WebSocket connection)
- [ ] Responsive design (mobile, tablet, desktop)
- [ ] Firebase authentication integration

### Browser Testing

Test on multiple browsers:
- Chrome/Edge (Chromium-based)
- Firefox
- Safari (if on macOS)

---

## 🐛 Troubleshooting

### Port Already in Use

If port 3000 is already in use:
```bash
# Kill the process using port 3000 (Windows)
netstat -ano | findstr :3000
taskkill /PID <PID> /F

# Or use a different port
yarn dev -p 3001
```

### Firebase Authentication Not Working

1. Check that all Firebase environment variables are set correctly
2. Verify that Phone authentication is enabled in Firebase Console
3. Ensure your domain is in the authorized domains list
4. Check browser console for detailed error messages

### Backend Connection Failed

1. Verify backend is running: http://localhost:8000/api/docs
2. Check `NEXT_PUBLIC_API_URL` in `.env.local`
3. Ensure no CORS issues (backend should allow localhost:3000)
4. Check browser console for network errors

### Build Errors

```bash
# Clear Next.js cache
rm -rf .next

# Reinstall dependencies
rm -rf node_modules
yarn install

# Try building again
yarn build
```

---

## 🌍 Environment-Specific Configuration

### Development
- Uses `.env.local` for environment variables
- Hot reload enabled
- Source maps enabled for debugging

### Production
- Requires `yarn build` before `yarn start`
- Optimized bundle size
- Environment variables must be set on hosting platform

---

## 📚 Additional Resources

- **Next.js Documentation:** https://nextjs.org/docs
- **React Documentation:** https://react.dev
- **TailwindCSS Documentation:** https://tailwindcss.com/docs
- **Firebase Documentation:** https://firebase.google.com/docs
- **TypeScript Documentation:** https://www.typescriptlang.org/docs

---

## 🔒 Security Notes

- **Never commit `.env.local`** - It contains sensitive credentials
- **API keys are public** - Next.js `NEXT_PUBLIC_*` variables are exposed to the browser
- **Use Firebase security rules** - Protect your Firebase resources
- **Backend authentication** - Always validate requests on the backend

---

## 📞 Support

- **Backend README:** [../backend/README.md](../backend/README.md)
- **Project README:** [../README.md](../README.md)
- **GitHub Issues:** Report bugs or request features

---

**Made with ❤️ for Cameroon 🇨🇲**
