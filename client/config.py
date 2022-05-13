where = "laptop"
if where == "laptop":
    WIFI_SSID = "gercowifi"
    WIFI_PASSWORD = "password"
    SERVER = "192.168.137.1"
elif where == "pc":
    WIFI_SSID = "KPN1479E6"
    WIFI_PASSWORD = "FXR7JX6mfkR2Wbcf"
    SERVER= "192.168.2.2"
else: 
    WIFI_SSID = "gercowifi"
    WIFI_PASSWORD = "password"
    SERVER = "192.168.137.1"

PORT = "5000"
ENDPOINTSTATUS = "/api/update_status"
ENDPOINTCONNECT = "/api/search_connect"