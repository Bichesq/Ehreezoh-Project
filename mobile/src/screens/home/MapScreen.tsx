import React, { useEffect, useState, useRef } from 'react';
import { View, StyleSheet, Text, TouchableOpacity, Alert, Dimensions, ActivityIndicator } from 'react-native';
import MapView, { Marker, PROVIDER_GOOGLE, Region, Polyline } from 'react-native-maps';
import { useRouter } from 'expo-router';
import { useSocket } from '../../context/SocketContext';
import { locationService, Coordinates } from '../../services/location';
import { rideService } from '../../services/ride';
import { driverService } from '../../services/driver'; // NEW
import { useAuth } from '../../context/AuthContext';
import { StatusBar } from 'expo-status-bar';
import IncidentReportModal from './IncidentReportModal';
import { incidentService, Incident } from '../../services/incident';
import { routeService, ScoredRoute } from '../../services/route';
import { analyticsService, SafetyPrediction } from '../../services/analytics';
import PaymentScreen from '../payment/PaymentScreen';
import PassengerActiveRide from './PassengerActiveRide';
import ActiveRideScreen from '../driver/ActiveRideScreen'; // NEW
import RideRatingScreen from './RideRatingScreen';
import DestinationPicker from '../../components/DestinationPicker';
import RideRequestSheet from '../../components/RideRequestSheet';
import RideOfferModal from '../../components/RideOfferModal'; // NEW
import RouteSelector from '../../components/RouteSelector';
import IncidentAlertBanner from '../../components/IncidentAlertBanner';
import IncidentDetailModal from '../../components/IncidentDetailModal';
import SafetyForecastModal from '../../components/SafetyForecastModal';
import { COLORS } from '../../constants/colors';
import { SHADOWS, TYPOGRAPHY } from '../../constants/theme';
import { DARK_MAP_STYLE } from '../../constants/mapStyle';
import polyline from '@mapbox/polyline';
import CustomAlert, { AlertButton } from '../../components/CustomAlert';

