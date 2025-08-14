FROM node:20-alpine
WORKDIR /app

# Install deps first (better layer caching)
COPY package*.json ./
RUN npm ci --only=production || npm install --only=production

# Copy app code (includes dealerships.json / reviews.json)
COPY . .

ENV PORT=3000
EXPOSE 3000
CMD ["node", "app.js"]
