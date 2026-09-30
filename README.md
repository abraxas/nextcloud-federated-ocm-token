<p align="center">
  <img src="header.png" alt="Abraxas Labs - nextcloud-federated-ocm-token" width="100%">
</p>

<p align="center">
  <a href="https://abraxaslabs.tech"><strong>abraxaslabs.tech</strong></a>
  &nbsp;·&nbsp;
  <a href="https://github.com/abraxas">github.com/abraxas</a>
  &nbsp;·&nbsp;
  <a href="https://x.com/abraxas_null">@abraxas_null</a>
  &nbsp;·&nbsp;
  <a href="https://github.com/abraxas/nextcloud-federated-ocm-token">nextcloud-federated-ocm-token</a>
</p>

# nextcloud-federated-ocm-token

**Nextcloud Server** `35.0.0` - Nextcloud GmbH

Unpublished Nextcloud source finding: a federated share secret is minted as an unscoped `PERMANENT_TOKEN` app password for the sharer. The recipient API returns it as `refresh_token`. Replaying it as Bearer on the sender WebDAV logs in as the sharer and reads files **that were never shared**.

**A bad actor you federated-share one file with can log in as you on your Nextcloud, skip 2FA, and read or overwrite all of your files, not just the one you shared.**

| | |
|---|---|
| ID | Unpublished Nextcloud source finding #1 (no CVE yet) |
| CWE | [CWE-269, CWE-287](https://cwe.mitre.org/data/definitions/269.html) |
| CVSS | **Critical: 8.1** `CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:N` (federated recipient). Public-link convert is worse (no recipient account on a peer). |
| Product | [Nextcloud Server](https://github.com/nextcloud/server) |
| Affected | **35.0.0** (`da02f41`) official `nextcloud:35.0.0-apache` |
| Patched | vendor patch - see references |
| Auth | federated recipient (or public-link converter) |
| License | [GNU Affero GPL v3.0](LICENSE) |
| Lab | `127.0.0.1` only |

---

## What an attacker can do

You share **one** file or folder with `bob` on another Nextcloud. Nextcloud mints a 32-character secret, stores it as **your app password**, and hands that secret to Bob as `refresh_token`.

Bob (or anyone who converts your **public link** into a federated share) then:

- **Logs in as you** on **your** server
- **Reads every file** in your home, not only the shared node
- **Overwrites** those files
- **Skips your 2FA** (app-password path)

They do not get a PHP shell on the host. They do not need your password. Do not accept the share and do not call OCM `access-token` first: that exchange locks filesystem scope. The lab proves the **pre-exchange** secret.

---

## Advisory (from the source map)

`FederatedShareProvider::createFederatedShare` `generateToken(..., type: PERMANENT_TOKEN)` with no scope. `PublicKeyToken` defaults `SCOPE_FILESYSTEM => true`. `GET /ocs/v2.php/apps/files_sharing/api/v1/remote_shares/pending` returns `refresh_token`. `Session::tryTokenLogin` accepts permanent Bearer and sets `app_password`. OCM access-token hop is rejected on `/remote.php/dav` on this tree.

---

## Reproduction (authorized lab)

```bash
cd lab
./run.sh
```

Target **only** `http://127.0.0.1:18340` (sender) and `:18341` (recipient).

Success last line:

```text
SUCCESS NEXTCLOUD-OCM-PERMANENT-TOKEN who=federated-recipient uid=alice NEXTCLOUD-OCM-PERMANENT-TOKEN-WITNESS
```

---

## Lab images

- [`lab/docker-compose.yml`](lab/docker-compose.yml)
- [`lab/Dockerfile`](lab/Dockerfile)
- [`lab/run.sh`](lab/run.sh)

Publish nothing except `127.0.0.1`.

---

## References

- [github.com/nextcloud/server](https://github.com/nextcloud/server) tag [v35.0.0](https://github.com/nextcloud/server/releases/tag/v35.0.0)
- Nearby OCM work: [PR #57234](https://github.com/nextcloud/server/pull/57234) / [PR #57166](https://github.com/nextcloud/server/pull/57166). TokenController locks FS scope **after** first exchange; create still mints unscoped.
- Unofficial writeup used the **post-exchange** hop, which this tree rejects on DAV. This pack is the pre-exchange permanent token.
- Vendor intake: [hackerone.com/nextcloud](https://hackerone.com/nextcloud). Do **not** open a public GitHub issue.
- Abraxas Labs: [abraxaslabs.tech](https://abraxaslabs.tech) · [github.com/abraxas](https://github.com/abraxas) · [@abraxas_null](https://x.com/abraxas_null)

---

## License

GNU Affero GPL v3.0. See [LICENSE](LICENSE). Loopback lab only. No warranty.
