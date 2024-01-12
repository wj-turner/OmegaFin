const express = require('express');
const app = express();
const fs = require('fs');
const OANDAAdapter = require("oanda-adapter")
const path = require('path');
const port = 3000;
const Redis = require('ioredis');

const client = new OANDAAdapter({
    // 'live' or 'practice'
    environment: "practice",
    // Generate your API access token in the 'Manage API Access' section of 'My Account' on OANDA's website
    accessToken: "f1d687560e287d40aed90ccb899aad3c-14a9bd4b6b8e9c09f864cd222690f293"
})

const redis = new Redis({
    host: 'redis-live-data',
    port: 6379,
  });


////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////
const streamKey = 'test_stream';

// // Function to generate sample data
// function generateData() {
//   const timestamp = new Date().toISOString();
//   const value = Math.random() * 100;
//   return { timestamp, value };
// }


// const streamKeyPrefix = 'price_stream_';
// client.subscribePrice(null, 'EUR_USD', (clientPrice) => {
//     console.log(clientPrice);
//     const streamKey = streamKeyPrefix + 'EUR_USD';
  
//     // Use XADD to add data to the stream
//     redis.xadd(streamKey, '*', 'data', JSON.stringify(clientPrice));
//   });
////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////
async function startListening(res, req, currency) {
    console.log('Start listening to currency:', currency);
  
    try {

        const streamKeyPrefix = 'price_stream_';
        client.subscribePrice(null, 'EUR_USD', (clientPrice) => {
            console.log(clientPrice);
            const streamKey = streamKeyPrefix + 'EUR_USD';
        
            // Use XADD to add data to the stream
            redis.xadd(streamKey, '*', 'data', JSON.stringify(clientPrice));
        });
      // Send response to indicate stream listening started
      await res.send(`Stream listening started for currency ${currency}`);
    } catch (error) {
      console.error('Error listening to price stream:', error);
    }
  }
  
  app.get('/start/:currency', async (req, res) => {
    const currency = req.params.currency; // Extract currency pair from request
  
    // Start listening to price stream and save data to Redis
    await startListening(res, req, currency);
  });


app.get('/sub', async (req, res) => {
    client.subscribePrice(null, "EUR_USD", (ClientPrice) => {
        // console.log(ClientPrice);
        console.log(ClientPrice);
    })
});
app.get('/', async (req, res) => {
  res.sendFile(path.join(__dirname, 'file.html'));
});
app.get('/stop', (req, res) => {
  
    // Stop stream listening process for specified currency pair
    client.kill();
    res.send(`all processed stoped!`);
});

app.listen(port, () => {
    console.log(`Server running at http://localhost:${port}/`);
});
