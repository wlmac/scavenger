const sqlite3 = require('sqlite3');
const config = require('../config');

const db = new sqlite3.Database(`./data/data_${config.currentGame}.db`, sqlite3.OPEN_READWRITE, (err) => {
    if (err) {
        console.error(err.message);
        process.exit(1);
    }
});

module.exports.dbRun = function (statement, params, type) {
    //type needs to be 'run', 'all', or 'get'
    return new Promise((resolve, reject) => {
        db[type](statement, params, (err, rows) => {
            if (err) {
                console.error(err.message);
                reject(`Error occurred on ${statement}`);
                return;
            }
            if (type === 'run') {
                resolve();
            }
            else {
                resolve(rows);
            }
        })
    });
}