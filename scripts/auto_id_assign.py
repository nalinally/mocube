import socket
import json
import time
import os
import threading

# ============================================================
# Settings
# ============================================================

PORT = 5000

# Heartbeatがこの秒数来なければOFFLINE
TIMEOUT = 3.0

# MAC -> ID の保存ファイル
DEVICE_FILE = "devices.json"


# ============================================================
# Device information
# ============================================================

devices = {}
last_seen = {}
ip_addresses = {}

next_id = 1

lock = threading.Lock()


# ============================================================
# Load device table
# ============================================================

if os.path.exists(DEVICE_FILE):

    try:
        with open(DEVICE_FILE, "r") as f:
            devices = json.load(f)

        # JSONではIDが数字になっていることを保証
        devices = {
            str(mac): int(device_id)
            for mac, device_id in devices.items()
        }

        if devices:
            next_id = max(devices.values()) + 1

        print(f"Loaded {len(devices)} devices.")

    except Exception as e:
        print(f"Could not load {DEVICE_FILE}: {e}")


# ============================================================
# Save device table
# ============================================================

def save_devices():

    with open(DEVICE_FILE, "w") as f:
        json.dump(
            devices,
            f,
            indent=4
        )


# ============================================================
# Get / assign ID
# ============================================================

def get_device_id(mac):

    global next_id

    with lock:

        # 既に登録されている
        if mac in devices:
            return devices[mac]

        # 新しいデバイス
        device_id = next_id

        devices[mac] = device_id

        next_id += 1

        save_devices()

        print()
        print("================================")
        print(" New AtomS3 detected")
        print(f" MAC : {mac}")
        print(f" ID  : {device_id}")
        print("================================")

        return device_id


# ============================================================
# Receive loop
# ============================================================

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

                device_id = get_device_id(mac)

                with lock:
                    last_seen[mac] = time.time()
                    ip_addresses[mac] = addr[0]

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

                device_id = get_device_id(mac)

                with lock:
                    last_seen[mac] = time.time()
                    ip_addresses[mac] = addr[0]

                response = f"ACK,{device_id}"

                sock.sendto(
                    response.encode(),
                    addr
                )

        except Exception as e:

            print(f"Receive error: {e}")


# ============================================================
# Monitor display
# ============================================================

def monitor_loop():

    while True:

        os.system("clear")

        print()
        print("╔══════════════════════════════════════════════════════╗")
        print("║                 AtomS3 Monitor                       ║")
        print("╠══════╦═══════════════════════╦═══════════════════════╣")
        print("║ ID   ║ MAC                   ║ STATUS                ║")
        print("╠══════╬═══════════════════════╬═══════════════════════╣")

        with lock:

            sorted_devices = sorted(
                devices.items(),
                key=lambda x: x[1]
            )

            if not sorted_devices:

                print(
                    "║                    No devices                       ║"
                )

            else:

                now = time.time()

                for mac, device_id in sorted_devices:

                    elapsed = (
                        now - last_seen.get(mac, 999999)
                    )

                    if elapsed < TIMEOUT:

                        status = "● ONLINE "

                    else:

                        status = "○ OFFLINE"

                    print(
                        f"║ {device_id:<4} "
                        f"║ {mac:<21} "
                        f"║ {status:<21}║"
                    )

        print("╚══════╩═══════════════════════╩═══════════════════════╝")

        print()
        print("Ctrl+C : exit")

        time.sleep(1)


# ============================================================
# Main
# ============================================================

def main():

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
        ("0.0.0.0", PORT)
    )

    print(
        f"AtomS3 server started "
        f"(UDP port {PORT})"
    )

    # 受信スレッド
    thread = threading.Thread(
        target=receive_loop,
        args=(sock,),
        daemon=True
    )

    thread.start()

    # モニター
    monitor_loop()


if __name__ == "__main__":
    main()