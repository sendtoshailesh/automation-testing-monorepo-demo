const express = require('express');
const todos = require('./todos');

const router = express.Router();

// GET /todos — list all todos
router.get('/', (req, res) => {
  res.json(todos.getAll());
});

// GET /todos/:id — get a single todo
router.get('/:id', (req, res) => {
  const id = parseInt(req.params.id, 10);
  const todo = todos.getById(id);
  if (!todo) {
    return res.status(404).json({ error: 'Todo not found' });
  }
  res.json(todo);
});

// POST /todos — create a todo
router.post('/', (req, res) => {
  const { title } = req.body;
  try {
    const todo = todos.create(title);
    res.status(201).json(todo);
  } catch (err) {
    res.status(400).json({ error: err.message });
  }
});

// PATCH /todos/:id — update a todo
router.patch('/:id', (req, res) => {
  const id = parseInt(req.params.id, 10);
  try {
    const todo = todos.update(id, req.body);
    if (!todo) {
      return res.status(404).json({ error: 'Todo not found' });
    }
    res.json(todo);
  } catch (err) {
    res.status(400).json({ error: err.message });
  }
});

// DELETE /todos/:id — delete a todo
router.delete('/:id', (req, res) => {
  const id = parseInt(req.params.id, 10);
  const deleted = todos.remove(id);
  if (!deleted) {
    return res.status(404).json({ error: 'Todo not found' });
  }
  res.status(204).send();
});

module.exports = router;
