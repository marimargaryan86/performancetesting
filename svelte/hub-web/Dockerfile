FROM node:19-bullseye-slim

WORKDIR /app
RUN chown -R node:node /app

COPY --chown=node:node package.json yarn.lock svelte.config.js vite.config.ts ./

USER node

RUN yarn install && yarn cache clean

COPY --chown=node:node . .

RUN yarn run lint && yarn run build

EXPOSE 3000

CMD ["node", "/app/build/index.js"]
