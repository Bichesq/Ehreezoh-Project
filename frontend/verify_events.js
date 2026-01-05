

const WebSocket = require('ws');

// Configuration
const TOKEN = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiI0MTZlOTk3Yi1mZjY3LTRjYzctOWEyNi1lZjA1NGQ2NTFiY2IiLCJwaG9uZSI6Iis5MTc2OTY5NzY0ODkiLCJleHAiOjE3NjY3NDQ5MTIsImlhdCI6MTc2NjE0MDExMn0.AFm0vyoxK8elvHIaBAyRhyCKlBOtD-t-xr3lQRAIz0Q";
// This token belongs to User ID: 416e997b-ff67-4cc7-9a26-ef054d651bcb
// Based on logs, this user is also the one we promoted to Driver.

const API_Base = "http://localhost:8000/api/v1";
const WS_URL = "ws://localhost:8000/api/v1/ws/connect";

async function main() {
    console.log("🚀 Starting verification script...");

    // 1. Connect WebSocket
    const ws = new WebSocket(`${WS_URL}?token=${TOKEN}`);
    
    const eventsReceived = {
        accepted: false,
        started: false,
        completed: false
    };

    ws.onopen = () => {
        console.log("✅ WebSocket Connected");
        startTestFlow();
    };

    ws.onerror = (e) => {
        console.error("❌ WebSocket Error:", e);
    };

    ws.onmessage = (event) => {
        const msg = JSON.parse(event.data);
        console.log("📨 WS Message:", msg.type, msg.data?.id || "");
        
        if (msg.type === "ride_accepted") eventsReceived.accepted = true;
        if (msg.type === "ride_started") eventsReceived.started = true;
        if (msg.type === "ride_completed") eventsReceived.completed = true;
        if (msg.type === "payment_received") {
             console.log("💰 Payment Notification Received!");
             eventsReceived.payment = true;
        }
    };

    async function startTestFlow() {
        try {
            // 2. Request Ride
            console.log("\n🚕 Requesting Ride...");
            const startLat = 4.0511;
            const startLng = 9.7679;
            const reqRes = await fetch(`${API_Base}/rides/request`, {
                method: "POST",
                headers: {
                    "Content-Type": "application/json",
                    "Authorization": `Bearer ${TOKEN}`
                },
                body: JSON.stringify({
                    ride_type: "moto",
                    pickup_latitude: startLat,
                    pickup_longitude: startLng,
                    pickup_address: "Test Pickup",
                    dropoff_latitude: startLat + 0.01,
                    dropoff_longitude: startLng + 0.01,
                    dropoff_address: "Test Dropoff"
                })
            });

            if (!reqRes.ok) {
                const err = await reqRes.text();
                throw new Error(`Request failed: ${reqRes.status} ${err}`);
            }

            const ride = await reqRes.json();
            const rideId = ride.id;
            console.log("✅ Ride Requested. ID:", rideId);

            // 3. Accept Ride (Driver)
            console.log("\n👮 Accepting Ride...");
            // Short delay to ensure WS is ready
            await new Promise(r => setTimeout(r, 1000));
            
            const acceptRes = await fetch(`${API_Base}/rides/${rideId}/accept`, {
                method: "PATCH",
                headers: { "Authorization": `Bearer ${TOKEN}` }
            });

            if (!acceptRes.ok) throw new Error(`Accept failed: ${await acceptRes.text()}`);
            console.log("✅ Ride Accepted via API");

            // 4. Start Ride
            console.log("\n🏁 Starting Ride...");
            await new Promise(r => setTimeout(r, 1000));
            
            const startRes = await fetch(`${API_Base}/rides/${rideId}/start`, {
                method: "PATCH",
                headers: { "Authorization": `Bearer ${TOKEN}` }
            });
            
            if (!startRes.ok) throw new Error(`Start failed: ${await startRes.text()}`);
            console.log("✅ Ride Started via API");

            // 5. Complete Ride
            console.log("\n🎉 Completing Ride...");
            await new Promise(r => setTimeout(r, 1000));
            
            const completeRes = await fetch(`${API_Base}/rides/${rideId}/complete?final_fare=2000`, {
                method: "PATCH",
                headers: { "Authorization": `Bearer ${TOKEN}` }
            });
            
            if (!completeRes.ok) throw new Error(`Complete failed: ${await completeRes.text()}`);
            console.log("✅ Ride Completed via API");

            // Verify
            await new Promise(r => setTimeout(r, 2000)); // Wait for messages
            
            console.log("\n📊 Verification Results:");
            console.log(`- Ride Accepted Event: ${eventsReceived.accepted ? "✅ PASS" : "❌ FAIL"}`);
            // Note: Ride Accepted was already implemented, so expected to pass.
            console.log(`- Ride Started Event:  ${eventsReceived.started ? "✅ PASS" : "❌ FAIL"}`);
            console.log(`- Ride Completed Event:${eventsReceived.completed ? "✅ PASS" : "❌ FAIL"}`);

            ws.close();
            
            if (eventsReceived.started && eventsReceived.completed) {
                console.log("\n✅ SUCCESS: All lifecycle events received!");
                process.exit(0);
            } else {
                console.log("\n❌ FAIL: Missing events.");
                process.exit(1);
            }

        } catch (error) {
            console.error("\n❌ Test Failed:", error);
            ws.close();
            process.exit(1);
        }
    }
}

main();
