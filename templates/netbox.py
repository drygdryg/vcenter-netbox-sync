#!/usr/bin/env python3
"""A collection of NetBox object templates"""
from typing import Optional, Tuple, Union, List


def remove_empty_fields(obj: dict) -> dict:
    """
    Removes empty fields from NetBox objects.

    This ensures NetBox objects do not return invalid None values in fields.
    :param obj: A NetBox formatted object
    """
    return {k: v for k, v in obj.items() if v is not None}


def format_slug(text: str) -> str:
    """
    Format string to comply to NetBox slug acceptable pattern and max length.

    :param text: Text to be formatted into an acceptable slug
    :return: Slug of allowed characters [-a-zA-Z0-9_] with max length of 50
    """
    allowed_chars = (
        "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ"  # Alphabet
        "0123456789"  # Numbers
        "_-"  # Symbols
        )
    # Replace separators with dash
    separators = [" ", ",", "."]
    for sep in separators:
        text = text.replace(sep, "-")
    # Strip unacceptable characters
    text = "".join([c for c in text if c in allowed_chars])
    # Enforce max length
    return truncate(text, max_len=50).lower()


def parse_version_tuple(v: Union[str, float]) -> Tuple[int]:
    """
    Parses version number to compare versions

    :param v: Version number; example: '2.10.3'
    """
    return tuple(map(int, (str(v).split("."))))


def truncate(text: str = "", max_len: int = 50):
    """Ensure a string complies to the maximum length specified."""
    return text if len(text) < max_len else text[:max_len]


