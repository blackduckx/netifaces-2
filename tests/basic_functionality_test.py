import platform
import re
from typing import Optional

import netifaces
import pytest


def test_interfaces_returns_something() -> None:
    assert len(netifaces.interfaces())


def test_interfaces_by_index_returns_same_interface_list() -> None:
    # Interface indices are difficult to verify, but we can at least check that we get
    # the same set of interfaces in both these functions
    assert set(netifaces.interfaces_by_index().values()) == set(netifaces.interfaces())


def test_can_lookup_by_either_name() -> None:
    # Test that it's possible to look up the ifaddresses of an interface
    # by either its machine readable or its human readable name

    # Choose an arbitrary interface by its index.
    # Use indices because the network interface list might not always be sorted the same between
    # multiple calls.
    ifaces_human_readable = netifaces.interfaces_by_index(netifaces.InterfaceDisplay.HumanReadable)
    arbitrary_iface_idx = next(iter(ifaces_human_readable.keys()))

    iface_human_readable = ifaces_human_readable[arbitrary_iface_idx]
    iface_machine_readable = netifaces.interfaces_by_index(netifaces.InterfaceDisplay.MachineReadable)[
        arbitrary_iface_idx
    ]

    assert netifaces.ifaddresses(iface_human_readable) == netifaces.ifaddresses(iface_machine_readable)


def test_has_ipv4_or_ipv6() -> None:
    has_any_ip = False

    for interface in netifaces.interfaces():
        address_table = netifaces.ifaddresses(interface)

        has_any_ip |= netifaces.AF_INET in address_table
        has_any_ip |= netifaces.AF_INET6 in address_table

        if has_any_ip:
            break

    assert has_any_ip, "Test failure; no AF_INET address of any kind found"


def test_has_link_layer() -> None:
    has_any_link = False

    for interface in netifaces.interfaces():
        address_table = netifaces.ifaddresses(interface)

        has_any_link |= netifaces.AF_PACKET in address_table
        has_any_link |= netifaces.AF_LINK in address_table

        if has_any_link:
            break

    assert has_any_link, "Test failure; no AF_PACKET address of any kind found"


@pytest.mark.skipif(platform.system() != "Windows", reason="Windows only")  # type: ignore[misc]
def test_interface_display_formats_windows() -> None:
    """
    Check that the InterfaceDisplay argument can be used to select between a UUID
    and a human readable name
    """

    uuid_regex = r"{[-A-F0-9]+}"

    # The machine readable interface should look like a UUID string
    machine_readable_iface0 = netifaces.interfaces(netifaces.InterfaceDisplay.MachineReadable)[0]
    print(f"Machine readable name of interface 0 is: {machine_readable_iface0}")
    assert re.fullmatch(uuid_regex, machine_readable_iface0) is not None

    # The human readable interface should NOT look like a UUID
    human_readable_iface0 = netifaces.interfaces(netifaces.InterfaceDisplay.HumanReadable)[0]
    print(f"Human readable name of interface 0 is: {human_readable_iface0}")
    assert re.fullmatch(uuid_regex, human_readable_iface0) is None


def test_loopback_addr_is_returned() -> None:
    """
    Test that the loopback address is returned in the lists of addresses
    (regression test for a bug)
    """

    loopback_ipv4_found = False
    loopback_ipv6_found = False

    for interface in netifaces.interfaces():
        address_table = netifaces.ifaddresses(interface)

        if netifaces.AF_INET in address_table:
            for ipv4_settings in address_table[netifaces.InterfaceType.AF_INET]:
                print(f"Loopback test: Considering iface {interface} IPv4 address " f"{ipv4_settings['addr']}")
                if ipv4_settings["addr"] == "127.0.0.1":
                    print("Loopback IPv4 found!")
                    loopback_ipv4_found = True

        if netifaces.AF_INET6 in address_table:
            for ipv6_settings in address_table[netifaces.InterfaceType.AF_INET6]:
                print(f"Loopback test: Considering iface {interface} IPv6 address " f"{ipv6_settings['addr']}")
                if ipv6_settings["addr"] == "::1":
                    print("Loopback IPv6 found!")
                    loopback_ipv6_found = True

    assert loopback_ipv4_found
    assert loopback_ipv6_found


def test_all_ifaces_have_ipv4() -> None:
    """
    Test that all interfaces which return IPv4 addresses have a "real" IPv4 address
    and not 0.0.0.0.
    (regression test for a bug)
    """

    for interface in netifaces.interfaces():
        address_table = netifaces.ifaddresses(interface)
        if netifaces.AF_INET in address_table:
            for ipv4_settings in address_table[netifaces.InterfaceType.AF_INET]:
                assert ipv4_settings["addr"] != "0.0.0.0"


def test_loopback_is_up() -> None:
    """
    Basic test of interface_is_up().  We can't make assumptions about most interfaces
    on the machine being up or down, but we can at least make sure that loopback is up.
    """

    loopback_if_name: Optional[str] = None

    # Find name of the loopback interface
    for interface in netifaces.interfaces():
        address_table = netifaces.ifaddresses(interface)
        if netifaces.AF_INET in address_table:
            for ipv4_settings in address_table[netifaces.InterfaceType.AF_INET]:
                if ipv4_settings["addr"] == "127.0.0.1":
                    loopback_if_name = interface
    assert loopback_if_name is not None

    assert netifaces.interface_is_up(loopback_if_name)


def test_ifaddresses_invalid_if_name() -> None:
    """
    Test that an invalid interface name passed to ifaddresses() is handled
    gracefully.
    """

    with pytest.raises(Exception) as exception_info:
        netifaces.ifaddresses("arglebargle")

    print("Got the following exception: " + str(exception_info))


def test_is_up_invalid_if_name() -> None:
    """
    Test that an invalid interface name passed to interface_is_up() is handled
    gracefully.
    """

    with pytest.raises(Exception) as exception_info:
        netifaces.interface_is_up("arglebargle")

    print("Got the following exception: " + str(exception_info))
