#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")"
export COMPOSE_PROJECT_NAME="${COMPOSE_PROJECT_NAME:-nextcloud-federated-ocm-token}"
export SENDER_URL="${SENDER_URL:-http://127.0.0.1:18340}"
export RECIPIENT_URL="${RECIPIENT_URL:-http://127.0.0.1:18341}"
export NC_SENDER_USER="${NC_SENDER_USER:-alice}"
export NC_SENDER_PASSWORD="${NC_SENDER_PASSWORD:-LabAlice35!}"
export NC_RECIPIENT_USER="${NC_RECIPIENT_USER:-bob}"
export NC_RECIPIENT_PASSWORD="${NC_RECIPIENT_PASSWORD:-LabBob35!}"
export NC_SHARE_WITH="${NC_SHARE_WITH:-bob@http://recipient}"
WITNESS="NEXTCLOUD-OCM-PERMANENT-TOKEN-WITNESS"
SHARED="shared-with-bob.txt"
chmod +x poc.py

occ() {
  local svc="$1"
  shift
  docker compose exec -T -u www-data "$svc" php occ "$@"
}

down() {
  echo "== docker compose down -v =="
  docker compose down -v --remove-orphans || true
}

echo "== docker compose down (clean) =="
docker compose down -v --remove-orphans || true

echo "== docker compose up (loopback :18340/:18341) =="
up_ok=0
for attempt in $(seq 1 8); do
  if docker compose up -d; then
    up_ok=1
    break
  fi
  echo "IOC compose-up-retry attempt=$attempt"
  sleep 12
done
if [[ "$up_ok" != 1 ]]; then
  echo "FAIL NEXTCLOUD-OCM-PERMANENT-TOKEN docker compose up" | tee poc-last-run.txt
  docker compose logs --tail=80 sender recipient || true
  down
  exit 1
fi

echo "== wait for status.php installed=true =="
ok=0
for i in $(seq 1 120); do
  sbody="$(curl -sS --max-time 8 "${SENDER_URL}/status.php" || true)"
  rbody="$(curl -sS --max-time 8 "${RECIPIENT_URL}/status.php" || true)"
  echo "IOC wait i=$i sender=${sbody} recipient=${rbody}"
  if echo "$sbody" | grep -q '"installed":true' && echo "$rbody" | grep -q '"installed":true'; then
    echo "IOC nextcloud-up sender+recipient installed=true"
    ok=1
    break
  fi
  sleep 5
done
if [[ "$ok" != 1 ]]; then
  echo "FAIL NEXTCLOUD-OCM-PERMANENT-TOKEN status.php not installed" | tee poc-last-run.txt
  docker compose logs --tail=80 sender recipient || true
  down
  exit 1
fi

echo "== seed occ sender/recipient =="
seed_ok=0
for attempt in $(seq 1 20); do
  if occ sender status && occ recipient status; then
    seed_ok=1
    break
  fi
  echo "IOC occ-wait attempt=$attempt"
  sleep 5
done
if [[ "$seed_ok" != 1 ]]; then
  echo "FAIL NEXTCLOUD-OCM-PERMANENT-TOKEN occ not ready" | tee poc-last-run.txt
  docker compose logs --tail=80 sender recipient || true
  down
  exit 1
fi

seed_instance() {
  local svc="$1"
  local cli_url="$2"
  local host="$3"
  occ "$svc" app:enable files_sharing || true
  occ "$svc" app:enable federatedfilesharing || true
  occ "$svc" app:enable federation || true
  occ "$svc" app:enable cloud_federation_api || true
  occ "$svc" config:app:set files_sharing outgoing_server2server_share_enabled --value=yes
  occ "$svc" config:app:set files_sharing incoming_server2server_share_enabled --value=yes
  occ "$svc" config:system:set allow_local_remote_servers --value=true --type=boolean
  occ "$svc" config:system:set overwrite.cli.url --value="${cli_url}"
  occ "$svc" config:system:set overwritehost --value="${host}"
  occ "$svc" config:system:set overwriteprotocol --value=http
  occ "$svc" config:system:set trusted_domains 0 --value=localhost
  occ "$svc" config:system:set trusted_domains 1 --value=127.0.0.1
  occ "$svc" config:system:set trusted_domains 2 --value="${host}"
  occ "$svc" config:system:set auth.bruteforce.protection.enabled --value=false --type=boolean || true
  occ "$svc" config:system:set ratelimit.protection.enabled --value=false --type=boolean || true
  occ "$svc" config:system:set lookup_server --value="" || true
}

seed_instance sender "http://sender" sender
seed_instance recipient "http://recipient" recipient

# Keep the pre-exchange window: recipient shareReceived optionally POSTs
# access-token when sender advertises exchange-token. First successful
# exchange locks SCOPE_FILESYSTEM on the minted refresh token.
occ sender config:app:set core ocm_discovery_enabled --value=false --type=boolean || true

echo "== plant sender DAV files =="
plant_ok=0
for i in $(seq 1 30); do
  scode="$(curl -sS -o /tmp/nc-ocm-plant-shared -w '%{http_code}' --max-time 20 \
    -u "${NC_SENDER_USER}:${NC_SENDER_PASSWORD}" \
    -H 'Content-Type: text/plain' \
    -X PUT \
    --data-binary "SHARED-ONLY" \
    "${SENDER_URL}/remote.php/dav/files/${NC_SENDER_USER}/${SHARED}" || true)"
  wcode="$(curl -sS -o /tmp/nc-ocm-plant-witness -w '%{http_code}' --max-time 20 \
    -u "${NC_SENDER_USER}:${NC_SENDER_PASSWORD}" \
    -H 'Content-Type: text/plain' \
    -X PUT \
    --data-binary "${WITNESS}" \
    "${SENDER_URL}/remote.php/dav/files/${NC_SENDER_USER}/${WITNESS}.txt" || true)"
  echo "IOC plant i=$i shared_http=$scode witness_http=$wcode"
  if [[ "$scode" == "201" || "$scode" == "204" || "$scode" == "200" ]] && \
     [[ "$wcode" == "201" || "$wcode" == "204" || "$wcode" == "200" ]]; then
    plant_ok=1
    break
  fi
  sleep 3
done
if [[ "$plant_ok" != 1 ]]; then
  echo "FAIL NEXTCLOUD-OCM-PERMANENT-TOKEN plant witness DAV" | tee poc-last-run.txt
  docker compose logs --tail=80 sender || true
  down
  exit 1
fi

echo "== poc.py =="
set +e
python3 poc.py | tee poc-last-run.txt
rc=${PIPESTATUS[0]}
set -e
if [[ "$rc" != 0 ]]; then
  echo "== sender/recipient logs (tail) ==" | tee -a poc-last-run.txt
  docker compose logs --tail=120 sender recipient | tee -a poc-last-run.txt || true
  echo "== occ sender log:tail ==" | tee -a poc-last-run.txt
  occ sender log:tail --lines=80 | tee -a poc-last-run.txt || true
  echo "== occ recipient log:tail ==" | tee -a poc-last-run.txt
  occ recipient log:tail --lines=80 | tee -a poc-last-run.txt || true
fi
down
exit "$rc"