class Templates:
    """NetBox object templates"""
    def __init__(self, api_version: float):
        """
        Required parameters for the NetBox class

        :param api_version: NetBox API version objects must be formatted to
        """
        self.api_version = api_version

    def cluster(self, name: str, cluster_type: str, group: Optional[str] = None, tags: Optional[List[dict]] = None):
        """
        Template for NetBox clusters at /virtualization/clusters/

        :param name: Name of the cluster group
        :param cluster_type: Name of NetBox cluster type object
        :param group: Name of NetBox cluster group object
        :param tags: Tags to apply to the object
        """
        obj = {
            "name": truncate(name, max_len=100),
            "type": {"name": cluster_type},
            "group": {"name": truncate(group, max_len=50)} if group else None,
            "tags": tags,
            }
        return remove_empty_fields(obj)

    def cluster_group(self, name, slug=None) -> dict:
        """
        Template for NetBox cluster groups at /virtualization/cluster-groups/

        :param name: Name of the cluster group
        :type name: str
        :param slug: Unique slug for cluster group.
        :type slug: str, optional
        """
        obj = {
            "name": truncate(name, max_len=50),
            "slug": slug if slug else format_slug(name)
            }
        return remove_empty_fields(obj)

    def device(self, name: str, device_role: str, device_type: str, display_name: Optional[str] = None,
               platform: Optional[str] = None, site: Optional[str] = None, serial: Optional[str] = None,
               asset_tag: Optional[str] = None, cluster: Optional[str] = None, status: int = None,
               tags: Optional[List[dict]] = None) -> dict:
        """
        Template for NetBox devices at /dcim/devices/

        :param name: Hostname of the device
        :param device_role: Name of device role
        :param device_type: Model name of device type
        :param display_name: Friendly name for device
        :param platform: Platform running on the device
        :param site: Site where the device resides
        :param serial: Serial number of the device
        :param asset_tag: Asset tag of the device
        :param cluster: Cluster the device belongs to
        :param status: NetBox IP address status in NB API v2.6 format
        :param tags: Tags to apply to the object
        """
        obj = {
            "name": name,
            "device_role": {"name": device_role},
            "device_type": {"model": device_type},
            "display_name": display_name,
            "platform": {"name": platform} if platform else None,
            "site": {"name": site} if site else None,
            "serial": truncate(serial, max_len=50) if serial else None,
            "asset_tag": truncate(asset_tag, max_len=50) if asset_tag else None,
            "cluster": {
                "name": truncate(cluster, max_len=100)
                } if cluster else None,
            "status": self._version_dependent(
                nb_obj_type="devices",
                key="status",
                value=status
                ),
            "tags": tags,
            }
        return remove_empty_fields(obj)

    def device_interface(self, device: str, name: str, iftype: Optional[int] = None, enabled: Optional[bool] = None,
                         mtu: Optional[int] = None, mac_address: Optional[str] = None, mgmt_only: Optional[bool] = None,
                         description: Optional[str] = None, cable: Optional[int] = None, mode: Optional[int] = None,
                         untagged_vlan: Optional[int] = None, tagged_vlans: Optional[str] = None,
                         tags: Optional[List[dict]] = None) -> dict:
        """
        Template for NetBox device interfaces at /dcim/interfaces/

        :param device: Name of parent device the interface belongs to
        :param name: Name of the physical interface
        :param iftype: Type of interface `0` if Virtual else `32767` for Other
        :param enabled: `True` if the interface is up else `False`
        :param mtu: The configured MTU for the interface
        :param mac_address: The MAC address of the interface
        :param mgmt_only: `True` if interface is only for out of band else `False`
        :param description: Description for the interface
        :param cable: NetBox cable object ID of the interface is attached to
        :param mode: `100` if access, `200` if tagged, or `300 if` tagged for all vlans
        :param untagged_vlan: NetBox VLAN object id of untagged vlan
        :param tagged_vlans: List of NetBox VLAN object ids for tagged VLANs
        :param tags: Tags to apply to the object
        """
        obj = {
            "device": {"name": device},
            "name": name,
            "type": self._version_dependent(
                nb_obj_type="interfaces",
                key="type",
                value=iftype
                ) if (iftype is not None) else None,
            "enabled": enabled,
            "mtu": mtu,
            "mac_address": mac_address.upper() if mac_address else None,
            "mgmt_only": mgmt_only,
            "description": description,
            "cable": cable,
            "mode": mode,
            "untagged_vlan": untagged_vlan,
            "tagged_vlans": tagged_vlans,
            "tags": tags,
            }
        return remove_empty_fields(obj)

    def device_type(self, manufacturer: str, model: str, slug: Optional[str] = None, part_number: Optional[str] = None,
                    tags: Optional[List[dict]] = None) -> dict:
        """
        Template for NetBox device types at /dcim/device-types/

        :param manufacturer: Name of NetBox manufacturer object
        :param model: Name of NetBox model object
        :param slug: Unique slug for manufacturer.
        :param part_number: Unique partner number for the device
        :param tags: Tags to apply to the object
        """
        obj = {
            "manufacturer": {"name": manufacturer},
            "model": truncate(model, max_len=50),
            "slug": slug if slug else format_slug(model),
            "part_number": truncate(
                part_number, max_len=50
                ) if part_number else None,
            "tags": tags
            }
        return remove_empty_fields(obj)

    def ip_address(self, address: str, description: Optional[str] = None, device: Optional[str] = None,
                   dns_name: Optional[str] = None, interface: Optional[str] = None, status: int = 1,
                   tags: Optional[List[dict]] = None, tenant: Optional[str] = None, virtual_machine: Optional[str] = None,
                   vrf: Optional[str] = None) -> dict:
        """
        Template for NetBox IP addresses at /ipam/ip-addresses/

        :param address: IP address
        :param description: A description of the IP address purpose
        :param device: The device which the IP and its interface are attached to
        :param dns_name: FQDN pointed to the IP address
        :param interface: Name of the parent interface IP is configured on
        :param status: `1` if active, `0` if deprecated
        :param tags: Tags to apply to the object
        :param tenant: The tenant the IP address belongs to
        :param virtual_machine: Name of the NetBox VM object the IP is configured on
        :param vrf: Virtual Routing and Forwarding instance for the IP
        """
        # Validate user did not try to provide a parent device and VM
        if bool(device and virtual_machine):
            raise ValueError(
                "Values provided for both parent device and virtual machine "
                "but they are exclusive to each other."
                )
        obj = {
            "address": address,
            "description": description,
            "dns_name": dns_name,
            "status": self._version_dependent(
                nb_obj_type="ip_addresses",
                key="status",
                value=status
                ),
            "tags": tags,
            "tenant": tenant,
            "vrf": vrf
            }
        if interface and bool(device or virtual_machine):
            obj["assigned_object"] = {"name": interface}
            if device:
                obj["assigned_object_type"] = "dcim.interface"
                obj["assigned_object"].update({"device": {"name": device}})
            elif virtual_machine:
                obj["assigned_object_type"] = "virtualization.vminterface"
                obj["assigned_object"].update({"virtual_machine": {"name": truncate(virtual_machine, max_len=64)}})
        return remove_empty_fields(obj)

    def manufacturer(self, name: str, slug: Optional[str] = None):
        """
        Template for NetBox manufacturers at /dcim/manufacturers

        :param name: Name of the manufacturer
        :param slug: Unique slug for manufacturer.
        """
        obj = {
            "name": truncate(name, max_len=50),
            "slug": slug if slug else format_slug(name)
            }
        return remove_empty_fields(obj)

    def _version_dependent(self, nb_obj_type: str, key: str, value) -> str:
        """
        Formats object values depending on the NetBox API version.

        Prior to NetBox API v2.7 NetBox used integers for multiple choice
        fields. We use the version of NetBox API to determine whether we need
        to return integers or named strings.

        :param nb_obj_type: NetBox object type, must match keys in self.obj_map
        :param key: The dictionary key to check against
        :param value: Value to the provided key in NetBox 2.6 or less format
        :return: NetBox API version safe value
        """
        obj_map = {
            "circuits": {
                "status": {
                    0: "deprovisioning",
                    1: "active",
                    2: "planned",
                    3: "provisioning",
                    4: "offline",
                    5: "decomissioned"
                }},
            "devices": {
                "status": {
                    0: "offline",
                    1: "active",
                    2: "planned",
                    3: "staged",
                    4: "failed",
                    5: "inventory",
                    6: "decomissioning"
                }},
            "interfaces": {
                "type": {
                    0: "virtual",
                    32767: "other"
                },
                "mode": {
                    100: "access",
                    200: "tagged",
                    300: "tagged-all",
                }},
            "ip_addresses": {
                "role": {
                    10: "loopback",
                    20: "secondary",
                    30: "anycast",
                    40: "vip",
                    41: "vrrp",
                    42: "hsrp",
                    43: "glbp",
                    44: "carp"
                    },
                "status": {
                    1: "active",
                    2: "reserved",
                    3: "deprecated",
                    5: "dhcp"
                    },
                "type": {
                    0: "virtual",
                    32767: "other"
                }},
            "prefixes": {
                "status": {
                    0: "container",
                    1: "active",
                    2: "reserved",
                    3: "deprecated"
                }},
            "sites": {
                "status": {
                    1: "active",
                    2: "planned",
                    4: "retired"
                }},
            "vlans": {
                "status": {
                    1: "active",
                    2: "reserved",
                    3: "deprecated"
                }},
            "virtual_machines": {
                "status": {
                    0: "offline",
                    1: "active",
                    3: "staged"
                    }
            }}
        # isinstance is used as a safety check. If a string is passed we'll
        # assume someone passed a value for API v2.7 and return the result.
        if isinstance(value, int) and parse_version_tuple(self.api_version) > parse_version_tuple(2.6):
            result = obj_map[nb_obj_type][key][value]
        else:
            result = value
        return result

    def virtual_machine(self, name: str, cluster: str, status: Optional[int] = None, role: Optional[str] = None,
                        tenant: Optional[str] = None, platform: Optional[str] = None, primary_ip4: Optional[int] = None,
                        primary_ip6: Optional[int] = None, vcpus: Optional[int] = None, memory: Optional[int] = None,
                        disk: Optional[int] = None, comments: Optional[str] = None,
                        local_context_data: Optional[dict] = None, tags: Optional[List[dict]] = None) -> dict:
        """
        Template for NetBox virtual machines at /virtualization/virtual-machines/

        :param name: Name of the virtual machine
        :param cluster: Name of the cluster the virtual machine resides on
        :param status: `0` if offline, `1` if active, `3` if staged
        :param role: Name of NetBox role object
        :param tenant: Name of NetBox tenant object
        :param platform: Name of NetBox platform object
        :param primary_ip4: NetBox IP address object ID
        :param primary_ip6: NetBox IP address object ID
        :param vcpus: Quantity of virtual CPUs assigned to VM
        :param memory: Quantity of RAM assigned to VM in MB
        :param disk: Quantity of disk space assigned to VM in GB
        :param comments: Comments regarding the VM
        :param local_context_data: Additional context data regarding the VM
        :param tags: Tags to apply to the object
        """
        obj = {
            "name": name,
            "cluster": {"name": cluster},
            "status": self._version_dependent(
                nb_obj_type="virtual_machines",
                key="status",
                value=status
                ),
            "role": {"name": role} if role else None,
            "tenant": {"name": tenant} if tenant else None,
            "platform": platform,
            "primary_ip4": primary_ip4,
            "primary_ip6": primary_ip6,
            "vcpus": float(vcpus),
            "memory": memory,
            "disk": disk,
            "comments": comments,
            "local_context_data": local_context_data,
            "tags": tags
            }
        return remove_empty_fields(obj)

    def vm_interface(self, virtual_machine: str, name: str, iftype: Optional[int] = 0, enabled: Optional[bool] = None,
                     mtu: Optional[int] = None, mac_address: Optional[str] = None, description: Optional[str] = None,
                     mode: Optional[int] = None, untagged_vlan: Optional[int] = None, tagged_vlans: Optional[str] = None,
                     tags: Optional[List[dict]] = None) -> dict:
        """
        Template for NetBox virtual machine interfaces at /virtualization/interfaces/

        :param virtual_machine: Name of parent virtual machine the interface belongs to
        :param name: Name of the physical interface
        :param iftype: Type of interface `0` if Virtual else `32767` for Other
        :param enabled: `True` if the interface is up else `False`
        :param mtu: The configured MTU for the interface
        :param mac_address: The MAC address of the interface
        :param description: Description for the interface
        :param mode: `100` if access, `200` if tagged, or `300 if` tagged for all vlans
        :param untagged_vlan: NetBox VLAN object id of untagged vlan
        :param tagged_vlans: List of NetBox VLAN object ids for tagged VLANs
        :param tags: Tags to apply to the object
        """
        obj = {
            "virtual_machine": {"name": truncate(virtual_machine, max_len=64)},
            "name": name,
            "enabled": enabled,
            "mtu": mtu,
            "mac_address": mac_address.upper() if mac_address else None,
            "description": description,
            "mode": mode,
            "untagged_vlan": untagged_vlan,
            "tagged_vlans": tagged_vlans,
            "tags": tags,
            }
        return remove_empty_fields(obj)
