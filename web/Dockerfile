FROM node:16-alpine AS builder

WORKDIR /usr/src/app

COPY package*.json ./
RUN npm i

COPY . .

RUN npm run build

FROM node:16-alpine

WORKDIR /usr/src/app

COPY package*.json ./
RUN npm ci --production

COPY --from=builder /usr/src/app/templates /usr/src/app/templates
COPY --from=builder /usr/src/app/build /usr/src/app

CMD [ "node", "index.js" ]