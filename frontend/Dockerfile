# frontend/Dockerfile

# Stage 1: Build
FROM node:20-alpine as build-stage

WORKDIR /app

COPY package*.json ./
RUN npm install

COPY . .

# Argument for the production API URL
ARG VITE_API_URL
ENV VITE_API_URL=$VITE_API_URL

RUN npm run build

# Stage 2: Verification (Optional, files will be moved by compose volume in prod)
# This stage just confirms the build exists within the container
FROM alpine:latest as verification
COPY --from=build-stage /app/dist /dist
CMD ["ls", "-la", "/dist"]
