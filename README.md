# netifaces (2)

## 1. What is this?

The original [netifaces](https://github.com/al45tair/netifaces) was abandonned by it's maintainer,
leaving us without the option to get network addresses of any kind in Python. Unfortunately, the
original sources are more akin to arcane magic, so picking where it's been left off is a difficult
task.

I decided to rewrite `netifaces`, keeping the **almost** exact same API and adding the following:

- Support for future python versions
- Type annotations
- Maybe a more "queriable" API in the future

This project aims to be a drop-in replacement for those project who use `netifaces`, but I do not
guarantee anything.


### 1.1 What is not working **right-now**

- The `gateways` API is only working if your system has a `/proc/net/route` file or the `ip` tool
- The `windows` gateways API is non-functional

## 2. Usage

For now the API is the same as the original `netifaces`, so please refer to [it](https://github.com/al45tair/netifaces).

Install:
```shell
pip install netifaces2
```

Import:
```python
>>> import netifaces
>>> netifaces.interfaces()  
    ...
>>> netifaces.ifaddresses('en0')
    ...
>>> netifacs.gateways()
    ...
```

## 3. API differences between this and al45tair/netifaces

### `gateways`

The `gateways` function does not support indexing through the `default` special key. This is because it makes a
sane typing definition difficult to write and be understandable. Instead, if you want the same functionality,
the following is exposed:

```python
>>> netifaces.default_gateway()
    ...
```

The result will be the default gateway for each interface type. The result may
be an empty dict if no default route is set.

The level of completness differs a little bit with the original version; some
address families might not yet be available and `PEER` addresses are not
reported for now. If you need a feature, open an issue and I will do my best to
add it.

Gateways also returned the interfaces indexed by integer values. This is a bit
odd (IMO) since the integers values for the interface types are
system-dependent. Enum values with a more semantic meaning are now used (they
        are still tied to linux numbers), but you can use `old_api=True` in
their call to get the al45air-style keys back.

### `AF_` Constants

In the previous version of `netifaces` the `AF_` constants' values were assigned
to be platform dependent. This has the nice effect of using the correct OS constant value when
accessing the information of a network layer. However after consideration, it
does not feel like the right place to provide abstraction.

In netifaces-2, the AF_ constants are fixed, and no longer share the same integer value
as their equivalents from the `socket` module.  This means that code which uses the
two sets of constants interchangeably may have to be updated.  If you update your
project's dependencies to this version of `netifaces`, be wary of this change.

So that type annotations can help with this, netifaces provides the `netifaces.InterfaceType`
enum for its own interface types.  All netifaces results are annotated using this type.
You should use values like `netifaces.InterfaceType.AF_INET6` instead of `netifaces.AF_INET6`
where possible so that a type checker can help catch issues with using the incorrect constants.

In the future, an extra API will allow accessing a specific layer's information
by querying for it, without using the platform's constant.

### Interface Up/Down Status and IPv4 Addresses

netifaces-2 adds a new function for detecting if an interface is up or down: `netifaces.interface_is_up()`.  You can pass it an interface name and it will return true iff that interface is able to pass traffic.

This can come in handy when dealing with a specific quirk of the original netifaces: due to what is arguably a bug, it does not report the IPv4 addresses of interfaces which have static IPs, but are down on Windows.  So, code might try to iterate over all the IPv4 interfaces, assume that any interfaces which do have addresses are up, and try to do stuff on them.  This author found at least one such example in his own code.

netifaces-2 prefers to provide IP address information as received from the OS without changes.  In practice, this means that on Linux/Mac, static IPv4 IPs will not be reported for interfaces that are down, while on Windows, they are.   IPv6 IPs are always reported regardless of the interface status.  This means that in your code, you should always check `interface_is_up()` before attempting to do anything with an interface.

For extra fun, on MacOS, the OS has a nasty habit of reporting that interfaces are up when they actually aren't.  It appears that it sets the IFF_RUNNING flag even when a cable is not plugged into an Ethernet interface, and there aren't any other flags we're aware of that can produce more correct information.  And this isn't a netifaces-specific issue either -- the OS's own ifconfig tool also reports these interfaces as RUNNING even when they are disconnected.  For maximum portability, the best way to detect if an interface is usable appears to be to ensure that interface_is_up() returns true AND that the interface has IP addresses assigned to it.

## 4. Platform support

### Wheels
Building Linux, Windows and macOS cp37-abi3 wheels (requires Python 3.7 and newer)  
Install using pip:  
`python -m pip install netifaces2`

#### Linux  
Linux cp37-abi3 wheels are built on manylinux2_17 aka manylinux2014 and require pip>=19.3  
cp36m-manylinux2_17 wheels are unsupported and are being built only as a fallback
for systems with only Python 3.6 available.

## 5. License

This software is distributed under a MIT license.

## 6. Developing Locally

To set up for local development, you will first need to install Rust from [rustup](https://rustup.rs/).

It's then recommended to create a virtual environment and install the package plus its dependencies into it:
```
$ python3 -m venv venv
$ source venv/bin/activate (or .\venv\Scripts\activate.ps1 with Windows Powershell)
$ python3 -m pip install -e '.[dev]' # This internally runs the Rust compiler
$ python3 -m pip install pre-commit
$ source venv/bin/activate # Re-source the venv to pick up new scripts
$ pre-commit install
```

To recompile the rust code after making changes, run:
```
$ python3 -m pip install -e .
```
again.
