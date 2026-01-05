"""Constants for the Nornir MCP server."""

# Supported NAPALM getters with descriptions
# These are the data getters that can be used with the get_device_data function
ALLOWED_GETTERS = {
    "facts": "Basic device information",
    "interfaces": "Interface state and speed",
    "interfaces_ip": "IP addressing per interface",
    "bgp_neighbors": "BGP neighbor summary",
    "lldp_neighbors": "LLDP neighbor discovery",
    "arp_table": "ARP entries",
    "mac_address_table": "MAC address table",
    "environment": "Power, fans, temperature",
}
