const axios = require('axios');
const API_URL = 'http://localhost:8001/api/v1';
const PASSENGER_PHONE = '+237699887766';
const PASSENGER_TOKEN = `mock_token_${PASSENGER_PHONE}`;

async function verifyProfile() {
    console.log("👤 Starting Profile Verification...");

    try {
        // 1. Login Passenger
        console.log("\n1️⃣  Logging in...");
        let authRes = await axios.post(`${API_URL}/auth/login`, { firebase_token: PASSENGER_TOKEN });
        const token = authRes.data.access_token;
        const initialUser = authRes.data.user;
        console.log(`   ✅ Logged in as: ${initialUser.full_name || 'No Name'} (${initialUser.phone_number})`);

        // 2. Update Profile
        const newName = "Updated User " + Math.floor(Math.random() * 1000);
        const newEmail = `user${Math.floor(Math.random() * 1000)}@example.com`;
        
        console.log(`\n2️⃣  Updating Profile to: ${newName}, ${newEmail}...`);
        
        const updateRes = await axios.patch(`${API_URL}/auth/me`, {
            full_name: newName,
            email: newEmail,
            profile_photo_url: "https://example.com/avatar.jpg"
        }, {
            headers: { Authorization: `Bearer ${token}` }
        });
        
        console.log(`   ✅ Update Success! New Name in Response: ${updateRes.data.full_name}`);

        // 3. Verify Persistence (Get Me)
        console.log("\n3️⃣  Verifying Persistence...");
        const meRes = await axios.get(`${API_URL}/auth/me`, {
             headers: { Authorization: `Bearer ${token}` }
        });
        
        if (meRes.data.full_name === newName && meRes.data.email === newEmail) {
            console.log("   ✅ Profile Verified Persisted!");
        } else {
            throw new Error(`Profile Mismatch! Expected ${newName}, got ${meRes.data.full_name}`);
        }

        console.log("\n✅ Profile Verification Successful!");

    } catch (error) {
        console.error("\n❌ Verification Failed:", error.response ? error.response.data : error.message);
    }
}

verifyProfile();
