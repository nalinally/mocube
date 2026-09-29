import sys
import time

sys.path.append("../")
import device_manager
import display
import state

def main():
    device_manager.init()
    disp = display.Display()
    disp.add_func(display.display_connection_status_func(), "connection")
    
    while True:
        disp.update()
        state.state.update()
        time.sleep(0.001)
    
if __name__=="__main__":
    main()