export default function MapScreen() {
  const [location, setLocation] = useState<Coordinates | null>(null);
  const [loading, setLoading] = useState(true);
  const [mapRegion, setMapRegion] = useState<Region|null>(null);
  
  // Modes: IDLE, PICKING_DEST, SELECT_ROUTE, CONFIRMING, REQUESTING, NAVIGATING
  const [mode, setMode] = useState<'IDLE' | 'PICKING_DEST' | 'SELECT_ROUTE' | 'CONFIRMING' | 'REQUESTING' | 'NAVIGATING'>('IDLE');
  const [destination, setDestination] = useState<Coordinates | null>(null);

  // Route Analysis
  const [analyzing, setAnalyzing] = useState(false);
  const [availableRoutes, setAvailableRoutes] = useState<ScoredRoute[]>([]);
  const [selectedRoute, setSelectedRoute] = useState<ScoredRoute | null>(null);

  // Forecast State
  const [showForecast, setShowForecast] = useState(false);
  const [forecastLoading, setForecastLoading] = useState(false);
  const [forecastData, setForecastData] = useState<SafetyPrediction[]>([]);

  // Ride State
  const [activeRideId, setActiveRideId] = useState<string | null>(null);
  const { user } = useAuth();
  const { socket, passengerRide, clearPassengerRide, setPassengerRide, activeOffer, clearOffer } = useSocket();
  const [isPaid, setIsPaid] = useState(false);
  
  // Driver state
  const [driverRide, setDriverRide] = useState<any | null>(null);

  // Data
  const [incidents, setIncidents] = useState<Incident[]>([]);
  const [showIncidentModal, setShowIncidentModal] = useState(false);
  const [selectedIncident, setSelectedIncident] = useState<Incident | null>(null);
  
  // Alerts
  const [incidentAlert, setIncidentAlert] = useState<any | null>(null);
  const lastSubTime = useRef<number>(0);

  // Custom Alert State
  const [alertConfig, setAlertConfig] = useState<{visible: boolean, title: string, message?: string, buttons?: AlertButton[]}>({
      visible: false, title: '', message: ''
  });

  const showAlert = (title: string, message?: string, buttons?: AlertButton[]) => {
      setAlertConfig({ visible: true, title, message, buttons });
  };

  const closeAlert = () => {
      setAlertConfig(prev => ({ ...prev, visible: false }));
  };

  const mapRef = useRef<MapView>(null);
  const router = useRouter();

  // 1. Init & Location
  useEffect(() => {
    (async () => {
      const hasPermission = await locationService.requestPermissions();
      if (!hasPermission) {
        showAlert('Permission denied', 'Location permission is required.', [{ text: 'OK' }]);
        return;
      }
      // ... (rest of logic)
      const currentLoc = await locationService.getCurrentPosition();
      if (currentLoc) {
        setLocation(currentLoc);
        fetchIncidents(currentLoc.latitude, currentLoc.longitude);
      }
      setLoading(false);

      const sub = await locationService.watchPosition((coords) => {
        setLocation(coords);
        socket.send('passenger_location_update', coords);

        // Throttle Geohash Subscription (every 15s)
        const now = Date.now();
        if (now - lastSubTime.current > 15000) {
            socket.send('subscribe_geohash', coords);
            lastSubTime.current = now;
        }
      });

      return () => sub.remove();
    })();
  }, []);

  // 2. Incident Listener
  useEffect(() => {
      const handleIncidentAlert = (data: any) => {
          console.log("🔥 INCIDENT ALERT:", data);
          setIncidentAlert(data);
          setTimeout(() => setIncidentAlert(null), 10000); // Auto hide
          if (location) fetchIncidents(location.latitude, location.longitude);
      };
      
      const unsubscribe = socket.addListener((msg: any) => {
          if (msg.type === 'incident_alert') {
              handleIncidentAlert(msg.data);
          }
      });
      
      return () => {
          unsubscribe();
      };
  }, [location, socket]);

  // 3. Fit Map to Driver (Passenger Only)
  useEffect(() => {
     if (passengerRide && passengerRide.driver_location && location && mapRef.current) {
         mapRef.current.fitToCoordinates([
             { latitude: location.latitude, longitude: location.longitude },
             { latitude: passengerRide.driver_location.latitude, longitude: passengerRide.driver_location.longitude }
         ], {
             edgePadding: { top: 100, right: 50, bottom: 200, left: 50 },
             animated: true
         });
     }
  }, [passengerRide?.status, passengerRide?.driver_id]);

  const fetchIncidents = async (lat: number, lon: number) => {
      try {
          const data = await incidentService.getNearbyIncidents(lat, lon, 10);
          setIncidents(data);
      } catch (e) {
          console.log("Failed to fetch incidents", e);
      }
  };

  const handleRegionChange = (region: Region) => {
      setMapRegion(region);
  };

  const startDestinationPick = () => {
      if (!location) return;
      setMode('PICKING_DEST');
  };

  const confirmDestination = async () => {
    if (!mapRegion || !location) return;
    
    const dest = {
        latitude: mapRegion.latitude,
        longitude: mapRegion.longitude
    };
    setDestination(dest);

    // Analyze Routes
    setAnalyzing(true);
    try {
        const result = await routeService.analyzeRoutes(location, dest, 'moto');
        setAvailableRoutes(result.routes);
        
        if (result.routes.length > 0) {
            const best = result.routes[0];
            setSelectedRoute(best);
            setMode('SELECT_ROUTE');
            fitToRoute(best);
        } else {
            setMode('CONFIRMING');
        }
    } catch (e) {
        console.error("Analysis failed", e);
        setMode('CONFIRMING');
    } finally {
        setAnalyzing(false);
    }
  };


  const fitToRoute = (route: ScoredRoute) => {
      if (!mapRef.current) return;
      const points = polyline.decode(route.geometry_encoded).map(p => ({
          latitude: p[0], longitude: p[1]
      }));
      mapRef.current.fitToCoordinates(points, {
          edgePadding: { top: 50, right: 50, bottom: 350, left: 50 },
          animated: true
      });
  };

  const handleRouteConfirm = () => {
      setMode('CONFIRMING');
  };

  const cancelSelection = () => {
      setMode('IDLE');
      setDestination(null);
      setAvailableRoutes([]);
      setSelectedRoute(null);
  };
  
  // --- Navigation Logic ---
  const startNavigation = () => {
      if (!selectedRoute) return;
      setMode('NAVIGATING');
      fitToRoute(selectedRoute);
      showAlert("Navigation Started", "Drive safely! We will alert you of incidents ahead.");
  };

  const exitNavigation = () => {
      showAlert(
          "Exit Navigation", 
          "Stop navigation?", 
          [
              { text: "Cancel", style: "cancel", onPress: closeAlert },
              { text: "Exit", style: "destructive", onPress: () => {
                  setMode('IDLE');
                  setDestination(null);
                  setAvailableRoutes([]);
                  setSelectedRoute(null);
                  closeAlert();
              }}
          ]
      );
  };
  // ------------------------

  // --- Forecast Logic ---
  const handleForecast = async () => {
      if (!selectedRoute) return;
      setShowForecast(true);
      setForecastLoading(true);
      try {
          const result = await analyticsService.getBestTimeToLeave(selectedRoute.geometry_encoded);
          setForecastData(result.predictions);
      } catch (e) {
          console.error("Forecast failed", e);
          showAlert("Forecast Unavailable", "Could not fetch historical data at this time.");
          setShowForecast(false);
      } finally {
          setForecastLoading(false);
      }
  };
  // ----------------------

  const handleRequestRide = async (rideType: 'moto' | 'car') => {
    if (!location || !destination) return;

    setMode('REQUESTING');
    try {
      const request = {
        ride_type: rideType,
        pickup_latitude: location.latitude,
        pickup_longitude: location.longitude,
        dropoff_latitude: destination.latitude,
        dropoff_longitude: destination.longitude,
        pickup_address: 'Current Location',
        dropoff_address: 'Pin Location',
        route_id: selectedRoute?.id
      };

      const ride = await rideService.requestRide(request);
      setActiveRideId(ride.id);
      setPassengerRide(ride);
      socket.send('join_ride', { ride_id: ride.id });
      setMode('IDLE'); 
    } catch (error: any) {
      console.error('Ride request error:', error);
      showAlert('Error', 'Failed to request ride');
      setMode('CONFIRMING');
    }
  };
  
  // --- Driver Logic ---
  const handleAcceptRide = async (rideId: string) => {
      try {
          // 1. Accept API
          const ride = await driverService.acceptRide(rideId);
          // 2. Clear Offer
          clearOffer();
          // 3. Set Driver Active Ride
          setDriverRide(ride);
          // 4. Join Socket room to broadcast updates
          // socket.send('join_ride', { ride_id: ride.id }); // optional for driver if purely API driven, but safer
      } catch (e) {
          console.error(e);
          showAlert('Failed to Accept', 'Someone else may have taken it.');
          clearOffer();
      }
  };

  const handleDriverRideComplete = () => {
      setDriverRide(null);
      setMode('IDLE');
      showAlert("Great Job!", "Ride completed successfully.");
  };
  // --------------------

  const handleRatingComplete = () => {
      clearPassengerRide();
      setActiveRideId(null);
      setIsPaid(false);
      setMode('IDLE');
      setDestination(null);
      setAvailableRoutes([]);
  };

  const getDistance = () => {
      if (selectedRoute) return selectedRoute.distance_km;
      if (!location || !destination) return 0;
      return locationService.calculateDistance(
          location.latitude, location.longitude,
          destination.latitude, destination.longitude
      );
  };

  const handleCancelRide = async () => {
    if (!passengerRide) return;
    showAlert('Cancel Ride', 'Are you sure?', [
        { text: 'No', style: 'cancel', onPress: closeAlert },
        { text: 'Yes', style: 'destructive', onPress: async () => {
            try {
                await rideService.cancelRide(passengerRide.id);
                clearPassengerRide();
                setActiveRideId(null);
                setMode('IDLE');
                setDestination(null);
                closeAlert();
            } catch (e) {
                console.log("Cancel failed", e);
                clearPassengerRide();
                closeAlert();
            }
        }}
    ]);
  };

  if (loading || !location) {
    return (
      <View style={styles.loadingContainer}>
        <ActivityIndicator size="large" color={COLORS.primary} />
        <Text style={{color: COLORS.text, marginTop: 10}}>Locating...</Text>
      </View>
    );
  }

  // --- Active Ride Views ---
  
  // 1. Driver View
  if (driverRide) {
      return (
          <ActiveRideScreen 
            ride={driverRide}
            currentLocation={location}
            onRideComplete={handleDriverRideComplete}
          />
      );
  }

  // 2. Passenger View (Completed - Rating/Payment)
  if (passengerRide && passengerRide.status === 'completed') {
    if (!isPaid) return <PaymentScreen ride={passengerRide} onPaymentComplete={() => setIsPaid(true)} onCancel={() => setIsPaid(true)} />;
    return <RideRatingScreen ride={passengerRide} onComplete={handleRatingComplete} />;
  }

  // 3. Passenger View (Active)
  if (passengerRide) {
      return (
        <View style={styles.container}>
            <StatusBar style="light" />
            <MapView
                ref={mapRef}
                provider={PROVIDER_GOOGLE}
                customMapStyle={DARK_MAP_STYLE}
                style={styles.map}
                initialRegion={{
                   latitude: location.latitude, longitude: location.longitude,
                   latitudeDelta: 0.05, longitudeDelta: 0.05
                }}
                showsUserLocation={true}
            >
                {passengerRide.driver_location && (
                    <Marker
                        coordinate={{ latitude: passengerRide.driver_location.latitude, longitude: passengerRide.driver_location.longitude }}
                        title="Your Driver"
                    >
                        <View style={styles.driverMarker}><Text style={{fontSize: 20}}>🚗</Text></View>
                    </Marker>
                )}
            </MapView>
            <PassengerActiveRide ride={passengerRide} onCancel={handleCancelRide} />
            <CustomAlert 
                visible={alertConfig.visible} 
                title={alertConfig.title} 
                message={alertConfig.message} 
                buttons={alertConfig.buttons}
                onClose={closeAlert}
            />
        </View>
      );
  }

  return (
    <View style={styles.container}>
      <StatusBar style="light" />
      
      {/* Driver Offer Modal */}
      <RideOfferModal 
        visible={!!activeOffer}
        offer={activeOffer}
        onAccept={handleAcceptRide}
        onDecline={clearOffer}
      />
      
      <SafetyForecastModal
           visible={showForecast}
           onClose={() => setShowForecast(false)}
           predictions={forecastData}
           loading={forecastLoading}
      />

      <IncidentAlertBanner 
          alert={incidentAlert} 
          onDismiss={() => setIncidentAlert(null)}
          onView={(alert) => {
              setIncidentAlert(null);
              mapRef.current?.animateToRegion({
                  latitude: alert.latitude, longitude: alert.longitude,
                  latitudeDelta: 0.02, longitudeDelta: 0.02
              });
          }}
          onReroute={destination || passengerRide ? async () => {
              setIncidentAlert(null);
              setAnalyzing(true);
              try {
                const start = location;
                const end = passengerRide ? {
                    latitude: passengerRide.dropoff_latitude,
                    longitude: passengerRide.dropoff_longitude
                } : destination;

                if (!start || !end) return;

                const result = await routeService.analyzeRoutes(start, end, 'moto');
                if (result.routes.length > 0) {
                    const best = result.routes[0];
                    setSelectedRoute(best);
                    
                    if (passengerRide) {
                        showAlert("Route Updated", "Verifying with driver...");
                    } else if (mode === 'NAVIGATING' || mode === 'SELECT_ROUTE') {
                         showAlert("Rerouted", "Found a better route.");
                    }
                    fitToRoute(best);
                } else {
                    showAlert("No better route", "Current route is still the best option.");
                }
              } catch (e) {
                  console.error(e);
                  showAlert("Reroute failed");
              } finally {
                  setAnalyzing(false);
              }
          } : undefined}
      />

      <MapView
        ref={mapRef}
        provider={PROVIDER_GOOGLE}
        customMapStyle={DARK_MAP_STYLE}
        style={styles.map}
        initialRegion={{
          latitude: location.latitude, longitude: location.longitude,
          latitudeDelta: 0.01, longitudeDelta: 0.01
        }}
        showsUserLocation
        followsUserLocation={mode === 'IDLE' || mode === 'NAVIGATING'}
        onRegionChangeComplete={handleRegionChange}
      >
          {destination && (mode === 'CONFIRMING' || mode === 'SELECT_ROUTE') && (
              <Marker coordinate={destination} title="Dropoff" pinColor={COLORS.primary} />
          )}

          {/* Show route in SELECT_ROUTE, NAVIGATING, or Reroute view */}
          {(mode === 'SELECT_ROUTE' || mode === 'NAVIGATING') && availableRoutes.map(route => {
              // In Navigation mode, only show selected
              if (mode === 'NAVIGATING' && route.id !== selectedRoute?.id) return null;

              const isSelected = selectedRoute?.id === route.id;
              const points = polyline.decode(route.geometry_encoded).map(p => ({ latitude: p[0], longitude: p[1] }));
              
              return (
                  <Polyline 
                    key={route.id}
                    coordinates={points}
                    strokeColor={isSelected ? COLORS.primary : 'rgba(255,255,255,0.3)'}
                    strokeWidth={isSelected ? 6 : 4}
                    zIndex={isSelected ? 10 : 1}
                    onPress={() => setSelectedRoute(route)}
                    tappable={true}
                  />
              );
          })}

          {incidents.map(inc => (
              <Marker
                key={inc.id}
                coordinate={{ latitude: inc.latitude, longitude: inc.longitude }}
                onPress={() => setSelectedIncident(inc)}
              >
                  <View style={styles.incidentMarker}>
                      <Text>{inc.type === 'accident' ? '💥' : inc.type === 'police' ? '👮' : '⚠️'}</Text>
                  </View>
              </Marker>
          ))}
      </MapView>

      {/* Nav Overlay */}
      {mode === 'NAVIGATING' && (
          <View style={styles.navOverlay}>
             <View style={styles.navHeader}>
                <Text style={styles.navTitle}>Navigating to Dropoff</Text>
                <Text style={styles.navSubtitle}>{selectedRoute?.distance_km} km • {selectedRoute?.duration_minutes} min</Text>
             </View>
             <TouchableOpacity style={styles.exitNavButton} onPress={exitNavigation}>
                 <Text style={styles.exitNavText}>EXIT</Text>
             </TouchableOpacity>
          </View>
      )}
      
      {mode === 'IDLE' && (
          <>
            <TouchableOpacity style={styles.historyButton} onPress={() => router.push('/history')}>
                <Text style={styles.historyButtonText}>🕒</Text>
            </TouchableOpacity>
            <TouchableOpacity style={styles.profileButton} onPress={() => router.push('/profile')}>
                <Text style={styles.profileButtonText}>👤</Text>
            </TouchableOpacity>
            <View style={styles.listenOverlay}>
                <View style={styles.topCard}>
                    <Text style={styles.greeting}>Hi, {user?.full_name}</Text>
                    <Text style={styles.subtitle}>Ready for a ride?</Text>
                </View>
            </View>
          </>
      )}

      <DestinationPicker 
          isPicking={mode === 'PICKING_DEST'}
          onConfirm={confirmDestination}
          onCancel={cancelSelection}
          onLocationSelect={(lat, lon) => {
              const coords = { latitude: lat, longitude: lon, latitudeDelta: 0, longitudeDelta: 0 };
              setDestination(coords);
              mapRef.current?.animateToRegion({
                  latitude: lat,
                  longitude: lon,
                  latitudeDelta: 0.005,
                  longitudeDelta: 0.005
              }, 1000);
          }}
      />

       {analyzing && (
           <View style={styles.centerLoading}>
               <ActivityIndicator size="large" color={COLORS.primary} />
               <Text style={styles.loadingText}>Finding best routes...</Text>
           </View>
       )}

      {mode === 'SELECT_ROUTE' && (
          <RouteSelector 
              routes={availableRoutes}
              selectedRouteId={selectedRoute?.id || null}
              onSelect={(r) => { setSelectedRoute(r); fitToRoute(r); }}
              onConfirm={handleRouteConfirm}
              onNavigate={startNavigation}
              onForecast={handleForecast}
              onCancel={cancelSelection}
          />
      )}

      {mode === 'IDLE' && (
          <View style={styles.bottomSheet}>
            <Text style={styles.sheetTitle}>Where to?</Text>
            <TouchableOpacity style={styles.requestButton} onPress={startDestinationPick}>
                <Text style={styles.buttonText}>Tap to Select on Map 📍</Text>
            </TouchableOpacity>
          </View>
      )}

      {(mode === 'CONFIRMING' || mode === 'REQUESTING') && (
          <RideRequestSheet 
              distanceKm={getDistance()}
              onRequest={(type) => handleRequestRide(type as 'moto' | 'car')}
              isLoading={mode === 'REQUESTING'}
              onClose={() => setMode('SELECT_ROUTE')}
          />
      )}

      {(mode === 'IDLE' || mode === 'NAVIGATING') && (
          <TouchableOpacity style={styles.fab} onPress={() => setShowIncidentModal(true)}>
            <Text style={styles.fabText}>⚠️</Text>
          </TouchableOpacity>
      )}

      <IncidentReportModal
        visible={showIncidentModal}
        onClose={() => setShowIncidentModal(false)}
        location={location ? { latitude: location.latitude, longitude: location.longitude } : null}
        onReportSuccess={() => { if (location) fetchIncidents(location.latitude, location.longitude); }}
      />

      <IncidentDetailModal
        incident={selectedIncident}
        visible={selectedIncident !== null}
        onClose={() => setSelectedIncident(null)}
        onVerified={() => { if (location) fetchIncidents(location.latitude, location.longitude); }}
      />

      <CustomAlert 
        visible={alertConfig.visible} 
        title={alertConfig.title} 
        message={alertConfig.message} 
        buttons={alertConfig.buttons}
        onClose={closeAlert}
      />
    </View>
  );
}

