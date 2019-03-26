import datetime
import os

from cryptography import x509
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric import rsa
from cryptography.x509.oid import NameOID


def create_certs(cert_path, domain='localhost', sans=[]):
    subject = issuer = x509.Name([
        x509.NameAttribute(NameOID.COUNTRY_NAME, u"US"),
        x509.NameAttribute(NameOID.STATE_OR_PROVINCE_NAME, u"California"),
        x509.NameAttribute(NameOID.LOCALITY_NAME, u"San Francisco"),
        x509.NameAttribute(NameOID.ORGANIZATION_NAME, u"My Company"),
        x509.NameAttribute(NameOID.COMMON_NAME, domain)])

    ca_key = rsa.generate_private_key(
        public_exponent=65537,
        key_size=2048,
        backend=default_backend())

    ca_cert = x509.CertificateBuilder().subject_name(
        subject
    ).issuer_name(
        issuer
    ).public_key(
        ca_key.public_key()
    ).serial_number(
        x509.random_serial_number()
    ).not_valid_before(
        datetime.datetime.utcnow() - datetime.timedelta(days=2)
    ).not_valid_after(
        datetime.datetime.utcnow() + datetime.timedelta(days=14)
    ).sign(ca_key, hashes.SHA256(), default_backend())

    local_key = rsa.generate_private_key(
        public_exponent=65537,
        key_size=2048,
        backend=default_backend())

    local_cert = x509.CertificateBuilder().subject_name(
        subject
    ).issuer_name(
        issuer
    ).public_key(
        local_key.public_key()
    ).serial_number(
        x509.random_serial_number()
    ).not_valid_before(
        datetime.datetime.utcnow() - datetime.timedelta(days=1)
    ).not_valid_after(
        datetime.datetime.utcnow() + datetime.timedelta(days=7)
    ).add_extension(
        x509.SubjectAlternativeName([x509.DNSName(san) for san in sans]),
        critical=False
    ).sign(ca_key, hashes.SHA256(), default_backend())

    os.makedirs(cert_path, exist_ok=True)

    with open(os.path.join(cert_path, 'rootCA.crt'), 'wb+') as f:
        f.write(ca_cert.public_bytes(serialization.Encoding.PEM))

    with open(os.path.join(cert_path, 'rootCA.key'), 'wb+') as f:
        f.write(ca_key.private_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PrivateFormat.TraditionalOpenSSL,
            encryption_algorithm=serialization.NoEncryption()
        ))

    with open(os.path.join(cert_path, 'localhost.crt'), 'wb+') as f:
        f.write(local_cert.public_bytes(serialization.Encoding.PEM))

    with open(os.path.join(cert_path, 'localhost.key'), 'wb+') as f:
        f.write(local_key.private_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PrivateFormat.TraditionalOpenSSL,
            encryption_algorithm=serialization.NoEncryption()
        ))

    with open(os.path.join(cert_path, 'bundle'), 'wb+') as f:
        f.write(local_cert.public_bytes(serialization.Encoding.PEM))
        f.write('\n'.encode('utf-8'))
        f.write(ca_cert.public_bytes(serialization.Encoding.PEM))


if __name__ == '__main__':
    create_certs(u'localhost', [u"*.s3.us-west-2.amazonaws.com"])
