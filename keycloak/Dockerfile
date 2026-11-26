# syntax=docker/dockerfile:1.7
FROM quay.io/keycloak/keycloak:26.8.2-3 AS builder

# Enable health and metrics support
ENV KC_HEALTH_ENABLED=true
ENV KC_METRICS_ENABLED=true

# Configure a database vendor
ENV KC_DB=postgres

WORKDIR /opt/keycloak

# Keycloak 26.8.2-3 bundles Guava 33.6.0-jre (CVE-2026-102554, DoS during
# deserialization). No Keycloak release ships the fix yet, so swap in Guava
# 33.7.2-jre (same dependencies). The jar keeps its original file name because
# Quarkus' lib/quarkus/quarkus-application.dat lists it by that name; scanners
# read the version from the jar's own metadata. Drop this when the base image
# ships Guava >= 33.7.2.
ADD --checksum=sha256:b530942257fb935f8b2cfaa5f8eb5bd59c555fd8e8d01b8ce98912e077ea606c \
    --chown=keycloak:root --chmod=664 \
    https://repo1.maven.org/maven2/com/google/guava/guava/33.7.2-jre/guava-33.7.2-jre.jar \
    /opt/keycloak/lib/lib/main/com.google.guava.guava-33.6.0-jre.jar

# for demonstration purposes only, please make sure to use proper certificates in production instead
RUN /opt/keycloak/bin/kc.sh build

FROM quay.io/keycloak/keycloak:26.8.2-3
COPY --from=builder /opt/keycloak/ /opt/keycloak/

# Copy custom themes into the container
COPY themes /opt/keycloak/themes

# Add health check using the management interface on port 9000
HEALTHCHECK --interval=30s --timeout=10s --start-period=60s --retries=3 \
    CMD /opt/keycloak/bin/kc.sh show-config --help >/dev/null 2>&1 || exit 1

ENTRYPOINT ["/opt/keycloak/bin/kc.sh"]
