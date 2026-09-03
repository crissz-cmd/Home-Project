from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey
import base64
key=Ed25519PrivateKey.generate()
open("private_key.pem","wb").write(key.private_bytes(serialization.Encoding.PEM,serialization.PrivateFormat.PKCS8,serialization.NoEncryption()))
pub=key.public_key().public_bytes(serialization.Encoding.Raw,serialization.PublicFormat.Raw)
print("SCAP_PUBLIC_KEY_B64="+base64.b64encode(pub).decode())
print("Keep private_key.pem secret and backed up.")
