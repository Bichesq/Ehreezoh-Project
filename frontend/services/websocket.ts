/**
 * WebSocket Service
 * Real-time communication with backend
 */

type MessageHandler = (data: any) => void;

interface WebSocketMessage {
  type: string;
  data: any;
  timestamp: string;
  metadata?: any;
}

class WebSocketService {
  private ws: WebSocket | null = null;
  private reconnectAttempts = 0;
  private maxReconnectAttempts = 5;
  private reconnectDelay = 2000; // 2 seconds
  private listeners = new Map<string, MessageHandler[]>();
  private userId: string | null = null;
  private token: string | null = null;
  private reconnectTimeout: NodeJS.Timeout | null = null;
  private pingInterval: NodeJS.Timeout | null = null;

  /**
   * Connect to WebSocket server
   */
  connect(userId: string, token: string) {
    this.userId = userId;
    this.token = token;

    const envUrl = process.env.NEXT_PUBLIC_WS_URL || process.env.NEXT_PUBLIC_API_URL || 'ws://localhost:8000/api/v1';
    
    // Convert http/https to ws/wss if needed
    let baseUrl = envUrl;
    if (baseUrl.startsWith('http://')) {
        baseUrl = baseUrl.replace('http://', 'ws://');
    } else if (baseUrl.startsWith('https://')) {
        baseUrl = baseUrl.replace('https://', 'wss://');
    }
    
    // Remove trailing slash if present
    baseUrl = baseUrl.replace(/\/$/, '');
    
    // Remove trailing /ws if present to avoid duplication
    const cleanBaseUrl = baseUrl.endsWith('/ws') ? baseUrl.slice(0, -3) : baseUrl;

    console.log('🔌 Connecting to WebSocket:', `${cleanBaseUrl}/ws/connect`);
    const wsUrl = `${cleanBaseUrl}/ws/connect?token=${token}`;

    try {
      this.ws = new WebSocket(wsUrl);

      this.ws.onopen = () => {
        console.log('✅ WebSocket connected');
        this.reconnectAttempts = 0;
        this.startPing();
        this.emit('connected', { userId });
      };

      this.ws.onmessage = (event) => {
        try {
          const message: WebSocketMessage = JSON.parse(event.data);
          console.log('📨 WebSocket message:', message.type, message.data);
          this.emit(message.type, message.data);
        } catch (error) {
          console.error('❌ Error parsing WebSocket message:', error);
        }
      };

      this.ws.onerror = (error) => {
        console.error('❌ WebSocket error:', error);
        this.emit('error', error);
      };

      this.ws.onclose = () => {
        console.log('🔌 WebSocket disconnected');
        this.stopPing();
        this.emit('disconnected', {});
        this.handleReconnect();
      };
    } catch (error) {
      console.error('❌ Error creating WebSocket:', error);
      this.handleReconnect();
    }
  }

  /**
   * Disconnect from WebSocket server
   */
  disconnect() {
    this.reconnectAttempts = this.maxReconnectAttempts; // Prevent reconnection
    if (this.reconnectTimeout) {
      clearTimeout(this.reconnectTimeout);
      this.reconnectTimeout = null;
    }
    this.stopPing();
    if (this.ws) {
      this.ws.close();
      this.ws = null;
    }
    this.listeners.clear();
  }

  /**
   * Handle reconnection logic
   */
  private handleReconnect() {
    if (this.reconnectAttempts >= this.maxReconnectAttempts) {
      console.error('❌ Max reconnection attempts reached');
      this.emit('reconnect_failed', {});
      return;
    }

    this.reconnectAttempts++;
    const delay = this.reconnectDelay * this.reconnectAttempts;

    console.log(`🔄 Reconnecting in ${delay}ms (attempt ${this.reconnectAttempts}/${this.maxReconnectAttempts})`);

    this.reconnectTimeout = setTimeout(() => {
      if (this.userId && this.token) {
        this.connect(this.userId, this.token);
      }
    }, delay);
  }

  /**
   * Start ping interval to keep connection alive
   */
  private startPing() {
    this.pingInterval = setInterval(() => {
      this.send('ping', {});
    }, 30000); // 30 seconds
  }

  /**
   * Stop ping interval
   */
  private stopPing() {
    if (this.pingInterval) {
      clearInterval(this.pingInterval);
      this.pingInterval = null;
    }
  }

  /**
   * Send message to server
   */
  send(type: string, data: any) {
    if (this.ws && this.ws.readyState === WebSocket.OPEN) {
      const message = {
        type,
        ...data,
      };
      this.ws.send(JSON.stringify(message));
      console.log('📤 WebSocket send:', type, data);
    } else {
      console.warn('⚠️ WebSocket not connected, cannot send:', type);
    }
  }

  /**
   * Subscribe to ride updates
   */
  subscribeToRide(rideId: string) {
    this.send('join_ride', { ride_id: rideId });
  }

  /**
   * Unsubscribe from ride updates
   */
  unsubscribeFromRide(rideId: string) {
    this.send('leave_ride', { ride_id: rideId });
  }

  /**
   * Register event listener
   */
  on(event: string, callback: MessageHandler) {
    if (!this.listeners.has(event)) {
      this.listeners.set(event, []);
    }
    this.listeners.get(event)!.push(callback);
  }

  /**
   * Unregister event listener
   */
  off(event: string, callback: MessageHandler) {
    if (this.listeners.has(event)) {
      const handlers = this.listeners.get(event)!;
      const index = handlers.indexOf(callback);
      if (index > -1) {
        handlers.splice(index, 1);
      }
    }
  }

  /**
   * Emit event to all registered listeners
   */
  private emit(event: string, data: any) {
    const handlers = this.listeners.get(event) || [];
    handlers.forEach((handler) => {
      try {
        handler(data);
      } catch (error) {
        console.error(`❌ Error in event handler for ${event}:`, error);
      }
    });
  }

  /**
   * Check if WebSocket is connected
   */
  isConnected(): boolean {
    return this.ws !== null && this.ws.readyState === WebSocket.OPEN;
  }
}

// Global WebSocket service instance
export const wsService = new WebSocketService();

export default wsService;
