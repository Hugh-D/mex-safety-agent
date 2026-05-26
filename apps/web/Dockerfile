FROM node:20-slim AS builder

WORKDIR /app

# Copy shared types
COPY ../../shared /shared

# Install deps
COPY package*.json ./
RUN npm ci

# Build (VITE_API_KEY not needed — key is entered at runtime via browser)
COPY . .
RUN npm run build

# Serve with nginx
FROM nginx:alpine
COPY --from=builder /app/dist /usr/share/nginx/html
COPY nginx-spa.conf /etc/nginx/conf.d/default.conf
EXPOSE 80
