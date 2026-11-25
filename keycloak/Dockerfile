FROM quay.io/keycloak/keycloak:26.8.2 AS builder

# Enable health and metrics support
ENV KC_HEALTH_ENABLED=true
ENV KC_METRICS_ENABLED=true

# Configure a database vendor
ENV KC_DB=postgres

WORKDIR /opt/keycloak
# for demonstration purposes only, please make sure to use proper certificates in production instead
RUN /opt/keycloak/bin/kc.sh build

FROM quay.io/keycloak/keycloak:26.8.2
COPY --from=builder /opt/keycloak/ /opt/keycloak/

# Copy custom themes into the container
COPY themes /opt/keycloak/themes

# Add health check using the management interface on port 9000
HEALTHCHECK --interval=30s --timeout=10s --start-period=60s --retries=3 \
    CMD /opt/keycloak/bin/kc.sh show-config --help >/dev/null 2>&1 || exit 1

ENTRYPOINT ["/opt/keycloak/bin/kc.sh"]
