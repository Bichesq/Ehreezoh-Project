const axios = require('axios');
const WebSocket = require('ws');

const API_URL = 'http://localhost:8001/api/v1';
const WS_URL = 'ws://localhost:8001/api/v1/ws/connect';
// Driver phone needs to be different from passenger phone used in other script
const DRIVER_PHONE = '+237611223344'; 
const PASSENGER_PHONE = '+237699887766';

const DRIVER_TOKEN = `mock_token_${DRIVER_PHONE}`;
const PASSENGER_TOKEN = `mock_token_${PASSENGER_PHONE}`;

async function verifyDriverFlow() {
    console.log("🚕 Starting Driver Flow Verification...");

    try {
        // 1. Login Driver
        console.log("\n1️⃣  Logging in Driver...");
        let authRes;
        try {
            authRes = await axios.post(`${API_URL}/auth/login`, { firebase_token: DRIVER_TOKEN });
        } catch (e) {
            if (e.response && e.response.status === 404) {
                 console.log("   ℹ️  Driver not found, registering...");
                 authRes = await axios.post(`${API_URL}/auth/register`, {
                    firebase_token: DRIVER_TOKEN,
                    full_name: "Test Driver",
                    email: "driver@test.com",
                    language_preference: "en"
                });
            } else {
                throw e;
            }
        }
        const driverToken = authRes.data.access_token;
        const driverId = authRes.data.user.id;
        console.log(`   ✅ Driver Logged in! ID: ${driverId}`);

        // 2. Connect Driver WebSocket
        console.log("\n2️⃣  Connecting Driver WebSocket...");
        const driverWs = new WebSocket(`${WS_URL}?token=${driverToken}`);
        
        // Capture offers early to avoid race conditions
        let receivedOffers = [];
        driverWs.on('message', (data) => {
            const raw = data.toString();
            console.log("   📩 Received WS Message:", raw);
            try {
                const msg = JSON.parse(raw);
                if (msg.type === 'new_ride_offer') {
                    receivedOffers.push(msg.data);
                }
            } catch (e) { }
        });

        await new Promise((resolve) => driverWs.on('open', resolve));
        console.log("   ✅ Driver Connected");

        // 3. Go Online & Send Location
        console.log("\n3️⃣  Driver Going Online...");
        driverWs.send(JSON.stringify({ type: "driver_online" }));
        driverWs.send(JSON.stringify({
            type: "driver_location_update",
            data: { latitude: 4.0500, longitude: 9.7000 } // Same loc as passenger pickup
        }));
        
        // Wait for server to process and index (Redis/DB)
        console.log("   ⏳ Waiting 5s for driver to be indexed...");
        await new Promise(r => setTimeout(r, 5000));
        
        // Check driver status via API
        const meRes = await axios.get(`${API_URL}/auth/me`, {
            headers: { Authorization: `Bearer ${driverToken}` }
        });
        console.log("   🔍 Driver Profile:", { 
            is_driver: meRes.data.is_driver, 
            id: meRes.data.id 
        });

        // 4. Passenger Request (Simulate Passenger)
        console.log("\n4️⃣  Simulating Passenger Request...");
        // Login Passenger
        let passAuthRes = await axios.post(`${API_URL}/auth/login`, { firebase_token: PASSENGER_TOKEN });
        const passToken = passAuthRes.data.access_token;
        
        // Request Ride
        const rideReq = {
            ride_type: "moto",
            pickup_latitude: 4.0500,
            pickup_longitude: 9.7000,
            dropoff_latitude: 4.0600,
            dropoff_longitude: 9.7100,
            pickup_address: "Akwa",
            dropoff_address: "Bonanjo"
        };
        const rideRes = await axios.post(`${API_URL}/rides/request`, rideReq, {
            headers: { Authorization: `Bearer ${passToken}` }
        });
        const rideId = rideRes.data.id;
        console.log(`   ✅ Ride Requested: ${rideId}`);

        // 5. Driver Receives Offer?
        console.log("\n5️⃣  Waiting for Ride Offer...");
        let offerData = null;
        if (receivedOffers.length > 0) {
            offerData = receivedOffers[0];
            console.log("   ⚡ Offer already received!");
        } else {
             offerData = await new Promise((resolve, reject) => {
                const timeout = setTimeout(() => reject(new Error("Timeout waiting for offer")), 10000);
                const interval = setInterval(() => {
                    if (receivedOffers.length > 0) {
                        clearTimeout(timeout);
                        clearInterval(interval);
                        resolve(receivedOffers[0]);
                    }
                }, 100);
            });
        }
        console.log("   ✅ Offer Received!", offerData);

        // Monitor Passenger Events for Updates
        const passengerWs = new WebSocket(`${WS_URL}?token=${passToken}`);
        await new Promise(r => passengerWs.on('open', r));
        console.log("   ✅ Passenger WS Connected");

        passengerWs.on('message', (data) => {
            const raw = data.toString();
            try {
                const msg = JSON.parse(raw);
                if (['ride_accepted', 'ride_started', 'ride_completed'].includes(msg.type)) {
                    console.log(`   👤 Passenger Received Update: ${msg.type}`);
                }
            } catch (e) {}
        });

        // 6. Accept Ride
        console.log("\n6️⃣  Accepting Ride...");
        const acceptRes = await axios.patch(`${API_URL}/rides/${rideId}/accept`, {}, {
            headers: { Authorization: `Bearer ${driverToken}` }
        });
        console.log(`   ✅ Ride Accepted! Status: ${acceptRes.data.status}`);

        // 7. Start Ride
        console.log("\n7️⃣  Starting Ride...");
        const startRes = await axios.patch(`${API_URL}/rides/${rideId}/start`, {}, {
            headers: { Authorization: `Bearer ${driverToken}` }
        });
        console.log(`   ✅ Ride Started! Status: ${startRes.data.status}`);

        // Wait a bit
        await new Promise(r => setTimeout(r, 2000));

        // 8. Complete Ride
        console.log("\n8️⃣  Completing Ride...");
        const completeRes = await axios.patch(`${API_URL}/rides/${rideId}/complete`, {}, {
            headers: { Authorization: `Bearer ${driverToken}` }
        });
        console.log(`   ✅ Ride Completed! Status: ${completeRes.data.status}`);

        // 9. Rate Driver (Passenger)
        console.log("\n9️⃣  Rating Driver (Passenger)...");
        const ratingRes = await axios.post(`${API_URL}/rides/${rideId}/rate`, {
            rating: 5,
            review: "Great ride! Fast and safe."
        }, {
            headers: { Authorization: `Bearer ${passToken}` }
        });
        console.log(`   ✅ Passenger Rating Submitted! Response: ${ratingRes.data.message}`);

        // 10. Rate Passenger (Driver)
        console.log("\n🔟  Rating Passenger (Driver)...");
        const driverRatingRes = await axios.post(`${API_URL}/rides/${rideId}/rate`, {
            rating: 4,
            review: "Passenger was polite."
        }, {
            headers: { Authorization: `Bearer ${driverToken}` }
        });
        console.log(`   ✅ Driver Rating Submitted! Response: ${driverRatingRes.data.message}`);

        driverWs.close();
        passengerWs.close();
        console.log("\n✅ Verification Successful!");

    } catch (error) {
        console.error("\n❌ Verification Failed:", error.response ? error.response.data : error.message);
    }
}

verifyDriverFlow();
