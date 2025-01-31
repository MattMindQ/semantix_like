FROM node:18-alpine

WORKDIR /app

# Copy package files
COPY package*.json ./

# Install dependencies
RUN npm install

# Copy the rest of the code
COPY . .

# For development: Start Vite dev server
CMD ["npm", "run", "dev", "--", "--host", "0.0.0.0"]