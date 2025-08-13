// app.js
const path = require('path');
const fs = require('fs');
const express = require('express');
const mongoose = require('mongoose');
const cors = require('cors');

const PORT = parseInt(process.env.PORT, 10) || 3000;
const MONGO_URL = process.env.MONGO_URL || 'mongodb://127.0.0.1:27017/';
const DB_NAME = process.env.MONGO_DBNAME || 'dealershipsDB';
const SEED_ON_START = process.env.SEED_ON_START !== '0';

const app = express();
app.use(cors());
app.use(express.json());
app.use(express.urlencoded({ extended: false }));

// ---------- utilities ----------
function safeReadJSON(relPath, fallback) {
  try {
    const full = path.join(__dirname, relPath);
    return JSON.parse(fs.readFileSync(full, 'utf8'));
  } catch {
    return fallback;
  }
}
function normalizeDealers(raw) {
  if (Array.isArray(raw)) return raw;
  if (raw && Array.isArray(raw.dealerships)) return raw.dealerships;
  return [];
}
function normalizeReviews(raw) {
  if (Array.isArray(raw)) return raw;
  if (raw && Array.isArray(raw.reviews)) return raw.reviews;
  return [];
}
const dealersSeed = normalizeDealers(safeReadJSON('dealerships.json', []));
const reviewsSeed = normalizeReviews(safeReadJSON('reviews.json', []));

const mongoReady = () => mongoose.connection.readyState === 1;

// ---------- models ----------
const Reviews = require('./review');
const Dealerships = require('./dealership');

// ---------- routes ----------
app.get('/', (_req, res) => {
  res.send('Welcome to the Mongoose API');
});

// All reviews
app.get('/fetchReviews', async (_req, res) => {
  try {
    if (!mongoReady()) return res.json(reviewsSeed);
    const docs = await Reviews.find().lean();
    res.json(docs);
  } catch (err) {
    res.status(500).json({ error: 'Error fetching reviews' });
  }
});

// Reviews by dealer id
app.get('/fetchReviews/dealer/:id', async (req, res) => {
  try {
    const dealerId = parseInt(req.params.id, 10);
    if (!mongoReady()) {
      return res.json(reviewsSeed.filter(r => r.dealership === dealerId));
    }
    const docs = await Reviews.find({ dealership: dealerId }).lean();
    res.json(docs);
  } catch (err) {
    res.status(500).json({ error: 'Error fetching reviews by dealer' });
  }
});

// All dealers
app.get('/fetchDealers', async (_req, res) => {
  try {
    if (!mongoReady()) return res.json(dealersSeed);
    const dealers = await Dealerships.find().lean();
    res.json(dealers);
  } catch (err) {
    res.status(500).json({ error: 'Error fetching dealers' });
  }
});

// Dealers by state (case-insensitive exact match)
app.get('/fetchDealers/:state', async (req, res) => {
  try {
    const state = String(req.params.state || '').trim();
    if (!mongoReady()) {
      return res.json(dealersSeed.filter(d => String(d.state).toLowerCase() === state.toLowerCase()));
    }
    const dealers = await Dealerships.find({ state: new RegExp(`^${state}$`, 'i') }).lean();
    res.json(dealers);
  } catch (err) {
    res.status(500).json({ error: 'Error fetching dealers by state' });
  }
});

// Dealer by id
app.get('/fetchDealer/:id', async (req, res) => {
  try {
    const id = parseInt(req.params.id, 10);
    if (!mongoReady()) {
      return res.json(dealersSeed.find(d => d.id === id) || null);
    }
    const dealer = await Dealerships.findOne({ id }).lean();
    res.json(dealer);
  } catch (err) {
    res.status(500).json({ error: 'Error fetching dealer by ID' });
  }
});

// Insert review
app.post('/insert_review', async (req, res) => {
  try {
    if (!mongoReady()) return res.status(503).json({ error: 'Database not connected' });

    const data = typeof req.body === 'string' ? JSON.parse(req.body) : req.body;

    const last = await Reviews.find().sort({ id: -1 }).limit(1).lean();
    const new_id = last.length ? last[0].id + 1 : 1;

    const review = new Reviews({
      id: new_id,
      name: data.name,
      dealership: data.dealership,
      review: data.review,
      purchase: data.purchase,
      purchase_date: data.purchase_date,
      car_make: data.car_make,
      car_model: data.car_model,
      car_year: data.car_year,
    });

    const saved = await review.save();
    res.json(saved);
  } catch (err) {
    console.error(err);
    res.status(500).json({ error: 'Error inserting review' });
  }
});

// Tiny debug/health route
app.get('/_debug/counts', async (_req, res) => {
  const info = { mongoReady: mongoReady() };
  try {
    info.dealers = await Dealerships.countDocuments();
    info.reviews = await Reviews.countDocuments();
  } catch {
    info.dealers = dealersSeed.length;
    info.reviews = reviewsSeed.length;
  }
  res.json(info);
});

(async () => {
  try {
    await mongoose.connect(MONGO_URL, { dbName: DB_NAME });
    console.log('Mongo connected');

    if (SEED_ON_START) {
      if (reviewsSeed.length) {
        await Reviews.deleteMany({});
        await Reviews.insertMany(reviewsSeed);
      }
      if (dealersSeed.length) {
        await Dealerships.deleteMany({});
        await Dealerships.insertMany(dealersSeed);
      }
      console.log('Seeded Mongo collections');
    }

    app.listen(PORT, () => {
      console.log(`Server running on port ${PORT}`);
    });
  } catch (e) {
    console.error('Startup error:', e.message);
    // still start so JSON fallback works
    app.listen(PORT, () => {
      console.log(`Server running (JSON fallback) on port ${PORT}`);
    });
  }
})();
