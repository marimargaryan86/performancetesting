FROM node:16-bullseye-slim

WORKDIR /app
RUN chown -R node:node /app

COPY --chown=node:node ./package.json ./yarn.lock ./svelte.config.js ./

USER node

RUN yarn install && yarn cache clean

COPY --chown=node:node . .

RUN yarn run lint && yarn run build && find /app -mindepth 1 ! -regex '^/app/build\(/.*\)?' -delete
COPY --chown=node:node ./package.json ./

CMD ["node", "/app/build/index.js"]
