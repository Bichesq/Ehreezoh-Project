import { Alert } from 'react-native';
import { WS_URL } from '../config';

type WebSocketListener = (data: any) => void;

class SocketService {
  private ws: WebSocket | null = null;
  private listeners: Set<WebSocketListener> = new Set();
  private reconnectInterval: NodeJS.Timeout | null = null;
  private token: string | null = null;

  connect(token: string) {
    if (this.ws && (this.ws.readyState === WebSocket.OPEN || this.ws.readyState === WebSocket.CONNECTING)) return;
    
    this.token = token;
    // Append token to URL query params
    const wsUrl = `${WS_URL}?token=${token}`;
    console.log(`🔌 Connecting to WebSocket: ${WS_URL}`);
    console.log('🔑 Token being sent:', token ? `${token.substring(0, 10)}...` : 'None');

    this.ws = new WebSocket(wsUrl);

    this.ws.onopen = () => {
      console.log('✅ WebSocket Connected');
      if (this.reconnectInterval) {
        clearInterval(this.reconnectInterval);
        this.reconnectInterval = null;
      }
    };

    this.ws.onmessage = (event) => {
      try {
        const data = JSON.parse(event.data);
        // console.log('📩 WS Message:', data.type);
        this.notifyListeners(data);
      } catch (e) {
        console.error('❌ WS Parse Error:', e);
      }
    };

    this.ws.onclose = (e) => {
      console.log('⚠️ WebSocket Disconnected', e.code, e.reason);
      
      // Check for authentication error (403 Forbidden)
      if (e.reason && (e.reason.includes('403') || e.reason.includes('Forbidden'))) {
          console.log('🔒 Auth Error Detected. Triggering logout...');
          this.notifyListeners({ type: 'auth_error', data: { message: 'Session expired' } });
          return; // Do not reconnect
      }

      this.attemptReconnect();
    };

    this.ws.onerror = (e) => {
      console.error('❌ WebSocket Error:', (e as any).message);
      const msg = (e as any).message || 'Unknown error';
      // Only alert if it's a connection failure (not just a closure)
      import('react-native').then(({ Alert }) => {
          Alert.alert('WebSocket Error', `Failed to connect: ${msg}\nURL: ${this.ws?.url}`);
      });
    };
  }

  disconnect() {
    if (this.ws) {
      this.ws.close();
      this.ws = null;
    }
    if (this.reconnectInterval) {
      clearInterval(this.reconnectInterval);
      this.reconnectInterval = null;
    }
  }

  send(type: string, data: any = {}) {
    if (this.ws && this.ws.readyState === WebSocket.OPEN) {
      this.ws.send(JSON.stringify({ type, data }));
    } else {
      console.warn('⚠️ Cannot send message, WebSocket not open');
    }
  }

  addListener(listener: WebSocketListener) {
    this.listeners.add(listener);
    return () => this.listeners.delete(listener);
  }

  private notifyListeners(data: any) {
    this.listeners.forEach((listener) => listener(data));
  }

  private attemptReconnect() {
    if (!this.reconnectInterval && this.token) {
      console.log('🔄 Attempting to reconnect in 5s...');
      this.reconnectInterval = setInterval(() => {
        if (this.token) this.connect(this.token);
      }, 5000);
    }
  }
  joinChat(roomId: string) {
    this.send('join_chat', { room_id: roomId });
  }

  leaveChat(roomId: string) {
    this.send('leave_chat', { room_id: roomId });
  }

  sendTyping(roomId: string, isTyping: boolean) {
    this.send('typing', { room_id: roomId, is_typing: isTyping });
  }
}

export const socketService = new SocketService();
