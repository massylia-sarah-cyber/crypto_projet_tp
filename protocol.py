import struct
import json
import hashlib


MAGIC = b"CXCH"
VERSION = 1

MSG_HELLO       = 0x01
MSG_CERT        = 0x02
MSG_KEY_WRAP    = 0x03
MSG_FILE_META   = 0x04
MSG_FILE_CHUNK  = 0x05
MSG_ACK         = 0x06
MSG_ERROR       = 0x07
MSG_BYE         = 0x08


def encode_packet(msg_type: int, payload: bytes) -> bytes:
    header = struct.pack(">4sBBI", MAGIC, VERSION, msg_type, len(payload))
    return header + payload


def decode_packet(data: bytes) -> tuple[int, bytes]:
    hdr_size = 4 + 1 + 1 + 4
    magic, version, msg_type, length = struct.unpack(">4sBBI", data[:hdr_size])
    assert magic == MAGIC, "bad magic"
    assert version == VERSION, "bad version"
    return msg_type, data[hdr_size:hdr_size + length]


def recv_packet(sock) -> tuple[int, bytes]:
    hdr_size = 4 + 1 + 1 + 4
    raw = _recv_exactly(sock, hdr_size)
    magic, version, msg_type, length = struct.unpack(">4sBBI", raw)
    payload = _recv_exactly(sock, length) if length else b""
    return msg_type, payload


def send_packet(sock, msg_type: int, payload: bytes = b""):
    sock.sendall(encode_packet(msg_type, payload))


def _recv_exactly(sock, n: int) -> bytes:
    buf = b""
    while len(buf) < n:
        chunk = sock.recv(n - len(buf))
        if not chunk:
            raise ConnectionError("connection closed")
        buf += chunk
    return buf


def file_checksum(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def build_file_meta(filename: str, file_size: int, checksum: str, enc_key: bytes, nonce: bytes, signature: bytes) -> bytes:
    return json.dumps({
        "filename": filename,
        "size": file_size,
        "checksum": checksum,
        "enc_key": enc_key.hex(),
        "nonce": nonce.hex(),
        "signature": signature.hex(),
    }).encode()


def parse_file_meta(raw: bytes) -> dict:
    d = json.loads(raw)
    d["enc_key"] = bytes.fromhex(d["enc_key"])
    d["nonce"] = bytes.fromhex(d["nonce"])
    d["signature"] = bytes.fromhex(d["signature"])
    return d
