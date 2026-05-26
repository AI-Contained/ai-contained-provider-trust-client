ARG TRUST_SERVER_REF=heads/main

FROM alpine AS package-client
# ai-contained-provider-trust-server bundles both our client and server into seperate packages
#  it was written this way, so that development and regressions can be isolated and tested into
#  a single PR.  However, that means the packaging for this repo is a little "different" and we
#  fetch the source code for the client from ai-contained-provider-trust-server.
ARG TRUST_SERVER_REF
ADD https://github.com/AI-Contained/ai-contained-provider-trust-server/archive/refs/${TRUST_SERVER_REF}.tar.gz /tmp/trust-server.tar.gz
RUN tar -xzf /tmp/trust-server.tar.gz \
    && mv ai-contained-provider-trust-server-*/packages/client /opt/ai-contained-provider-trust-server-client

FROM scratch
COPY --from=package-client /opt/ai-contained-provider-trust-server-client /opt/ai-contained-provider-trust-server-client
COPY . /opt/ai-contained-provider-trust-client
