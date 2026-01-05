
const WebSocket = require('ws');
const TOKEN = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiI0MTZlOTk3Yi1mZjY3LTRjYzctOWEyNi1lZjA1NGQ2NTFiY2IiLCJwaG9uZSI6Iis5MTc2OTY5NzY0ODkiLCJleHAiOjE3NjY3NDQ5MTIsImlhdCI6MTc2NjE0MDExMn0.AFm0vyoxK8elvHIaBAyRhyCKlBOtD-t-xr3lQRAIz0Q";
const API_Base = "http://localhost:8000/api/v1";
const WS_URL = "ws://localhost:8000/api/v1/ws/connect";

async function main() {
    console.log("🚀 Starting Driver Dispatch Verification...");

    // 1. Connect Driver to WebSocket
    console.log("👮 Driver connecting to WebSocket...");
    const ws = new WebSocket(`${WS_URL}?token=${TOKEN}`);
    let offerReceived = false;

    ws.onopen = () => {
        console.log("✅ Driver Connected");
        // Mark driver as online to be eligible for matching
        ws.send(JSON.stringify({ type: "driver_online" }));
        
        // Update location (essential for GEOSPATIAL matching)
        // 4.05, 9.70 matches the pickup location in the request below
        ws.send(JSON.stringify({ 
            type: "driver_location_update", 
            data: { latitude: 4.0500, longitude: 9.7000 }
        }));
    };
    
    ws.onmessage = (event) => {
        const msg = JSON.parse(event.data);
        if (msg.type === "new_ride_offer") {
            console.log("🔔 New Ride Offer Received!", msg.data);
            offerReceived = true;
        }
    };

    try {
        // Wait for connection and online status (give Redis time to index)
        await new Promise(r => setTimeout(r, 4000));

        // 2. Simulate Passenger Requesting a Ride (using a different mock token/user if possible, 
        // but for now we'll just trigger the request and hope self-matching is allowed or ignored for test)
        // Ideally we need a separate passenger user. 
        // Since we are using the DRIVER token, we need to ensure the backend allows self-matching or simply finds "a driver" (which is us).
        
        console.log("\n🚕 Passenger Requesting Ride...");
        // Use a random pickup location near the driver's last known location (which acts as the "center" of their availability)
        // Assuming driver is at (4.05, 9.70) based on typical test data
        
        const reqRes = await fetch(`${API_Base}/rides/request`, {
            method: "POST",
            headers: { "Content-Type": "application/json", "Authorization": `Bearer ${TOKEN}` },
            body: JSON.stringify({
                ride_type: "moto",
                pickup_latitude: 4.0500, pickup_longitude: 9.7000,
                dropoff_latitude: 4.0600, dropoff_longitude: 9.7100,
                pickup_address: "Test Match Pickup"
            })
        });

        if (!reqRes.ok) throw new Error(`Request failed: ${await reqRes.text()}`);
        const ride = await reqRes.json();
        console.log("✅ Ride Requested ID:", ride.id);

        // Wait for notification
        console.log("⏳ Waiting for offer...");
        await new Promise(r => setTimeout(r, 4000));

        ws.close();

        if (offerReceived) {
            console.log("\n✅ SUCCESS: Driver received dispatched ride offer!");
            process.exit(0);
        } else {
            console.log("\n❌ FAIL: no offer received.");
            console.log("Possible causes: Driver not online, not close enough, or self-matching blocked.");
            process.exit(1);
        }

    } catch (error) {
        console.error("\n❌ Verification Failed:", error);
        ws.close();
        process.exit(1);
    }
}

main();
