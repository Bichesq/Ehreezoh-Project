const axios = require('axios');

const API_URL = 'http://localhost:8000/api/v1';
const TEST_PHONE = '+237699123456';
const MOCK_TOKEN = `mock_token_${TEST_PHONE}`;

async function testAuth() {
    console.log("🔐 Starting Mobile Auth Verification...");
    console.log(`   Target: ${API_URL}`);
    console.log(`   Phone:  ${TEST_PHONE}`);
    console.log(`   Token:  ${MOCK_TOKEN}`);

    try {
        // 1. Test Login (Expect 404 if user doesn't exist, or success if they do)
        console.log("\n1️⃣  Testing Login...");
        try {
            const loginRes = await axios.post(`${API_URL}/auth/login`, {
                firebase_token: MOCK_TOKEN
            });
            console.log("   ✅ Login Successful!");
            console.log("   🔑 Token:", loginRes.data.access_token.substring(0, 20) + "...");
            return; // Exit if login worked (user exists)
        } catch (error) {
            if (error.response && error.response.status === 404) {
                console.log("   ℹ️  User not found (Expected for new user). Proceeding to Register...");
            } else {
                throw error;
            }
        }

        // 2. Test Registration (If login failed/user didn't exist)
        console.log("\n2️⃣  Testing Registration...");
        const regRes = await axios.post(`${API_URL}/auth/register`, {
            firebase_token: MOCK_TOKEN,
            full_name: "Test Mobile User",
            email: "mobile@test.com",
            language_preference: "en"
        });

        console.log("   ✅ Registration Successful!");
        console.log("   👤 User ID:", regRes.data.user.id);
        console.log("   🔑 Token:", regRes.data.access_token.substring(0, 20) + "...");

        // 3. Verify Login success AFTER registration
        console.log("\n3️⃣  Verifying Login (Post-Registration)...");
        const loginRetry = await axios.post(`${API_URL}/auth/login`, {
            firebase_token: MOCK_TOKEN
        });
        console.log("   ✅ Login Successful!");

    } catch (error) {
        console.error("\n❌ Auth Test Failed:");
        if (error.response) {
            console.error("   Status:", error.response.status);
            console.error("   Data:", error.response.data);
        } else {
            console.error("   Error:", error.message);
        }
    }
}

testAuth();
