# Cameroon Traffic App - Mobile

React Native mobile application for real-time traffic reporting in Cameroon.

## Prerequisites

- Node.js 18+
- React Native CLI
- Android Studio (for Android development)
- Xcode (for iOS development, macOS only)
- Java JDK 11+

## Setup

1. **Install dependencies**
   ```bash
   npm install
   ```

2. **Configure environment variables**
   ```bash
   cp .env.example .env
   # Edit .env with your API keys
   ```

3. **Install iOS dependencies (macOS only)**
   ```bash
   cd ios && pod install && cd ..
   ```

## Running the App

### Android
```bash
npm run android
```

### iOS (macOS only)
```bash
npm run ios
```

### Start Metro Bundler
```bash
npm start
```

## Project Structure

```
mobile/
├── src/
│   ├── components/     # Reusable UI components
│   ├── screens/        # Screen components
│   ├── navigation/     # Navigation configuration
│   ├── store/          # Redux store and slices
│   ├── services/       # API services
│   ├── utils/          # Utility functions
│   ├── i18n/           # Translations
│   └── types/          # TypeScript types
├── android/            # Android native code
├── ios/                # iOS native code
└── index.js            # Entry point
```

## Development

### Type Checking
```bash
npm run type-check
```

### Linting
```bash
npm run lint
```

### Formatting
```bash
npm run format
```

### Testing
```bash
npm test
```

## Building for Production

### Android
```bash
cd android
./gradlew assembleRelease
```

### iOS
```bash
cd ios
xcodebuild -workspace CameroonTrafficApp.xcworkspace -scheme CameroonTrafficApp -configuration Release
```

## Features (MVP)

- [x] Project setup
- [ ] Map view with Mapbox
- [ ] User location tracking
- [ ] Display incidents on map
- [ ] Report incidents
- [ ] Photo upload
- [ ] Upvote/downvote
- [ ] Push notifications
- [ ] Offline mode
- [ ] French/English support

## Notes

This is the mobile app for the Cameroon Traffic App MVP.
Full implementation will be completed in Weeks 5-8 of the development plan.

