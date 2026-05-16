import socket
import json
from pathlib import Path
from datetime import datetime

from pki import (
    load_private_key, load_certificate, bootstrap_pki,
    verify_certificate, rsa_encrypt, sign_data,
    CERTS_DIR,
)
from aes_crypto import generate_aes_key, aes_encrypt
from protocol import (
    recv_packet, send_packet,
    MSG_HELLO, MSG_CERT, MSG_KEY_WRAP, MSG_FILE_META,
    MSG_FILE_CHUNK, MSG_ACK, MSG_ERROR, MSG_BYE,
    file_checksum, build_file_meta,
)

HOST = "127.0.0.1"
PORT = 9999


def log(tag: str, msg: str):
    ts = datetime.now().strftime("%H:%M:%S")
    print(f"[{ts}] \033[33m[CLIENT/{tag}]\033[0m {msg}")


class SecureClient:
    def __init__(self):
        pki = bootstrap_pki()
        self.client_key, self.client_cert = pki["client"]
        _, self.ca_cert = pki["ca"]
        self.server_cert = None
        self.sock = None

    def connect(self):
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock.connect((HOST, PORT))
        log("CONN", f"Connected to {HOST}:{PORT}")
        self._handshake()

    def _handshake(self):
        send_packet(self.sock, MSG_HELLO, b"hello")
        log("HS", "Sent HELLO")

        msg_type, server_cert_bytes = recv_packet(self.sock)
        assert msg_type == MSG_CERT, "expected server CERT"

        from cryptography import x509
        self.server_cert = x509.load_pem_x509_certificate(server_cert_bytes)
        if not verify_certificate(self.server_cert, self.ca_cert):
            raise ValueError("server certificate verification failed")
        cn = self.server_cert.subject.get_attributes_for_oid(__import__("cryptography").x509.oid.NameOID.COMMON_NAME)[0].value
        log("HS", f"Server cert verified: CN={cn}")

        from cryptography.hazmat.primitives import serialization
        client_cert_bytes = self.client_cert.public_bytes(serialization.Encoding.PEM)
        send_packet(self.sock, MSG_CERT, client_cert_bytes)
        log("HS", "Sent client certificate")

        msg_type, ack = recv_packet(self.sock)
        assert msg_type == MSG_ACK and ack == b"cert_ok", "handshake rejected"
        log("HS", "Handshake complete — secure channel established")

    def send_file(self, file_path: str):
        path = Path(file_path)
        if not path.exists():
            raise FileNotFoundError(f"File not found: {file_path}")

        plaintext = path.read_bytes()
        log("FILE", f"Preparing to send: {path.name} ({len(plaintext)} bytes)")

        aes_key = generate_aes_key()
        log("CRYPTO", "Generated AES-256 session key")

        nonce, ciphertext = aes_encrypt(plaintext, aes_key)
        log("CRYPTO", f"File encrypted with AES-256-GCM (nonce: {nonce.hex()[:12]}…)")

        signature = sign_data(plaintext, self.client_key)
        log("SIGN", f"Digital signature created ({len(signature)} bytes)")

        enc_key = rsa_encrypt(aes_key, self.server_cert.public_key())
        log("CRYPTO", "AES key wrapped with server RSA public key")

        checksum = file_checksum(plaintext)
        log("HASH", f"SHA-256: {checksum[:16]}…")

        meta_bytes = build_file_meta(path.name, len(plaintext), checksum, enc_key, nonce, signature)
        send_packet(self.sock, MSG_FILE_META, meta_bytes)
        send_packet(self.sock, MSG_FILE_CHUNK, ciphertext)
        log("SEND", f"Encrypted payload sent ({len(ciphertext)} bytes)")

        msg_type, ack_payload = recv_packet(self.sock)
        if msg_type == MSG_ACK:
            result = json.loads(ack_payload)
            log("ACK", f"Server confirmed: {result}")
        elif msg_type == MSG_ERROR:
            raise RuntimeError(f"Server error: {ack_payload.decode()}")

    def disconnect(self):
        if self.sock:
            send_packet(self.sock, MSG_BYE, b"bye")
            self.sock.close()
            log("CONN", "Disconnected")


def send_files(file_paths: list[str]):
    client = SecureClient()
    client.connect()
    for fp in file_paths:
        client.send_file(fp)
    client.disconnect()
