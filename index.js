const express = require("express");
const config = require('./config');
const fs = require('fs');

const app = express();
const PORT = 8080;

var endpoints = {}
fs.readdirSync('./endpoints/').forEach(function (file) {
    let m = require('./endpoints/' + file);
    if (m.name == null || m.execute == null) {
        console.error(`\x1b[31mInvalid endpoint: ${file}\x1b[0m`);
    }
    else if (m.name in endpoints) {
        console.error(`\x1b[31mDuplicate endpoint name: ${file} (${m.name})\x1b[0m`);
    }
    else {
        endpoints[m.name] = m;
        console.log(`Loaded endpoint: ${file} (${m.name})`);
    }
});

app.use(express.urlencoded({ extended: true }));
app.use(express.json({ strict: true }));
app.enable('trust proxy');

if (config.scoreslocked) {
    app.get('/', (req, res) => {
        res.redirect('/leaderboard');
    })
}

app.use(express.static(`static`, { extensions: ['html'] }));
console.log('Set up static directory');

app.use('/api/', (req, res) => {
    const endpoint = req.url.split('?')[0].slice(1);
    if (!endpoints[endpoint]) {
        res.status(404).json({ status: 404, error: 'Unknown endpoint' });
    }
    else {
        try {
            endpoints[endpoint].execute(req, res);
        }
        catch {
            res.status(500).json({ status: 500, error: 'Internal server error' });
        }
    }
})

app.use('/', (req, res) => {
    res.status(404).send('404 not found :('); //replace this with 404 file
})

app.listen(PORT, () => {
    console.log(`Server listening on port ${PORT}`);
});