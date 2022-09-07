FROM node:16-bullseye-slim

WORKDIR /app
RUN chown -R node:node /app

COPY --chown=node:node ./package.json ./yarn.lock ./svelte.config.js ./

USER node

RUN yarn install && yarn cache clean

COPY --chown=node:node . .

RUN yarn run lint && yarn run build

EXPOSE 3000

CMD ["node", "/app/build/index.js"]
