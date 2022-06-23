import socket

def get_ip_address(ip):
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    s.connect((ip, 80))
    return s.getsockname()[0]


def send_broadcast(data, port=37021):
    server = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)
    server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEPORT, 1)

    # Enable broadcasting mode
    server.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)

    # Set a timeout so the socket does not block
    # indefinitely when trying to receive data.
    server.settimeout(0.2)
    server.sendto(bytes(data, encoding="raw_unicode_escape"), ('<broadcast>', port))

def reponse_broadcast_request_ip(port=37020):
    client = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)  # UDP
    client.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEPORT, 1)

    # Enable broadcasting mode
    client.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
    client.bind(("", port))
    while True:
        data, addr = client.recvfrom(1024)
        print("received message: %s" % data)
        if "request-extensions-server-ip" in data.decode('utf8'):
            print("camera is requesting ip of rc")
            ipCamera = data.decode('utf8').split('|')[1]
            ipRc = get_ip_address(ipCamera)
            send_broadcast(ipRc)

if __name__ == '__main__':
    # Discovery function: Camera send request broadcast, Recorder Center response ip
    # Usage: In camera run two command in different terminal, one for send, one for listen
    # Listen: nc -luk 37021
    # Send: echo -n "request-rc-ip|192.168.0.132" | nc -u -b 255.255.255.255 37020
    reponse_broadcast_request_ip()
