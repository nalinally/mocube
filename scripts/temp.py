import json
import os

devices = {"30.30.30.30": {"id": 0, "addr": "192.168.1.2", "last_seen": 17171717, "online": True},
           "40.40.40.40": {"id": 1, "addr": "192.168.1.3", "last_seen": 17171729, "online": False}}

# with open("temp.json", "w") as f:
#     json.dump(
#         devices,
#         f,
#         indent=4
#     )

if os.path.exists("temp.json"):

    try:
        with open("temp.json", "r") as f:
            devices = json.load(f)

        # JSONではIDが数字になっていることを保証
        for mac, data in devices.items():
            print(mac)
            print(data["id"])
            print(data["addr"])
            print(data["last_seen"])
            print(data["online"])
            # devices = {
            #     str(mac): int(device_id)
            #     for mac, device_id in devices.items()
            # }
    
    except Exception as e:
        print(f"Could not load : {e}")
    
