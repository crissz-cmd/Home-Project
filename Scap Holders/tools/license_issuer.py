import argparse,base64,json,os,socket,hashlib
from pathlib import Path
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey
PRODUCT="Scap Holders"
def canonical(payload): return json.dumps(payload,sort_keys=True,separators=(",",":")).encode()
def main():
 p=argparse.ArgumentParser(); p.add_argument("--private-key",required=True); p.add_argument("--machine-id",required=True); p.add_argument("--expires",required=True); p.add_argument("--license-id",required=True); p.add_argument("--output",default="license.key"); a=p.parse_args()
 key=serialization.load_pem_private_key(Path(a.private_key).read_bytes(),password=None)
 if not isinstance(key,Ed25519PrivateKey): raise SystemExit("Private key must be Ed25519.")
 payload={"product":PRODUCT,"license_id":a.license_id,"machine_id":a.machine_id.upper(),"expires_at":a.expires}
 payload["signature"]=base64.b64encode(key.sign(canonical(payload))).decode()
 Path(a.output).write_text(json.dumps(payload,indent=2),encoding="utf-8"); print(f"Issued {a.output}")
if __name__=="__main__": main()
