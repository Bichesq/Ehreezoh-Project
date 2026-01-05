import React, { createContext, useContext, useEffect, useState } from 'react';
import { socketService } from '../services/socket';
import { authService } from '../services/auth';
import { useAuth } from './AuthContext';
import { Alert } from 'react-native';

interface RideOffer {
  ride_id: string;
  pickup_address: string;
  dropoff_address: string;
  estimated_fare: number;
  distance_km: number;
}

interface SocketContextType {
  socket: typeof socketService;
  activeOffer: RideOffer | null;
  clearOffer: () => void;
  passengerRide: any | null;
  setPassengerRide: (ride: any) => void;
  clearPassengerRide: () => void;
}

const SocketContext = createContext<SocketContextType>({ 
  socket: socketService,
  activeOffer: null,
  clearOffer: () => {},
  passengerRide: null,
  setPassengerRide: () => {},
  clearPassengerRide: () => {}
});

export const useSocket = () => useContext(SocketContext);

export const SocketProvider: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  const { user, signOut } = useAuth();
  // Create a ref to access signOut inside the callback
  const authRef = React.useRef({ signOut });
  
  useEffect(() => {
      authRef.current = { signOut };
  }, [signOut]);

  const useAuthLink = authRef.current;
  const [activeOffer, setActiveOffer] = useState<RideOffer | null>(null);
  const [passengerRide, setPassengerRideState] = useState<any>(null); // Active ride for passenger
  const passengerRideRef = React.useRef(passengerRide);

  // Sync ref with state
  const setPassengerRide = (ride: any) => {
      // If passing a function/updater
      if (typeof ride === 'function') {
          setPassengerRideState((prev: any) => {
              const newState = ride(prev);
              passengerRideRef.current = newState;
              return newState;
          });
      } else {
          passengerRideRef.current = ride;
          setPassengerRideState(ride);
      }
  };

  useEffect(() => {
    let token: string | null = null;
    let unsubscribe: (() => void) | null = null;
    
    const connect = async () => {
      if (user) {
        token = await authService.getToken();
        if (token) {
          socketService.connect(token);
          
          // Listen for events
          unsubscribe = socketService.addListener((data: any) => {
            console.log('WS Event:', data.type, data.data);

            if (data.type === 'connected') {
                console.log('WS Connected. Checking for active ride to rejoin...');
                if (passengerRideRef.current?.id) {
                    console.log('🔄 Re-joining active ride room:', passengerRideRef.current.id);
                    socketService.send('join_ride', { ride_id: passengerRideRef.current.id });
                }
            }
            
            if (data.type === 'auth_error') {
                console.log('🔒 Auth Error received. Logging out...');
                Alert.alert('Session Expired', 'Please log in again.');
                useAuthLink.signOut(); 
            }

            if (data.type === 'pong') {
              console.log('🏓 Pong Received');
              Alert.alert('✅ Connection OK', 'Server responded to Ping!');
            }
            
            if (data.type === 'new_ride_offer') {
              console.log('🔔 Offer Received in Context:', data.data);
              Alert.alert('DEBUG: OFFER RECEIVED', `Fare: ${data.data.estimated_fare}`);
              setActiveOffer(data.data);
            }
            
            // Passenger Events
            if (['ride_accepted', 'ride_started', 'ride_completed', 'ride_cancelled'].includes(data.type)) {
                // Determine structure: data.data might be the ride object
                // IMPORTANT: Merge with existing state to preserve driver info and other fields
                // because backend updates (started, completed) often send partial data.
                setPassengerRide((prev: any) => {
                    const newState = { ...prev, ...data.data };
                    console.log('WS Update Merge:', { type: data.type, prev, newData: data.data, result: newState });
                    return newState;
                });
                
                if (data.type === 'ride_accepted') {
                    // Alert.alert('Ride Accepted!', 'Your driver is on the way.');
                } else if (data.type === 'ride_started') {
                    // Alert.alert('Ride Started', 'You are on your way!');
                } else if (data.type === 'ride_completed') {
                    Alert.alert('Arrived!', `Ride completed.`);
                }
            }

            if (data.type === 'driver_location_update') {
               console.log('📍 Driver Location Update:', data.data);
               setPassengerRide((prev: any) => {
                   if (!prev) return prev;
                   // Update the driver_location field in the ride object
                   return {
                       ...prev,
                       driver_location: {
                           latitude: data.data.latitude,
                           longitude: data.data.longitude
                       }
                   };
               });
            }
          });
        }
      } else {
        socketService.disconnect();
      }
    };

    connect();

    return () => {
      if (unsubscribe) unsubscribe();
      socketService.disconnect();
    };
  }, [user]);

  const clearOffer = () => setActiveOffer(null);
  const clearPassengerRide = () => setPassengerRide(null);

  return (
    <SocketContext.Provider value={{ socket: socketService, activeOffer, clearOffer, passengerRide, setPassengerRide, clearPassengerRide }}>
      {children}
    </SocketContext.Provider>
  );
};
