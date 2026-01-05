import socket
import sys
import time

def check_port(host, port):
    print(f"Checking connectivity to {host}:{port}...")
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.settimeout(3)
    try:
        result = sock.connect_ex((host, port))
        if result == 0:
            print("Success! Port is open and reachable.")
            return True
        else:
            print(f"Failure. Port is not reachable (ErrorCode: {result}).")
            return False
    except Exception as e:
        print(f"Error checking port: {e}")
        return False
    finally:
        sock.close()

if __name__ == "__main__":
    host = "192.168.1.4"
    port = 8000
    
    # Try multiple times
    for i in range(3):
        if check_port(host, port):
            sys.exit(0)
        time.sleep(1)
        
    print("Could not connect after multiple attempts.")
    sys.exit(1)
