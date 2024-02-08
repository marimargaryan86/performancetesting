ARG REGISTRY
ARG NODE_VERSION
FROM ${REGISTRY}node:${NODE_VERSION}-bookworm-slim AS build
RUN corepack enable
WORKDIR /app
COPY svelte/package.json svelte/yarn.lock svelte/.yarnrc.yml ./
COPY svelte/hub-web/package.json svelte/hub-web/svelte.config.js svelte/hub-web/vite.config.ts ./hub-web/
RUN yarn install --immutable
COPY svelte/hub-web ./hub-web
RUN yarn workspace @snowfall/hub-web build \
    && rm -rf node_modules \
    && yarn workspaces focus --production -A \
    && cp -r node_modules hub-web/build/node_modules \
    && cp hub-web/package.json hub-web/build/

FROM ${REGISTRY}node:${NODE_VERSION}-bookworm-slim AS runtime
WORKDIR /app
COPY --from=build /app/hub-web/build /app
ARG VERSION "dev"
ENV VERSION $VERSION
LABEL vendor="Snowfall Limited"
LABEL com.snowfalltravel.version=$VERSION
CMD ["node", "/app"]
