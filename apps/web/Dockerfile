FROM node:22-alpine

WORKDIR /app

COPY package.json package-lock.json ./
RUN npm ci

COPY . .

# Rewrites are evaluated at build time by Next.js. The browser talks to Next on :3000
# and Next forwards /api/* to the Compose API service.
ARG API_PROXY_TARGET=http://api:8000
ENV API_PROXY_TARGET=${API_PROXY_TARGET}

RUN npm run build

EXPOSE 3000

CMD ["npm", "start"]
