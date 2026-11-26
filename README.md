# bridge-to-bridge-api

## Deploying

Merging to `main` deploys. `.github/workflows/ci.yml` runs the tests, builds the API and
Keycloak images, pushes them to the private registry on Omarchy tagged with the commit SHA,
and runs `/usr/local/bin/deploy-app brug-tot-brug <sha>` over SSH (a forced-command key that
can do nothing else). That script recreates `api` and `bridge-keycloak`, waits until the stack
is healthy, rolls back to the previous tag when it is not, and records the deployed tag in
`~/deployments/brug-tot-brug/.deployed_image_tag`. Keycloak restarts on every deploy (about a
minute without logins). A failed deploy opens a `deploy-failure` issue.

The CI secrets live in the repository's `production` environment: `TS_OAUTH_CLIENT_ID`,
`TS_OAUTH_SECRET`, `REGISTRY_HOST`, `REGISTRY_USERNAME`, `REGISTRY_PASSWORD`, `PROD_SSH_HOST`,
`PROD_SSH_USER`, `PROD_SSH_KEY`, `PROD_SSH_KNOWN_HOSTS` and optionally `PROD_SSH_PORT`.

CI never changes `docker-compose.yml`, `.env` or `keycloak/realm-config/` on the server. When
one of those changes, copy it by hand and restart with the deployed tag:

```sh
cd ~/deployments/brug-tot-brug
cp <checkout>/docker-compose.yml . && cp -r <checkout>/keycloak/realm-config keycloak/
IMAGE_TAG="$(cat .deployed_image_tag)" docker compose up -d
```

Production imports `bridge-realm-prod.json` (`KEYCLOAK_REALM_IMPORT_FILE`). Keycloak imports
a realm file only when the realm does not exist yet, so a change to it does not reach the
running realm: make the same change in the admin console as well.

The server also has a `docker-compose.override.yml` that is not in this repository. It marks
the two database volumes as external, because they were created before this compose
project existed.

Always pass `IMAGE_TAG` like this for manual `docker compose` commands; `.env` does not
pin it, so without it compose falls back to `latest`.
## Keycloak hostnames

Keycloak uses hostname v2:

- `KEYCLOAK_HOSTNAME` (`KC_HOSTNAME`), e.g. `auth.brug-tot-brug.casteleijn.com`: the login
  hostname used by the app and the token issuer of the app realm.
- `KC_HOSTNAME_ADMIN`: the only address for the admin console. It is
  `KEYCLOAK_ADMIN_URL` when set, otherwise `KEYCLOAK_PROTOCOL://KEYCLOAK_ADMIN_HOSTNAME`.

`KC_HOSTNAME_ADMIN` only tells the admin console which URL to use. Keycloak still answers
`/admin/` and `/realms/master/` on every hostname, so the reverse proxy must block them on
the login hostnames:

```nginx
server {
    server_name auth.brug-tot-brug.casteleijn.com;
    location ^~ /admin/ { return 404; }
    location ^~ /realms/master/ { return 404; }
    location / { proxy_pass http://bridge-keycloak:8080; }
}
```

### Production: admin console on the tailnet only

The admin console is not published on the internet. Keycloak listens on
`127.0.0.1:${KEYCLOAK_ADMIN_LOCAL_PORT:-8180}` and Tailscale publishes that port to the
tailnet only:

```sh
tailscale serve --bg --https=8443 http://127.0.0.1:8180
```

with, in the production `.env`:

```sh
KEYCLOAK_ADMIN_URL=https://omarchy.tail0118fa.ts.net:8443
```

and the master realm's *Frontend URL* (Realm settings → General) set to the same URL, so the
admin login page and its tokens also stay on the tailnet. Open the console at
`https://omarchy.tail0118fa.ts.net:8443/admin/master/console/` from a device on the tailnet.

### The API's Keycloak access

The API invites users with the service account of the `bridge-api-admin` client in the app
realm (client credentials, roles `realm-management/manage-users` and `view-users`, full scope off,
plus the built-in `kc-admin-api` client scope: Keycloak 26.8 rejects admin API tokens without
the admin API audience it adds), set by
`KEYCLOAK_API_ADMIN_CLIENT_SECRET`. It does not hold the master admin password. It reaches
Keycloak over the internal network (`http://bridge-keycloak:8080`), so the proxy rules
above do not affect it.
