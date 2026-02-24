import subprocess
import ipaddress

def ping(ip):
    result = subprocess.run(
        ["ping", "-c", "1", "-W", "1", str(ip)],
        stdout=subprocess.DEVNULL
    )
    return result.returncode == 0


def scan(network):
    net = ipaddress.ip_network(network, strict=False)
    alive = []
    for ip in net.hosts():
        print(str(ip))
    for ip in net.hosts():
        if ping(ip):
            alive.append(str(ip))

    return alive


if __name__ == "__main__":
    devices = scan("10.42.0.1/24")

    for ip in devices:
        print(ip)