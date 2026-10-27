"""Discover and choose a device, then list its APIs. Performs read operations only."""
from divoom_wifi import connect, discover_devices


def main() -> None:
    devices = [device for device in discover_devices() if device.supported]
    if not devices:
        raise SystemExit("No supported devices; use a direct IP and hardware ID instead.")
    for index, device in enumerate(devices, 1):
        print(index, device.name, device.product, device.hardware, device.device_id, device.ip, device.mac)
    choice = int(input("Device number: "))
    if not 1 <= choice <= len(devices):
        raise SystemExit("Invalid selection")
    with connect(devices[choice - 1]) as client:
        print(type(client).__name__)
        for spec in client.list_apis():
            print(spec.name, spec.title)


if __name__ == "__main__":
    main()
