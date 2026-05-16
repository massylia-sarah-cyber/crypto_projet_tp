import socket
import threading
import struct
import json
from pathlib import Path
from datetime import datetime

from pki import (
    load_private_key, load_certificate, bootstrap_pki,
    verify_certificate, verify_signature, rsa_encrypt, rsa_decrypt,
    CERTS_DIR,
)
from aes_crypto import aes_decrypt
from protocol import (
    recv_packet, send_packet,
    MSG_HELLO, MSG_CERT, MSG_KEY_WRAP, MSG_FILE_META,
    MSG_FILE_CHUNK, MSG_ACK, MSG_ERROR, MSG_BYE,
    file_checksum, parse_file_meta,
)

HOST = "127.0.0.1"
PORT = 9999
SAVE_DIR = Path(__file__).parent / "server_files"
SAVE_DIR.mkdir(exist_ok=True)


def log(tag: str, msg: str):
    ts = datetime.now().strftime("%H:%M:%S")
    print(f"[{ts}] \033[36m[SERVER/{tag}]\033[0m {msg}")


def handle_client(conn: socket.socket, addr):
    log("CONN", f"New connection from {addr}")
    try:
        _run_session(conn)
    except Exception as exc:
        log("ERR", str(exc))
        send_packet(conn, MSG_ERROR, str(exc).encode())
    finally:
        conn.close()
        log("CONN", f"Connection closed {addr}")


def _run_session(conn: socket.socket):
    pki = bootstrap_pki()
    server_key, server_cert = pki["server"]
    _, ca_cert = pki["ca"]

    msg_type, _ = recv_packet(conn)
    assert msg_type == MSG_HELLO, "expected HELLO"
    log("HS", "Received HELLO")

    server_cert_bytes = server_cert.public_bytes(__import__("cryptography").hazmat.primitives.serialization.Encoding.PEM)
    send_packet(conn, MSG_CERT, server_cert_bytes)
    log("HS", "Sent server certificate")

    msg_type, client_cert_bytes = recv_packet(conn)
    assert msg_type == MSG_CERT, "expected client CERT"

    from cryptography import x509
    client_cert = x509.load_pem_x509_certificate(client_cert_bytes)
    if not verify_certificate(client_cert, ca_cert):
        raise ValueError("client certificate verification failed")
    log("HS", f"Client cert verified: CN={client_cert.subject.get_attributes_for_oid(__import__('cryptography').x509.oid.NameOID.COMMON_NAME)[0].value}")

    send_packet(conn, MSG_ACK, b"cert_ok")
    log("HS", "Handshake complete")

    while True:
        msg_type, payload = recv_packet(conn)

        if msg_type == MSG_BYE:
            log("SESSION", "Client disconnected gracefully")
            break

        if msg_type == MSG_FILE_META:
            meta = parse_file_meta(payload)
            filename = Path(meta["filename"]).name
            log("FILE", f"Incoming: {filename} ({meta['size']} bytes)")

            enc_key = rsa_decrypt(meta["enc_key"], server_key)
            log("CRYPTO", "AES session key unwrapped with RSA private key")

            msg_type2, encrypted_payload = recv_packet(conn)
            assert msg_type2 == MSG_FILE_CHUNK, "expected FILE_CHUNK"

            plaintext = aes_decrypt(meta["nonce"], encrypted_payload, enc_key)
            log("CRYPTO", f"File decrypted with AES-256-GCM ({len(plaintext)} bytes)")

            if not verify_signature(plaintext, meta["signature"], client_cert.public_key()):
                raise ValueError("file signature verification failed")
            log("VERIFY", "Digital signature verified")

            actual_checksum = file_checksum(plaintext)
            if actual_checksum != meta["checksum"]:
                raise ValueError("integrity check failed (SHA-256 mismatch)")
            log("VERIFY", f"Integrity OK — SHA-256: {actual_checksum[:16]}…")

            out_path = SAVE_DIR / filename
            out_path.write_bytes(plaintext)
            log("SAVE", f"Saved to {out_path}")

            send_packet(conn, MSG_ACK, json.dumps({"status": "ok", "file": filename}).encode())


def run_server():
    pki = bootstrap_pki()
    log("PKI", "Certificates ready")

    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as srv:
        srv.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        srv.bind((HOST, PORT))
        srv.listen(5)
        log("LISTEN", f"Listening on {HOST}:{PORT}")

        while True:
            conn, addr = srv.accept()
            t = threading.Thread(target=handle_client, args=(conn, addr), daemon=True)
            t.start()


if __name__ == "__main__":
    run_server()
