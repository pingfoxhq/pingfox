import requests
import dramatiq
from .models import Site, verification_file_path
from apps.core.utils import get_or_null


@dramatiq.actor
def verify_site(site_id):
    """
    Verify the ownership of a site by checking for a specific token.
    """
    site = get_or_null(Site, site_id=site_id)
    if not site:
        print(f"[PingFox Verify] Site ID {site_id} not found.")

    for protocol in ["https://", "http://"]:
        url = f"{protocol}{site.domain}/{verification_file_path()}"
        try:
            response = requests.get(url, timeout=10, headers={"User-Agent": "PingFox Verification Bot"})
            if (
                response.status_code == 200
                and response.text.strip() == site.verification_token
            ):
                site.is_verified = True
                site.save(update_fields=["is_verified"])
                print(f"[PingFox Verify] Site verified: {site.domain}")
        except requests.RequestException as e:
            continue

    print(f"[PingFox Verify] Verification failed for {site.domain}")
