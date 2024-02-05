#to do_ fix version
FROM node:current-alpine3.18

ENV NODE_ENV production

WORKDIR /usr/src/app

# Copy package.json and package-lock.json first to leverage Docker caching
COPY ./package.json .
COPY ./package-lock.json .

# Install devDependencies & Dependencies
#to do get from env
RUN npm install --production=false

COPY ./src ./src

USER node

EXPOSE 3100

CMD ["npm", "run", "dev"]
 