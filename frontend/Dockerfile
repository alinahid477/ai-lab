# === Stage 1: Builder ===
FROM node:23-bullseye AS builder

# Create app directory
WORKDIR /app

# Copy lock file and package.json
COPY package.json package-lock.json* ./

# Install dependencies
RUN \
  if [ -f package-lock.json ]; then npm ci; \
  elif [ -f yarn.lock ]; then npm install -g yarn && yarn install --frozen-lockfile; \
  elif [ -f pnpm-lock.yaml ]; then npm install -g pnpm && pnpm install --frozen-lockfile; \
  else echo "No lock file found" && exit 1; fi

# Copy rest of the source code
COPY . .

# Build the app
RUN npm run build



# === Stage 2: Runner ===
FROM node:23-bullseye-slim AS runner

# Create app directory
WORKDIR /app

# Install production dependencies only
COPY --from=builder /app/package.json ./
COPY --from=builder /app/node_modules ./node_modules

# Copy built application
COPY --from=builder /app/.next ./.next
COPY --from=builder /app/public ./public
COPY --from=builder /app/postcss.config.mjs ./postcss.config.mjs
COPY --from=builder /app/tailwind.config.js ./tailwind.config.js
COPY --from=builder /app/tsconfig.app.json ./tsconfig.app.json
COPY --from=builder /app/tsconfig.json ./tsconfig.json
COPY --from=builder /app/tsconfig.node.json ./tsconfig.node.json
# Optional: set environment variables
ENV NODE_ENV=production
ENV PORT=3000

# Expose the port Next.js will run on
EXPOSE 3000

# Start the app
CMD ["npm", "start"]