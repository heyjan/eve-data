const express = require('express');
const sqlite3 = require('sqlite3');
const path = require('path');

const app = express();
const dbPath = path.resolve(__dirname, 'eve_killboard.db');
const db = new sqlite3.Database(dbPath);

// Serve static files from the 'public' directory
app.use(express.static(path.join(__dirname, 'public')));

// Endpoint to get total number of kills
app.get('/total-kills', (req, res) => {
    db.get('SELECT COUNT(*) as totalKills FROM killboard', (err, row) => {
        if (err) {
            res.status(500).json({ error: 'Internal Server Error' });
            return console.error(err.message);
        }

        res.json({ totalKills: row.totalKills });
    });
});

// Endpoint to get counts for each ship type
app.get('/ship-type-counts', (req, res) => {
    db.all('SELECT ship_type, COUNT(*) as count FROM killboard GROUP BY ship_type', (err, rows) => {
        if (err) {
            res.status(500).json({ error: 'Internal Server Error' });
            return console.error(err.message);
        }

        res.json(rows);
    });
});

app.get('/top-enemy-corporations', (req, res) => {
    db.all(`
    SELECT enemy_corporation, COUNT(*) as killCount
    FROM killboard
    WHERE enemy_corporation IS NOT NULL
     AND enemy_corporation <> ''
     AND enemy_corporation <> 'Vigilant Tyrannos'
  
    GROUP BY enemy_corporation
    ORDER BY killCount DESC
    LIMIT 10
  `, (err, rows) => {
        if (err) {
            res.status(500).json({ error: 'Internal Server Error' });
            return console.error(err.message);
        }

        res.json(rows);
    });
});

// Endpoint to get activity by days
app.get('/activity-by-days', (req, res) => {
    db.all(`
    SELECT SUBSTR(date, 1, 10) as day, COUNT(*) as activityCount
    FROM killboard
    GROUP BY day
  `, (err, rows) => {
        if (err) {
            res.status(500).json({ error: 'Internal Server Error' });
            return console.error(err.message);
        }

        res.json(rows);
    });
});

// Set the server to listen on port 3000
const PORT = process.env.PORT
app.listen(PORT, () => {
    console.log(`Server is running on http://localhost:${PORT}`);
});
