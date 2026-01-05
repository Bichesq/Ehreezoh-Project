import React from 'react';
import { View, Text, StyleSheet, Modal, TouchableOpacity, Dimensions } from 'react-native';
import { COLORS } from '../constants/colors';
import { SHADOWS, TYPOGRAPHY } from '../constants/theme';

export interface AlertButton {
    text: string;
    onPress?: () => void;
    style?: 'default' | 'cancel' | 'destructive';
}

interface CustomAlertProps {
    visible: boolean;
    title: string;
    message?: string;
    buttons?: AlertButton[];
    onClose?: () => void; // Called on backdrop press or default close
}

export default function CustomAlert({ visible, title, message, buttons, onClose }: CustomAlertProps) {
    if (!visible) return null;

    const renderButtons = () => {
        const btnList = buttons || [{ text: 'OK', onPress: onClose }];
        
        return (
            <View style={styles.buttonRow}>
                {btnList.map((btn, index) => (
                    <TouchableOpacity 
                        key={index} 
                        style={[
                            styles.button, 
                            btn.style === 'cancel' ? styles.cancelBtn : 
                            btn.style === 'destructive' ? styles.destructiveBtn : styles.defaultBtn
                        ]}
                        onPress={() => {
                            if (btn.onPress) btn.onPress();
                            if (onClose && !btn.onPress) onClose(); // Auto close if no press handler but close exists
                        }}
                    >
                        <Text style={[
                            styles.btnText, 
                            btn.style === 'cancel' ? styles.cancelText : styles.defaultText
                        ]}>
                            {btn.text.toUpperCase()}
                        </Text>
                    </TouchableOpacity>
                ))}
            </View>
        );
    };

    return (
        <Modal transparent visible={visible} animationType="fade" onRequestClose={onClose}>
            <View style={styles.overlay}>
                <View style={styles.alertBox}>
                    <Text style={styles.title}>{title}</Text>
                    {message && <Text style={styles.message}>{message}</Text>}
                    {renderButtons()}
                </View>
            </View>
        </Modal>
    );
}

const styles = StyleSheet.create({
    overlay: {
        flex: 1,
        backgroundColor: 'rgba(0,0,0,0.7)',
        justifyContent: 'center',
        alignItems: 'center',
        padding: 40,
    },
    alertBox: {
        width: '100%',
        backgroundColor: '#000000', // Pitch black
        borderRadius: 16,
        padding: 24,
        borderWidth: 1,
        borderColor: '#ff0033', // Neon Red
        shadowColor: '#ff0033',
        shadowOffset: { width: 0, height: 0 },
        shadowOpacity: 0.8,
        shadowRadius: 15,
        elevation: 20, // Strong Android glow
        alignItems: 'center',
    },
    title: {
        color: '#ff0033', // Neon Red Title
        fontSize: 20,
        fontWeight: 'bold',
        marginBottom: 12,
        textAlign: 'center',
        textShadowColor: 'rgba(255, 0, 51, 0.5)',
        textShadowOffset: { width: 0, height: 0 },
        textShadowRadius: 10,
    },
    message: {
        color: '#ffffff',
        fontSize: 14,
        textAlign: 'center',
        marginBottom: 24,
        lineHeight: 20,
    },
    buttonRow: {
        flexDirection: 'row',
        justifyContent: 'center',
        gap: 16,
        width: '100%',
    },
    button: {
        paddingVertical: 12,
        paddingHorizontal: 20,
        borderRadius: 8,
        minWidth: 80,
        alignItems: 'center',
    },
    defaultBtn: {
        backgroundColor: 'rgba(255, 0, 51, 0.1)',
        borderWidth: 1,
        borderColor: '#ff0033',
    },
    destructiveBtn: {
        backgroundColor: 'rgba(255, 0, 51, 0.3)',
        borderWidth: 1,
        borderColor: '#ff0033',
    },
    cancelBtn: {
        backgroundColor: 'transparent',
    },
    btnText: {
        fontWeight: 'bold',
        fontSize: 14,
    },
    defaultText: {
        color: '#ff0033',
    },
    cancelText: {
        color: '#888',
    },
});
