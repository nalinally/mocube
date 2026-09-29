import time
import threading
import params
import socket

class State():
    
    def __init__(self, timeout):
        self.devices = {}
        self.timeout = timeout
        self.lock = threading.Lock()
        
    def set_device(self, mac, id, addr):
        with self.lock:
            self.devices[mac] = {"id": id, "addr": addr, "last_seen": time.time(), "online": True}
        
    def set_addr(self, mac, addr):
        with self.lock:
            self.devices[mac]["addr"] = addr
        
    def init_device(self, devices):
        with self.lock:
            self.devices = devices
            for device in self.devices:
                device["last_seen"] = time.time()
                device["online"] = False
            
    def get_device(self):
        with self.lock:
            # print(f"2:{type(self.devices)}")
            return self.devices
        
    def heart_beat(self, mac):
        with self.lock:
            self.devices[mac]["last_seen"] = time.time()
            self.devices[mac]["online"] = True
        
    def update(self):
        now = time.time()
        with self.lock:
            for mac in self.devices.keys():
                if now - self.devices[mac].get("last_seen", 99999) > self.timeout:
                    self.devices[mac]["online"] = False
                    
    def acquire(self):
        self.lock.acquire()
        
    def release(self):
        self.lock.release()
                
        
state = State(params.TIMEOUT)
    
    