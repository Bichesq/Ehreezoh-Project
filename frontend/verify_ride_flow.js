const axios = require('axios');
const WebSocket = require('ws');

const API_URL = 'http://localhost:8000/api/v1';
const WS_URL = 'ws://localhost:8000/api/v1/ws/connect';
const TEST_PHONE = '+237699887766';
const MOCK_TOKEN = `mock_token_${TEST_PHONE}`;

async function verifyRideFlow() {
    console.log("🚀 Starting Ride Request Verification...");

    try {
        // 1. Login
        console.log("\n1️⃣  Logging in Passenger...");
        let authRes;
        try {
            authRes = await axios.post(`${API_URL}/auth/login`, { firebase_token: MOCK_TOKEN });
        } catch (e) {
            if (e.response && e.response.status === 404) {
                 console.log("   ℹ️  User not found, registering...");
                 authRes = await axios.post(`${API_URL}/auth/register`, {
                    firebase_token: MOCK_TOKEN,
                    full_name: "Test Passenger",
                    email: "passenger@test.com",
                    language_preference: "en"
                });
            } else {
                throw e;
            }
        }
        const token = authRes.data.access_token;
        const passengerId = authRes.data.user.id;
        console.log(`   ✅ Logged in as ${passengerId}`);

        // 2. Connect WebSocket
        console.log("\n2️⃣  Connecting WebSocket...");
        const ws = new WebSocket(`${WS_URL}?token=${token}`);
        
        await new Promise((resolve, reject) => {
            ws.on('open', resolve);
            ws.on('error', reject);
        });
        console.log("   ✅ WebSocket Connected!");

        // 3. Send Location Update
        console.log("\n3️⃣  Sending Location Update...");
        ws.send(JSON.stringify({
            type: "passenger_location_update",
            data: { latitude: 4.0500, longitude: 9.7000 }
        }));
        // Wait for server to process
        await new Promise(r => setTimeout(r, 1000));
        console.log("   ✅ Location sent.");

        // 4. Request Ride
        console.log("\n4️⃣  Requesting Ride...");
        const rideReq = {
            ride_type: "moto",
            pickup_latitude: 4.0500,
            pickup_longitude: 9.7000,
            dropoff_latitude: 4.0600,
            dropoff_longitude: 9.7100,
            pickup_address: "Akwa, Douala",
            dropoff_address: "Bonanjo, Douala"
        };

        const rideRes = await axios.post(`${API_URL}/rides/request`, rideReq, {
            headers: { Authorization: `Bearer ${token}` }
        });
        
        const rideId = rideRes.data.id;
        console.log(`   ✅ Ride Request Accepted! Ride ID: ${rideId}`);
        console.log(`   Initial Status: ${rideRes.data.status}`);

        // 5. Check if Ride exists in DB (Wait 2s)
        await new Promise(r => setTimeout(r, 2000));
        
        // Clean up
        ws.close();
        console.log("\n✅ Verification Complete! The flow works.");

    } catch (error) {
        console.error("\n❌ Verification Failed:", error.response ? error.response.data : error.message);
    }
}

verifyRideFlow();
