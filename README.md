
# 🔍 FTP Forensic Proxy Toolkit

![Python](https://img.shields.io/badge/Python-3.x-blue?logo=python)
![License](https://img.shields.io/badge/License-MIT-green)

## Building a TCP Proxy

A TCP proxy is a crucial tool enabling:

* **Traffic Forwarding**: Redirecting traffic between hosts.
* **Software Evaluation**: Useful for analyzing network-based applications.
* **Wireshark Alternative**: Especially beneficial in enterprise environments with restrictions.

The TCP proxy requires four key functions:

1. **hexdump**: Displays machine communication in the console.
2. **receive\_from**: Receives incoming socket data.
3. **proxy\_handler**: Manages traffic flow between machines.
4. **server\_loop**: Configures and handles the listening connector.

A forensic traffic analysis tool for FTP that intercepts and visualizes:

* Plain-text credentials
* Directory structure
* Transfer metadata

## 🎯 Key Features

* 🕵️‍♂️ Real-time hexdump of communications
* 📊 Active/passive mode analysis
* 🔐 Demonstrates vulnerabilities in unencrypted protocols
* 📦 Reconstruction of remote file structures

## 🚀 Quick Installation

```bash
git clone https://github.com/diegomty/python-proxy-sniffer
cd ftp-forensic-proxy
pip install -r requirements.txt
```

## 💻 Basic Usage - Detailed Mode

🛠 Command Syntax:

```bash
python proxy.py [LOCAL_IP] [LOCAL_PORT] [REMOTE_SERVER] [REMOTE_PORT] [RECEIVE_FIRST]
```

🌍 Example with Public Server:

```bash
python proxy.py 127.0.0.1 2121 ftp.debian.org 21 True
```

🔓 Anonymous Authentication:
When prompted by the FTP client for credentials:

```bash
Name (127.0.0.1:your_username): anonymous
Password: [any_text]
```

(Public FTP servers accept any password for anonymous users)

## 🌐 Public FTP Servers for Testing

| Server            | Port | Notes                   |
| ----------------- | ---- | ----------------------- |
| ftp.debian.org    | 21   | Debian package contents |
| ftp.gnu.org       | 21   | GNU software            |
| mirror.centos.org | 21   | CentOS repositories     |

---

