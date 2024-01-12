const express = require('express');
const app = express();
const fs = require('fs');
const OANDAAdapter = require("oanda-adapter")
const path = require('path');
const redis = require('redis');


const port = 3000;

const redisClient = redis.createClient({
    url: 'redis://:mypassword@redis:6379',
    poolSize: 10,
  connectTimeout: 1000, // ms
  retryInterval: 500, // ms
});

redisClient.on('error', (error) => {
    console.error('Error connecting to Redis:', error);
    process.exit(1); // Terminate the Node.js process
});
const client = new OANDAAdapter({
    // 'live' or 'practice'
    environment: "practice",
    // Generate your API access token in the 'Manage API Access' section of 'My Account' on OANDA's website
    accessToken: "f1d687560e287d40aed90ccb899aad3c-14a9bd4b6b8e9c09f864cd222690f293"
})
redisClient.on('error', (error) => {
    if (error.code === 'ECONNRESET') {
      console.error('Redis connection closed unexpectedly');
    } else {
      console.error('Error adding test data:', error);
    }
  });
  
// Define a route that executes your JavaScript code
app.get('/', (req, res) => {
    // Your JavaScript code goes here
    // const result = yourJavaScriptCode();

    // Send the result as the response
    // res.json(result);
    // res.send(result);
});
let buffer = [];
const streamName = 'my-stream';
const groupName = 'mygroup';
  
// app.get('/start-listening/:currency', (req, res) => {
// const currency = req.params.currency; // Extract currency pair from request
// console.log('start listening to '+ currency);
// // Start stream listening process for specified currency pair
// client.subscribePrice(null, currency, (ClientPrice) => {
//     // Process received stream data
//     buffer.push(ClientPrice);
//     // console.log(buffer);
//     // Periodically save data to Redis
//     if (buffer.length >= 1) {
//     // Convert buffered data to JSON format
//     const encodedData = JSON.stringify(buffer);
//     console.log('saving to redis');
//     // Save data to Redis
//     redisClient.xadd(streamName, '', {
//         message: encodedData
//     });

//     // Clear the buffer after saving to Redis
//     buffer = [];
//     }
// });

// res.send(`Stream listening started for currency ${currency}`);
// });
// Function to subscribe to price stream and save data to Redis
async function startListening(res, req, currency) {
    console.log('Start listening to currency:', currency);
  
    try {
      // Subscribe to price stream and receive stream events
      const subscription = client.subscribePrice(null, currency, async (ClientPrice) => {
        // Process received stream data
        buffer.push(ClientPrice);
  
        // Periodically save data to Redis
        if (buffer.length >= 1) {
          // Convert buffered data to JSON format
          const encodedData = JSON.stringify(buffer);
  
          // Send XADD command to append data to Redis
          await sendXAddCommand(streamName, encodedData);
  
          // Clear the buffer after saving to Redis
          buffer = [];
        }
      });
      
  
      // Send response to indicate stream listening started
      await res.send(`Stream listening started for currency ${currency}`);
    } catch (error) {
      console.error('Error listening to price stream:', error);
    }
  }
  
  app.get('/start-listening/:currency', async (req, res) => {
    const currency = req.params.currency; // Extract currency pair from request
  
    // Start listening to price stream and save data to Redis
    await startListening(res, req, currency);
  });

  async function sendXAddCommand(data) {
    
      // Convert buffered data to JSON format
      const encodedData = JSON.stringify(data);
    
      // Send XADD command to append data to Redis
      await redisClient.set(streamName, 'test');
    
      // Close the Redis connection
      // await redisClient.quit();
    }
  

  app.get('/stop', (req, res) => {
  
    // Stop stream listening process for specified currency pair
    client.kill();
    res.send(`all processed stoped!`);
  });
function getInstrumentsAsync() {
    return new Promise((resolve, reject) => {
        client.getInstruments(null, function (error, data) {
            if (error) {
                reject(error);
            } else {
                resolve(data);
            }
        });
    });
}
function writeToFile(dataToWrite){
    // Data to be written to the file
    const jsonString = JSON.stringify(dataToWrite, null, 2);
    // Specify the file path
        const filePath = 'example.txt';

    // Write data to the file
    //     fs.writeFile(filePath, jsonString, (err) => {
    //         if (err) {
    //             console.error('Error writing to file:', err);
    //         } else {
    //             console.log('Data has been written to the file successfully.');
    //         }
    //     });
    fs.appendFile(filePath, jsonString + '\n', (err) => {
        if (err) {
            console.error('Error appending to file:', err);
        } else {
            console.log('Data has been appended to the file successfully.');
        }
    });
}
app.get('/get', async (req, res) => {
    try {
        const data = await getInstrumentsAsync();
        res.json({ data });
    } catch (error) {
        console.error(error);
        res.status(500).json({ error: 'Internal Server Error' });
    }
});

app.get('/sub', async (req, res) => {
    client.subscribePrice(null, "EUR_USD", (ClientPrice) => {
        // console.log(ClientPrice);
        console.log(ClientPrice);
    })
});


// Start the server
app.listen(port, () => {
    console.log(`Server running at http://localhost:${port}/`);
});


  
  
  
  