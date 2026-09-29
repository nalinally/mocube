import os
import time
import state

# ============================================================
# Monitor display
# ============================================================

class Display():

    def __init__(self):
        self.funcs = {}
        
    def add_func(self, f, name):
        self.funcs[name] = [f, True]
        
    def enable(self, name):
        self.funcs[name][1] = True
        
    def disable(self, name):
        self.funcs[name][1] = False

    def update(self):
        os.system("clear")
        for f in self.funcs.keys():
            self.funcs[f][0]()
        time.sleep(1)

def display_connection_status_func():
    def f():
        print()
        print("╔══════════════════════════════════════════════════════╗")
        print("║                 AtomS3 Monitor                       ║")
        print("╠══════╦═══════════════════════╦═══════════════════════╣")
        print("║ ID   ║ MAC                   ║ STATUS                ║")
        print("╠══════╬═══════════════════════╬═══════════════════════╣")

        devices = state.state.get_device()

        # print(f"1:{type(devices)}")

        if not devices:

            print(
                "║                    No devices                        ║"
            )

        else:

            now = time.time()

            # print(f"0:{type(devices)}")

            for mac in devices.keys():

                if "online" in devices[mac].keys():
                    
                    if devices[mac]["online"]:

                        status = "● ONLINE "
                        
                    else:
                    
                        status = "○ OFFLINE"

                else:

                    status = "○ OFFLINE"

                print(
                    f"║ {devices[mac]["id"]:<4} "
                    f"║ {mac:<21} "
                    f"║ {status:<21} ║"
                )

        print("╚══════╩═══════════════════════╩═══════════════════════╝")

        print()
        print("Ctrl+C : exit")
    return f