const styles = StyleSheet.create({
  container: { flex: 1, backgroundColor: COLORS.background },
  loadingContainer: { flex: 1, justifyContent: 'center', alignItems: 'center', backgroundColor: COLORS.background },
  map: { width: Dimensions.get('window').width, height: Dimensions.get('window').height },
  historyButton: {
    position: 'absolute', top: 60, left: 20,
    backgroundColor: COLORS.card, padding: 12, borderRadius: 25,
    ...SHADOWS.medium, zIndex: 10, borderWidth: 1, borderColor: COLORS.border,
  },
  historyButtonText: { fontSize: 20 },
  profileButton: {
    position: 'absolute', top: 60, right: 20,
    backgroundColor: COLORS.card, padding: 12, borderRadius: 25,
    ...SHADOWS.medium, zIndex: 10, borderWidth: 1, borderColor: COLORS.border,
  },
  profileButtonText: { fontSize: 20 },
  topCard: {
    padding: 20, borderRadius: 16,
    ...SHADOWS.medium, borderWidth: 1, borderColor: COLORS.border,
    backgroundColor: 'rgba(30, 41, 59, 1)', // Solid background for better readability
  },
  listenOverlay: { position: 'absolute', top: 110, left: 20, right: 20 }, // Moved up from 160 to 110
  greeting: { ...TYPOGRAPHY.header, color: COLORS.primary },
  subtitle: { ...TYPOGRAPHY.body, marginTop: 4 },
  bottomSheet: {
    position: 'absolute', bottom: 0, left: 0, right: 0,
    backgroundColor: COLORS.card, padding: 24, paddingBottom: 40,
    borderTopLeftRadius: 24, borderTopRightRadius: 24,
    ...SHADOWS.medium, borderTopWidth: 1, borderTopColor: COLORS.border,
  },
  sheetTitle: { ...TYPOGRAPHY.header, marginBottom: 20 },
  requestButton: {
    backgroundColor: COLORS.card, padding: 18, borderRadius: 16, alignItems: 'center',
    borderWidth: 1, borderColor: COLORS.primary, flexDirection: 'row', justifyContent: 'center', gap: 10,
  },
  buttonText: { color: COLORS.primary, fontSize: 16, fontWeight: 'bold' },
  fab: {
      position: 'absolute', bottom: 220, right: 20,
      backgroundColor: COLORS.danger, width: 56, height: 56, borderRadius: 28,
      justifyContent: 'center', alignItems: 'center', ...SHADOWS.neon, zIndex: 20,
  },
  fabText: { fontSize: 24 },
  incidentMarker: {
      backgroundColor: COLORS.card, padding: 8, borderRadius: 20, borderWidth: 2, borderColor: COLORS.danger,
  },
  driverMarker: {
      backgroundColor: COLORS.background, padding: 8, borderRadius: 20,
      borderWidth: 2, borderColor: COLORS.primary, ...SHADOWS.small
  },
  centerLoading: {
      ...StyleSheet.absoluteFillObject, justifyContent: 'center', alignItems: 'center',
      backgroundColor: 'rgba(0,0,0,0.5)', zIndex: 100,
  },
  loadingText: { marginTop: 10, color: COLORS.text, fontWeight: 'bold' },
  // Nav
  navOverlay: {
      position: 'absolute', top: 60, left: 20, right: 20,
      flexDirection: 'row', justifyContent: 'space-between', alignItems: 'center', zIndex: 100,
  },
  navHeader: {
      backgroundColor: COLORS.card, padding: 15, borderRadius: 12, flex: 1, marginRight: 15,
      borderWidth: 1, borderColor: COLORS.border, ...SHADOWS.medium,
  },
  navTitle: { color: COLORS.text, fontWeight: 'bold', fontSize: 16 },
  navSubtitle: { color: COLORS.textDim, fontSize: 14, marginTop: 2 },
  exitNavButton: {
      backgroundColor: COLORS.danger, padding: 15, borderRadius: 12, ...SHADOWS.medium,
  },
  exitNavText: { color: 'white', fontWeight: 'bold' }
});
