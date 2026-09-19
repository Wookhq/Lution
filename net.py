# lution can't fetch the marketplace and this fixes it
import os

_CA_FILES = (
    "/etc/ssl/certs/ca-certificates.crt",
    "/etc/pki/tls/certs/ca-bundle.crt",
    "/etc/pki/ca-trust/extracted/pem/tls-ca-bundle.pem",
    "/etc/ssl/cert.pem",
)
_CA_DIRS = ("/etc/ssl/certs",)

_done = {"set": False}

def ensure_ca_certs():
    if _done["set"]:
        return
    _done["set"] = True
    if os.environ.get("SSL_CERT_FILE") or os.environ.get("SSL_CERT_DIR"):
        return
    for p in _CA_FILES:
        if os.path.isfile(p) and os.path.getsize(p) > 0:
            os.environ["SSL_CERT_FILE"] = p
            break
    for p in _CA_DIRS:
        if os.path.isdir(p):
            os.environ["SSL_CERT_DIR"] = p
            break
    if "SSL_CERT_FILE" in os.environ:
        try:
            import log
            log.debug(f"Using host CA bundle: {os.environ['SSL_CERT_FILE']}")
        except Exception:
            pass
