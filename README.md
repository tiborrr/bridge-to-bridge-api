# bridge-to-bridge-api
## Keycloak hostnames

Keycloak uses hostname v2 with two hostnames:

- `KEYCLOAK_HOSTNAME` (`KC_HOSTNAME`), e.g. `auth.brug-tot-brug.casteleijn.com`: the login
  hostname used by the app and the token issuer.
- `KEYCLOAK_ADMIN_HOSTNAME` (`KC_HOSTNAME_ADMIN`), e.g. `admin.brug-tot-brug.casteleijn.com`:
  the only hostname for the admin console.

`KC_HOSTNAME_ADMIN` only tells the admin console which URL to use. Keycloak still answers
`/admin/` on every hostname, so the reverse proxy must block it on the login hostnames:

```nginx
server {
    server_name auth.brug-tot-brug.casteleijn.com;
    location ^~ /admin/ { return 404; }
    location / { proxy_pass http://bridge-keycloak:8080; }
}
server {
    server_name admin.brug-tot-brug.casteleijn.com;
    location / { proxy_pass http://bridge-keycloak:8080; }
}
```

The API talks to Keycloak's admin REST API over the internal network
(`http://bridge-keycloak:8080`), so it is not affected by the proxy rule.
