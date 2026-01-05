import React, { useState, useEffect } from 'react';
import { View, Text, StyleSheet, TouchableOpacity, TextInput, FlatList, ActivityIndicator, Keyboard } from 'react-native';
import { mapService, PlaceResult } from '../services/map';
import { locationService } from '../services/location';

interface DestinationPickerProps {
    onConfirm: () => void;
    onCancel: () => void;
    onLocationSelect: (lat: number, lon: number) => void;
    isPicking: boolean;
}

import { COLORS } from '../constants/colors';
import { SHADOWS, LAYOUT, TYPOGRAPHY } from '../constants/theme';

export default function DestinationPicker({ onConfirm, onCancel, onLocationSelect, isPicking }: DestinationPickerProps) {
    const [query, setQuery] = useState('');
    const [results, setResults] = useState<PlaceResult[]>([]);
    const [loading, setLoading] = useState(false);
    
    // Debounce Search
    useEffect(() => {
        const timer = setTimeout(async () => {
            if (query.length >= 2) {
                setLoading(true);
                const loc = await locationService.getCurrentPosition(); // Optional: could pass as prop to avoid async here
                const places = await mapService.searchPlaces(query, loc || undefined);
                setResults(places);
                setLoading(false);
            } else {
                setResults([]);
            }
        }, 500);

        return () => clearTimeout(timer);
    }, [query]);

    if (!isPicking) return null;

    return (
        <View style={styles.container} pointerEvents="box-none">
            {/* Search Bar */}
            <View style={styles.searchContainer}>
                <TextInput
                    style={styles.searchInput}
                    placeholder="Where to? (e.g. Mvan Market)"
                    placeholderTextColor={COLORS.textDim}
                    value={query}
                    onChangeText={setQuery}
                />
                {loading && <ActivityIndicator style={styles.loader} color={COLORS.primary} />}
            </View>

            {/* Results List */}
            {results.length > 0 && (
                <View style={styles.resultsList}>
                    <FlatList
                        data={results}
                        keyExtractor={item => item.id}
                        keyboardShouldPersistTaps="handled"
                        renderItem={({ item }) => (
                            <TouchableOpacity 
                                style={styles.resultItem}
                                onPress={() => {
                                    onLocationSelect(item.latitude, item.longitude);
                                    setResults([]); // Clear results
                                    setQuery(item.name); // Set text
                                    Keyboard.dismiss();
                                }}
                            >
                                <Text style={styles.resultName}>{item.name}</Text>
                                <Text style={styles.resultDesc} numberOfLines={1}>{item.description}</Text>
                            </TouchableOpacity>
                        )}
                    />
                </View>
            )}

            {/* Center Pin Marker */}
            <View style={styles.centerMarkerContainer} pointerEvents="none">
                <View style={styles.pinPoint} />
                <View style={styles.pinHead}>
                    <Text style={styles.pinText}>📍</Text>
                </View>
            </View>

            {/* Bottom Controls */}
            <View style={styles.bottomContainer}>
                <Text style={styles.instructionText}>Move map to adjust pin</Text>
                
                <View style={styles.buttonRow}>
                    <TouchableOpacity style={styles.cancelButton} onPress={onCancel}>
                        <Text style={styles.cancelButtonText}>Cancel</Text>
                    </TouchableOpacity>
                    
                    <TouchableOpacity style={styles.confirmButton} onPress={onConfirm}>
                        <Text style={styles.confirmButtonText}>Confirm Dropoff</Text>
                    </TouchableOpacity>
                </View>
            </View>
        </View>
    );
}

const styles = StyleSheet.create({
    container: {
        ...StyleSheet.absoluteFillObject,
        justifyContent: 'center',
        alignItems: 'center',
        zIndex: 200, // Above everything
    },
    centerMarkerContainer: {
        alignItems: 'center',
        justifyContent: 'center',
        marginBottom: 40, // Offset to make the pin point at the center center
    },
    pinHead: {
        marginBottom: 5,
    },
    pinText: {
        fontSize: 40,
    },
    pinPoint: {
        width: 4,
        height: 4,
        borderRadius: 2,
        backgroundColor: COLORS.text,
        position: 'absolute',
        bottom: 0,
    },
    bottomContainer: {
        position: 'absolute',
        bottom: 40,
        left: 20,
        right: 20,
        backgroundColor: COLORS.card,
        padding: 24,
        borderRadius: 24,
        ...SHADOWS.medium,
        borderWidth: 1,
        borderColor: COLORS.border,
        alignItems: 'center',
    },
    instructionText: {
        marginBottom: 20,
        color: COLORS.textDim,
        ...TYPOGRAPHY.subheader,
    },
    buttonRow: {
        flexDirection: 'row',
        width: '100%',
        justifyContent: 'space-between',
        gap: 15,
    },
    cancelButton: {
        flex: 1,
        padding: 16,
        backgroundColor: COLORS.background, // Darker
        borderRadius: 16,
        alignItems: 'center',
        borderWidth: 1,
        borderColor: COLORS.border,
    },
    cancelButtonText: {
        color: COLORS.textDim,
        fontWeight: 'bold',
    },
    confirmButton: {
        flex: 2,
        padding: 16,
        backgroundColor: COLORS.primary,
        borderRadius: 16,
        alignItems: 'center',
        ...SHADOWS.neon,
    },

    confirmButtonText: {
        color: COLORS.background,
        fontWeight: 'bold',
    },
    searchContainer: {
        position: 'absolute',
        top: 60,
        left: 20,
        right: 20,
        zIndex: 201,
        flexDirection: 'row',
        alignItems: 'center',
    },
    searchInput: {
        flex: 1,
        backgroundColor: COLORS.card,
        padding: 16,
        borderRadius: 16,
        fontSize: 16,
        borderWidth: 1,
        borderColor: COLORS.border,
        color: COLORS.text,
        ...SHADOWS.medium,
    },
    loader: {
        position: 'absolute',
        right: 16,
    },
    resultsList: {
        position: 'absolute',
        top: 120, // Below search bar
        left: 20,
        right: 20,
        backgroundColor: COLORS.card,
        borderRadius: 16,
        maxHeight: 200,
        zIndex: 202,
        ...SHADOWS.medium,
        borderWidth: 1,
        borderColor: COLORS.border,
    },
    resultItem: {
        padding: 16,
        borderBottomWidth: 1,
        borderBottomColor: COLORS.border,
    },
    resultName: {
        fontWeight: 'bold',
        color: COLORS.text,
        marginBottom: 4,
    },
    resultDesc: {
        color: COLORS.textDim,
        fontSize: 12,
    },
});
