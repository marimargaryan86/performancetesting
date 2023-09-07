ARG REGISTRY
FROM ${REGISTRY}node:19-bullseye-slim AS build
WORKDIR /app
COPY package.json yarn.lock svelte.config.js vite.config.ts ./
RUN yarn install --frozen-lockfile
COPY . .
RUN yarn run build && cp package.json yarn.lock build/
WORKDIR /app/build
RUN yarn install --frozen-lockfile --production=true && rm yarn.lock

FROM ${REGISTRY}node:19-bullseye-slim AS runtime
WORKDIR /app
COPY --from=build /app/build /app
ARG VERSION "dev"
ENV VERSION $VERSION
LABEL vendor="Snowfall Limited"
LABEL com.snowfalltravel.version=$VERSION
CMD ["node", "/app"]
