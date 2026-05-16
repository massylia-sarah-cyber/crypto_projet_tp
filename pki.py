import os
import datetime
from pathlib import Path
from cryptography import x509
from cryptography.x509.oid import NameOID
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import rsa, padding

CERTS_DIR = Path(__file__).parent / "certs"
CERTS_DIR.mkdir(exist_ok=True)


def generate_rsa_key(bits=2048):
    return rsa.generate_private_key(public_exponent=65537, key_size=bits)


def save_private_key(key, path: Path, password: bytes = None):
    enc = (
        serialization.BestAvailableEncryption(password)
        if password
        else serialization.NoEncryption()
    )
    path.write_bytes(
        key.private_bytes(
            serialization.Encoding.PEM,
            serialization.PrivateFormat.TraditionalOpenSSL,
            enc
        )
    )


def save_certificate(cert, path: Path):
    path.write_bytes(cert.public_bytes(serialization.Encoding.PEM))


def load_private_key(path: Path, password: bytes = None):
    return serialization.load_pem_private_key(path.read_bytes(), password=password)


def load_certificate(path: Path):
    return x509.load_pem_x509_certificate(path.read_bytes())


def generate_ca():
    ca_key_path = CERTS_DIR / "ca.key"
    ca_cert_path = CERTS_DIR / "ca.crt"

    if ca_key_path.exists() and ca_cert_path.exists():
        return load_private_key(ca_key_path), load_certificate(ca_cert_path)

    key = generate_rsa_key()
    subject = issuer = x509.Name([
        x509.NameAttribute(NameOID.COUNTRY_NAME, "DZ"),
        x509.NameAttribute(NameOID.ORGANIZATION_NAME, "CryptoExchange CA"),
        x509.NameAttribute(NameOID.COMMON_NAME, "Root CA"),
    ])
    cert = (
        x509.CertificateBuilder()
        .subject_name(subject)
        .issuer_name(issuer)
        .public_key(key.public_key())
        .serial_number(x509.random_serial_number())
        .not_valid_before(datetime.datetime.now(datetime.timezone.utc))
        .not_valid_after(datetime.datetime.now(datetime.timezone.utc) + datetime.timedelta(days=3650))
        .add_extension(x509.BasicConstraints(ca=True, path_length=None), critical=True)
        .sign(key, hashes.SHA256())
    )
    save_private_key(key, ca_key_path)
    save_certificate(cert, ca_cert_path)
    return key, cert


def issue_certificate(common_name: str, ca_key, ca_cert):
    key_path = CERTS_DIR / f"{common_name}.key"
    cert_path = CERTS_DIR / f"{common_name}.crt"

    if key_path.exists() and cert_path.exists():
        return load_private_key(key_path), load_certificate(cert_path)

    key = generate_rsa_key()
    subject = x509.Name([
        x509.NameAttribute(NameOID.COUNTRY_NAME, "DZ"),
        x509.NameAttribute(NameOID.ORGANIZATION_NAME, "CryptoExchange"),
        x509.NameAttribute(NameOID.COMMON_NAME, common_name),
    ])
    cert = (
        x509.CertificateBuilder()
        .subject_name(subject)
        .issuer_name(ca_cert.subject)
        .public_key(key.public_key())
        .serial_number(x509.random_serial_number())
        .not_valid_before(datetime.datetime.now(datetime.timezone.utc))
        .not_valid_after(datetime.datetime.now(datetime.timezone.utc) + datetime.timedelta(days=365))
        .add_extension(x509.BasicConstraints(ca=False, path_length=None), critical=True)
        .sign(ca_key, hashes.SHA256())
    )
    save_private_key(key, key_path)
    save_certificate(cert, cert_path)
    return key, cert


def verify_certificate(cert, ca_cert):
    """Fixed version: uses UTC-aware dates + better error reporting"""
    try:
        # Verify signature
        ca_cert.public_key().verify(
            cert.signature,
            cert.tbs_certificate_bytes,
            padding.PKCS1v15(),
            cert.signature_hash_algorithm,
        )

        # Use UTC-aware comparison (fixes deprecation warning and timing issues)
        now = datetime.datetime.now(datetime.timezone.utc)
        not_before = cert.not_valid_before_utc
        not_after = cert.not_valid_after_utc

        if not (not_before <= now <= not_after):
            print(f"[PKI] Certificate time invalid: now={now}, valid from {not_before} to {not_after}")
            return False

        return True
    except Exception as e:
        print(f"[PKI] Certificate verification failed: {type(e).__name__}: {e}")
        return False


def sign_data(data: bytes, private_key) -> bytes:
    return private_key.sign(
        data,
        padding.PSS(mgf=padding.MGF1(hashes.SHA256()), salt_length=padding.PSS.MAX_LENGTH),
        hashes.SHA256()
    )


def verify_signature(data: bytes, signature: bytes, public_key) -> bool:
    try:
        public_key.verify(
            signature,
            data,
            padding.PSS(mgf=padding.MGF1(hashes.SHA256()), salt_length=padding.PSS.MAX_LENGTH),
            hashes.SHA256()
        )
        return True
    except Exception:
        return False


def rsa_encrypt(data: bytes, public_key) -> bytes:
    return public_key.encrypt(
        data,
        padding.OAEP(mgf=padding.MGF1(algorithm=hashes.SHA256()), algorithm=hashes.SHA256(), label=None)
    )


def rsa_decrypt(data: bytes, private_key) -> bytes:
    return private_key.decrypt(
        data,
        padding.OAEP(mgf=padding.MGF1(algorithm=hashes.SHA256()), algorithm=hashes.SHA256(), label=None)
    )


def bootstrap_pki():
    ca_key, ca_cert = generate_ca()
    server_key, server_cert = issue_certificate("server", ca_key, ca_cert)
    client_key, client_cert = issue_certificate("client", ca_key, ca_cert)
    return {
        "ca": (ca_key, ca_cert),
        "server": (server_key, server_cert),
        "client": (client_key, client_cert),
    }