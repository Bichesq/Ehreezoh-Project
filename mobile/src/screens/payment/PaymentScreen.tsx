import React, { useState } from 'react';
import { View, Text, StyleSheet, TouchableOpacity, TextInput, ActivityIndicator, Alert, Image } from 'react-native';
import { StatusBar } from 'expo-status-bar';
import { rideService } from '../../services/ride';
import { useRouter } from 'expo-router';

interface PaymentScreenProps {
  ride: any;
  onPaymentComplete: () => void;
  onCancel?: () => void;
}

const PROVIDERS = [
  { id: 'momo', name: 'MTN Mobile Money', color: '#FFCC00' },
  { id: 'om', name: 'Orange Money', color: '#FF7900' },
  { id: 'cash', name: 'Cash', color: '#4CAF50' },
];

export default function PaymentScreen({ ride, onPaymentComplete, onCancel }: PaymentScreenProps) {
  const [selectedProvider, setSelectedProvider] = useState<string | null>(null);
  const [phoneNumber, setPhoneNumber] = useState('');
  const [processing, setProcessing] = useState(false);
  const router = useRouter();

  const handlePay = async () => {
    if (!selectedProvider) {
      Alert.alert('Select Method', 'Please select a payment method.');
      return;
    }
    
    if ((selectedProvider === 'momo' || selectedProvider === 'om') && phoneNumber.length < 9) {
      Alert.alert('Phone Number Invalid', 'Please enter a valid phone number.');
      return;
    }

    setProcessing(true);
    try {
      // Use ride.passenger_phone used for mock if user doesn't enter one? No, force entry.
      // Or auto-fill from user profile (future task).
      const finalPhone = selectedProvider === 'cash' ? '000000000' : phoneNumber;
      
      const result = await rideService.initiatePayment(ride.id, selectedProvider, finalPhone);
      
      Alert.alert('Payment Successful', `Transaction ID: ${result.transaction_id || 'Cash'}`);
      onPaymentComplete();
    } catch (error: any) {
      console.error('Payment Error:', error);
      Alert.alert('Payment Failed', error.response?.data?.detail || 'Transaction failed.');
    } finally {
      setProcessing(false);
    }
  };

  const amount = ride.final_fare || ride.estimated_fare;

  return (
    <View style={styles.container}>
      <StatusBar style="dark" />
      <View style={styles.card}>
        <Text style={styles.title}>Payment</Text>
        
        <View style={styles.amountContainer}>
            <Text style={styles.label}>Total Amount</Text>
            <Text style={styles.amount}>{amount.toLocaleString()} XAF</Text>
        </View>

        <Text style={styles.sectionTitle}>Select Payment Method</Text>
        <View style={styles.providersList}>
            {PROVIDERS.map((provider) => (
                <TouchableOpacity 
                    key={provider.id} 
                    style={[
                        styles.providerItem, 
                        selectedProvider === provider.id && styles.selectedProvider,
                        { borderColor: selectedProvider === provider.id ? provider.color : '#e0e0e0' }
                    ]}
                    onPress={() => setSelectedProvider(provider.id)}
                >
                    <View style={[styles.radio, selectedProvider === provider.id && { backgroundColor: provider.color }]} />
                    <Text style={styles.providerName}>{provider.name}</Text>
                </TouchableOpacity>
            ))}
        </View>

        {(selectedProvider === 'momo' || selectedProvider === 'om') && (
            <View style={styles.inputContainer}>
                <Text style={styles.label}>Mobile Number</Text>
                <TextInput 
                    style={styles.input}
                    placeholder="6XXXXXXXX"
                    keyboardType="phone-pad"
                    value={phoneNumber}
                    onChangeText={setPhoneNumber}
                />
            </View>
        )}

        {selectedProvider === 'cash' && (
            <Text style={styles.cashNote}>
                Please hand over exact change to the driver.
            </Text>
        )}

        <View style={styles.buttonRow}>
            {onCancel && (
                <TouchableOpacity style={styles.cancelButton} onPress={onCancel} disabled={processing}>
                    <Text style={styles.cancelButtonText}>Cancel</Text>
                </TouchableOpacity>
            )}
            
            <TouchableOpacity 
                style={[styles.payButton, processing && styles.disabledButton]} 
                onPress={handlePay}
                disabled={processing}
            >
                {processing ? (
                   <ActivityIndicator color="#fff" />
                ) : (
                   <Text style={styles.payButtonText}>PAY NOW</Text>
                )}
            </TouchableOpacity>
        </View>
      </View>
    </View>
  );
}

const styles = StyleSheet.create({
  container: {
    ...StyleSheet.absoluteFillObject,
    backgroundColor: 'rgba(0,0,0,0.5)', 
    justifyContent: 'flex-end',
  },
  card: {
    backgroundColor: '#fff',
    borderTopLeftRadius: 20,
    borderTopRightRadius: 20,
    padding: 20,
    paddingBottom: 40,
    minHeight: 500,
  },
  title: {
    fontSize: 24,
    fontWeight: 'bold',
    marginBottom: 20,
    textAlign: 'center',
  },
  amountContainer: {
    alignItems: 'center',
    marginBottom: 30,
    backgroundColor: '#f9f9f9',
    padding: 15,
    borderRadius: 12,
  },
  amount: {
    fontSize: 36,
    fontWeight: 'bold',
    color: '#000',
  },
  label: {
    fontSize: 14,
    color: '#666',
    marginBottom: 5,
  },
  sectionTitle: {
    fontSize: 16,
    fontWeight: '600',
    marginBottom: 15,
  },
  providersList: {
    marginBottom: 20,
  },
  providerItem: {
    flexDirection: 'row',
    alignItems: 'center',
    padding: 15,
    borderWidth: 2,
    borderRadius: 12,
    marginBottom: 10,
  },
  selectedProvider: {
    backgroundColor: '#fff',
  },
  radio: {
    width: 20,
    height: 20,
    borderRadius: 10,
    borderWidth: 2,
    borderColor: '#ccc',
    marginRight: 15,
  },
  providerName: {
    fontSize: 16,
    fontWeight: '500',
  },
  inputContainer: {
    marginBottom: 20,
  },
  input: {
    borderWidth: 1,
    borderColor: '#ddd',
    padding: 15,
    borderRadius: 12,
    fontSize: 18,
  },
  cashNote: {
    textAlign: 'center',
    color: '#666',
    marginBottom: 20,
    fontStyle: 'italic',
  },
  buttonRow: {
    flexDirection: 'row',
    marginTop: 10,
  },
  cancelButton: {
    flex: 1,
    padding: 18,
    marginRight: 10,
    alignItems: 'center',
  },
  cancelButtonText: {
    color: '#F44336',
    fontSize: 16,
    fontWeight: 'bold',
  },
  payButton: {
    flex: 2,
    backgroundColor: '#000',
    padding: 18,
    borderRadius: 12,
    alignItems: 'center',
  },
  disabledButton: {
    backgroundColor: '#999',
  },
  payButtonText: {
    color: 'white',
    fontSize: 18,
    fontWeight: 'bold',
  },
});
