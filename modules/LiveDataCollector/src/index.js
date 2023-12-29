const express = require('express');
const app = express();
const port = 3000;
const fs = require('fs');
const OANDAAdapter = require("oanda-adapter")
const path = require('path');
const client = new OANDAAdapter({
    // 'live' or 'practice'
    environment: "practice",
    // Generate your API access token in the 'Manage API Access' section of 'My Account' on OANDA's website
    accessToken: "f1d687560e287d40aed90ccb899aad3c-14a9bd4b6b8e9c09f864cd222690f293"
})
// Define a route that executes your JavaScript code
app.get('/', (req, res) => {
    // Your JavaScript code goes here
    // const result = yourJavaScriptCode();

    // Send the result as the response
    // res.json(result);
    // res.send(result);
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
        writeToFile(ClientPrice);
    })
});
app.get('/chart', async (req, res) => {
    res.sendFile(path.join(__dirname, 'public', 'index.html'));
    // res.send('hi');
});



// Start the server
app.listen(port, () => {
    console.log(`Server running at http://localhost:${port}/`);
});
