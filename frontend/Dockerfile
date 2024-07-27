FROM node:20-alpine

WORKDIR /app

# Kopiere nur die package.json und yarn.lock (falls vorhanden)
COPY package.json yarn.lock ./

# Installiere die Abhängigkeiten
RUN yarn install

# Kopiere den restlichen Code
COPY . .

# Stelle sicher, dass der Container immer die aktuellsten Dateien hat, während er läuft
VOLUME ["/app/src", "/app/public"]

CMD ["yarn", "start"]