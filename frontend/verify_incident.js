const axios = require('axios');
const API_URL = 'http://localhost:8001/api/v1';
const PASSENGER_PHONE = '+237699887766';
const PASSENGER_TOKEN = `mock_token_${PASSENGER_PHONE}`;

async function verifyIncidents() {
    console.log("🚦 Starting Incident Reporting Verification...");

    try {
        // 1. Login Passenger
        console.log("\n1️⃣  Logging in Passenger...");
        let authRes = await axios.post(`${API_URL}/auth/login`, { firebase_token: PASSENGER_TOKEN });
        const token = authRes.data.access_token;
        console.log(`   ✅ Logged in! User ID: ${authRes.data.user.id}`);

        // 2. Report Incident
        console.log("\n2️⃣  Reporting Incident...");
        const incidentData = {
            type: "accident",
            description: "Minor fender bender causing delays",
            latitude: 4.0505,
            longitude: 9.7005
        };
        const reportRes = await axios.post(`${API_URL}/incidents/`, incidentData, {
            headers: { Authorization: `Bearer ${token}` }
        });
        console.log(`   ✅ Incident Reported! ID: ${reportRes.data.id}`);

        // 3. Fetch Nearby Incidents
        console.log("\n3️⃣  Fetching Nearby Incidents...");
        const fetchRes = await axios.get(`${API_URL}/incidents/`, {
            params: { latitude: 4.0500, longitude: 9.7000, radius_km: 5 },
            headers: { Authorization: `Bearer ${token}` }
        });
        
        const incidents = fetchRes.data;
        console.log(`   ✅ Found ${incidents.length} incidents.`);
        
        const found = incidents.find(i => i.id === reportRes.data.id);
        if (found) {
            console.log(`   ✅ Verified: Our reported incident is in the list!`);
            console.log(`      Location: ${found.latitude}, ${found.longitude}`);
            console.log(`      Type: ${found.type}`);
        } else {
             throw new Error("Reported incident not found in nearby list!");
        }

        console.log("\n✅ Incident Verification Successful!");

    } catch (error) {
        console.error("\n❌ Verification Failed:", error.response ? error.response.data : error.message);
    }
}

verifyIncidents();

