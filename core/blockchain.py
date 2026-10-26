"""
Blockchain helper.

Default mode is local-demo: the app creates a SHA-256 fingerprint and stores the
proof in Django's database. This makes the project runnable immediately, but it
is NOT a real blockchain. See contracts/CertificateRegistry.sol and README.md
for the optional Ethereum testnet integration extension.
"""
import hashlib
import json
import uuid

def file_sha256(uploaded_file):
    digest = hashlib.sha256()
    for chunk in uploaded_file.chunks():
        digest.update(chunk)
    uploaded_file.seek(0)
    return digest.hexdigest()

def text_sha256(text):
    return hashlib.sha256(text.encode("utf-8")).hexdigest()

def make_demo_record(certificate):
    payload = {
        "certificate_id": certificate.pk,
        "sha256": certificate.sha256_hash,
        "title": certificate.title,
        "issuer": certificate.issuer,
    }
    certificate.chain_record_id = "DEMO-" + uuid.uuid4().hex[:12].upper()
    certificate.transaction_hash = "local-" + hashlib.sha256(
        json.dumps(payload, sort_keys=True).encode("utf-8")
    ).hexdigest()[:32]
    certificate.blockchain_mode = "local-demo"
    certificate.is_registered = True
    certificate.save(update_fields=[
        "chain_record_id", "transaction_hash", "blockchain_mode", "is_registered"
    ])
