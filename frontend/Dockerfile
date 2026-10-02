FROM node:20-alpine

WORKDIR /app

ENV NEXT_TELEMETRY_DISABLED=1

COPY package*.json ./
RUN npm ci

COPY . .

RUN mkdir -p public && npm run build

EXPOSE 3000

ENV NODE_ENV=production

CMD ["sh", "-c", "npm run start -- --hostname 0.0.0.0 --port ${PORT:-3000}"]
