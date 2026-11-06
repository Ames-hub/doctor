from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import rsa
from datetime import datetime, timedelta, timezone
from cryptography.x509.oid import NameOID
from cryptography import x509
from pathlib import Path

def generate_self_signed_cert(
    key_path: str = "certs/private.key",
    cert_path: str = "certs/public.crt",
):
    # Generate private key
    private_key = rsa.generate_private_key(
        public_exponent=65537,
        key_size=2048,
    )

    # Certificate identity
    subject = issuer = x509.Name([
        x509.NameAttribute(NameOID.COUNTRY_NAME, "AU"),
        x509.NameAttribute(NameOID.ORGANIZATION_NAME, "Doctor OS Monitoring Software"),
        x509.NameAttribute(NameOID.COMMON_NAME, "localhost"),
    ])

    # Create self-signed certificate
    certificate = (
        x509.CertificateBuilder()
        .subject_name(subject)
        .issuer_name(issuer)
        .public_key(private_key.public_key())
        .serial_number(x509.random_serial_number())
        .not_valid_before(datetime.now(timezone.utc))
        .not_valid_after(datetime.now(timezone.utc) + timedelta(days=365))
        .add_extension(
            x509.SubjectAlternativeName([
                x509.DNSName("localhost"),
                x509.IPAddress(__import__("ipaddress").ip_address("127.0.0.1")),
            ]),
            critical=False,
        )
        .sign(private_key, hashes.SHA256())
    )

    # Save private key
    Path(key_path).write_bytes(
        private_key.private_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PrivateFormat.TraditionalOpenSSL,
            encryption_algorithm=serialization.NoEncryption(),
        )
    )

    # Save certificate
    Path(cert_path).write_bytes(
        certificate.public_bytes(serialization.Encoding.PEM)
    )

    return key_path, cert_path