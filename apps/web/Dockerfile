FROM node:20-slim AS builder

WORKDIR /app

# Copy shared types
COPY shared /shared

# Install deps
COPY apps/web/package*.json ./
RUN npm install

# Build (VITE_API_KEY not needed — key is entered at runtime via browser)
COPY apps/web .
RUN npm run build

# Serve with nginx
FROM nginx:alpine
COPY --from=builder /app/dist /usr/share/nginx/html
COPY apps/web/nginx-spa.conf /etc/nginx/conf.d/default.conf
EXPOSE 80
