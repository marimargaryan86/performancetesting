FROM node:19-bullseye-slim AS build
WORKDIR /app
COPY package.json yarn.lock svelte.config.js vite.config.ts ./
RUN yarn install && yarn cache clean
COPY . .
RUN yarn run build
COPY package.json build/package.json

FROM node:19-bullseye-slim AS runtime
WORKDIR /app
COPY --from=build /app/build /app
EXPOSE 3000
CMD ["node", "/app/index.js"]
