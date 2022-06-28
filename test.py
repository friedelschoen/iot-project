from remote import Remote

for port in Remote.list_ports():
    print(f'{port.name} at {port.device} ({port.description})')
