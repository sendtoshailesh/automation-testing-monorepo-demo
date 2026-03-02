const express = require('express');
const todosRouter = require('./router');

const app = express();

app.use(express.json());
app.use('/todos', todosRouter);

// Health-check endpoint
app.get('/health', (req, res) => {
  res.json({ status: 'ok' });
});

module.exports = app;
