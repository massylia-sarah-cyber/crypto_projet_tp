# 🛡️ CryptoExchange: Secure Hybrid File Transfer System

**CryptoExchange** is a high-security file transfer application built with Python. It implements a **Hybrid Cryptography** architecture, combining the high performance of symmetric encryption with the robust key distribution of asymmetric encryption.

## ✨ Core Security Features

* **Hybrid Encryption:** Utilizes **AES-256-GCM** for high-speed data encryption and **RSA-2048** for secure session key exchange (Key Wrapping).
* **Digital Signatures:** Implements **RSA-PSS** with **SHA-256** to guarantee **Non-repudiation** and **Authenticity**.
* **Custom Binary Protocol:** Features a structured packet-based communication layer with Magic Numbers (`CXCH`) and headers to ensure data alignment and protocol integrity.
* **PKI Architecture:** Includes a built-in **Certificate Authority (CA)** system to issue and verify X.509 certificates, preventing Man-in-the-Middle (MitM) attacks.
* **Integrity Assurance:** Uses cryptographic hashing (SHA-256) and GCM authentication tags to ensure that files have not been altered during transit.

---

## 🏗️ Technical Architecture

The system follows a strict multi-layered security workflow:

### 1. Identity Verification (Handshake)
Before any data is exchanged, the client and server perform a cryptographic handshake. They exchange certificates and verify them against the **Root CA**. This establishes a "Chain of Trust."



### 2. Secure Key Exchange (Key Wrapping)
Since RSA is computationally expensive for large files, the client generates a random **AES-256 session key**. This key is "wrapped" (encrypted) using the server's **RSA Public Key**, ensuring that only the intended server can decrypt the file.

### 3. Data Protection & Signing
The client signs the file hash with its **Private Key** and encrypts the payload using the AES key in **GCM mode**, which provides built-in message authentication.



---

## 📂 Project Structure

| Module | Responsibility |
| :--- | :--- |
| `pki.py` | Certificate Authority logic, RSA key generation, and PSS signing. |
| `aes_crypto.py` | Low-level AES-256-GCM encryption and decryption routines. |
| `protocol.py` | Binary framing, packet serialization, and checksum logic. |
| `server.py` | Multi-threaded socket server with session management and verification. |
| `client.py` | Secure client implementation for file processing and transmission. |
| `demo.py` | Orchestration script for automated end-to-end testing. |

---

## 🚀 Installation & Usage

### Prerequisites
* Python 3.8+
* `cryptography` library

### Setup
1.  **Clone the repository:**
    ```bash
    git clone [https://github.com/moonmido/CryptoExchange.git](https://github.com/moonmido/CryptoExchange.git)
    cd CryptoExchange
    ```
2.  **Install dependencies:**
    ```bash
    pip install cryptography
    ```

### Running the Demo
Execute the automated demo to see the full encryption and transfer lifecycle:
```bash
python demo.py
