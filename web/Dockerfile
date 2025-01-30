FROM node:22-alpine AS builder

WORKDIR /usr/src/app

COPY package*.json ./
RUN npm i

COPY . .

RUN npm run build

FROM node:22-alpine

WORKDIR /usr/src/app

COPY package*.json ./
RUN npm ci --production

COPY --from=builder /usr/src/app/dist/assets /usr/src/app/assets
COPY --from=builder /usr/src/app/dist/templates /usr/src/app/templates
COPY --from=builder /usr/src/app/build /usr/src/app

CMD [ "node", "index.js" ]
# CMD ["tail", "-f", "/dev/null"]