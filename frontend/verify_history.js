const axios = require('axios');
const API_URL = 'http://localhost:8001/api/v1';

// Reuse tokens or login
const PASSENGER_PHONE = '+237699887766'; 
const PASSENGER_TOKEN = `mock_token_${PASSENGER_PHONE}`; 

async function verifyHistory() {
    try {
        console.log(" Verifying Ride History...");

        // 1. Login Passenger
        const loginRes = await axios.post(`${API_URL}/auth/login`, {
            firebase_token: PASSENGER_TOKEN
        });
        
        let passToken;
        if (loginRes.data.is_new_user) {
             console.log("   ⚠️ Passenger is new user (unexpected). Registering...");
             // Simple register
             const regRes = await axios.post(`${API_URL}/auth/register`, {
                phone_number: PASSENGER_PHONE,
                full_name: "Test Passenger",
                is_passenger: true
             });
             passToken = regRes.data.access_token;
        } else {
             passToken = loginRes.data.access_token;
        }

        console.log("   ✅ Passenger Logged In.");

        // 2. Get History
        const historyRes = await axios.get(`${API_URL}/rides/`, {
            headers: { Authorization: `Bearer ${passToken}` }
        });

        console.log(`   ✅ History Fetched! Found ${historyRes.data.length} rides.`);
        
        if (historyRes.data.length > 0) {
            const firstRide = historyRes.data[0];
            console.log(`   📝 Most Recent Ride:`);
            console.log(`      ID: ${firstRide.id}`);
            console.log(`      Status: ${firstRide.status}`);
            console.log(`      Date: ${firstRide.requested_at}`);
            console.log(`      Fare: ${firstRide.final_fare || firstRide.estimated_fare}`);
        } else {
            console.log("   ⚠️ No rides found. Please run verify_rating_driver.js first to generate data.");
            process.exit(1);
        }

    } catch (error) {
        console.error("❌ Verification Failed:", error.message);
        if (error.response) console.error("   Response:", error.response.data);
    }
}

verifyHistory();
