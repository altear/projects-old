# Alarm System

A decentralized alarm system using webcams and computer vision

## Table of Contents

[TOC]

## Hardware

Raspberry Pi 3

## Development Environment

### Fresh Reinstall on Windows 

Windows may struggle to put a fresh os over an ssd card that was already partitioned for a RasPi OS. To deal with this you can use the windows tool `diskpart` from cmd line

Example, clear existing parts and add new primary part:`

```
$ diskpart
> list disks
> select disk 2
> list parts
> select part 1
> del part
> select part 2
> del part
> create part pri
> exit
```

### Headless Raspi Setup

SSH is disabled be default on a blank Jessie OS. To enable, add a file called "ssh" to the boot directory (this can be done from windows too). The file name must be lower case, with either no file extension or a `.txt` extension

### Host Discovery

Discovering raspis can be done with [NMap or Zenmap](https://nmap.org/download.html). 

NMap command example:

```
nmap 192.168.0.1-50
```

### Basic Security Notes



Reference: https://www.raspberrypi.org/documentation/configuration/security.md

### Efficient Configuration

As the target of this project is a decentralized network, manual configuration of each node would be a pain. To handle this, a script should handle configuration of new hosts.

## Notes

### File Versioning

```
policy_v01_08
```

Source: https://records.princeton.edu/blogs/records-management-manual/file-naming-conventions-version-control