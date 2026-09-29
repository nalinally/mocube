import os
import json
import socket
import threading

import params
import state

next_id = 0

def load_from_json():
    
    global next_id
    
    if os.path.exists(params.DEVICE_FILE):

        try:
            print("1")
            with open(params.DEVICE_FILE, "r") as f:
                devices = json.load(f)

            print("2")
            # JSONではIDが数字になっていることを保証
            state.state.init_device({
                str(mac): {"id": int(data["id"]), "addr": str(data["addr"])}
                for mac, data in devices.items()
            })
            print("3")
            if devices:
                next_id = max(devices.values()) + 1
            print("4")
            print(f"Loaded {len(devices)} devices.")

        except Exception as e:
            print(f"Could not load {params.DEVICE_FILE}: {e}")
    
    print("hoge")
    print(type(state.state.get_device()))
    print(state.state.get_device())
            
def save_devices():

    with open(params.DEVICE_FILE, "w") as f:
        json.dump(
            state.state.get_device(),
            f,
            indent=4
        )
        
def get_device_id(mac, addr):

    global next_id

    # 既に登録されている
    devices = state.state.get_device()
    if mac in devices:
        state.state.set_addr(mac, addr)
        return devices[mac]["id"]

    # 新しいデバイス
    device_id = next_id

    state.state.set_device(mac, device_id, addr)

    next_id += 1

    save_devices()

    print()
    print("================================")
    print(" New AtomS3 detected")
    print(f" MAC : {mac}")
    print(f" ID  : {device_id}")
    print("================================")

    return device_id

def receive_loop(sock):

    while True:

        try:

            data, addr = sock.recvfrom(1024)

            message = data.decode(
                "utf-8",
                errors="ignore"
            ).strip()

            parts = message.split(",")

            if len(parts) < 2:
                continue

            command = parts[0]
            mac = parts[1].upper()

            # ------------------------------------------------
            # REGISTER
            # ------------------------------------------------

            if command == "REGISTER":

                device_id = get_device_id(mac, addr[0])                    

                response = f"ID,{device_id}"

                sock.sendto(
                    response.encode(),
                    addr
                )

                print(
                    f"REGISTER: ID={device_id}, "
                    f"MAC={mac}, IP={addr[0]}"
                )

            # ------------------------------------------------
            # HEARTBEAT
            # ------------------------------------------------

            elif command == "HEARTBEAT":

                device_id = get_device_id(mac, addr[0])

                response = f"ACK,{device_id}"

                sock.sendto(
                    response.encode(),
                    addr
                )
                
                state.state.heart_beat(mac)

        except Exception as e:


            print(f"Receive error: {e}")


def initUDP():

    sock = socket.socket(
        socket.AF_INET,
        socket.SOCK_DGRAM
    )

    # UDP broadcastを許可
    sock.setsockopt(
        socket.SOL_SOCKET,
        socket.SO_BROADCAST,
        1
    )

    # 全てのネットワークインターフェースで受信
    sock.bind(
        ("0.0.0.0", params.PORT)
    )

    print(
        f"AtomS3 server started "
        f"(UDP port {params.PORT})"
    )

    # 受信スレッド
    thread = threading.Thread(
        target=receive_loop,
        args=(sock,),
        daemon=True
    )

    thread.start()
    
def init():
    load_from_json()
    initUDP()