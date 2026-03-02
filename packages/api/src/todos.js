/**
 * In-memory TODO store with CRUD operations.
 * Separated from the Express router to allow unit-testing without HTTP.
 */

let todos = [];
let nextId = 1;

function getAll() {
  return [...todos];
}

function getById(id) {
  return todos.find((t) => t.id === id) || null;
}

function create(title) {
  if (typeof title !== 'string' || title.trim().length === 0) {
    throw new Error('title must be a non-empty string');
  }
  const todo = { id: nextId++, title: title.trim(), completed: false };
  todos.push(todo);
  return todo;
}

function update(id, changes) {
  const todo = getById(id);
  if (!todo) return null;
  if (changes.title !== undefined) {
    if (typeof changes.title !== 'string' || changes.title.trim().length === 0) {
      throw new Error('title must be a non-empty string');
    }
    todo.title = changes.title.trim();
  }
  if (changes.completed !== undefined) {
    todo.completed = Boolean(changes.completed);
  }
  return todo;
}

function remove(id) {
  const index = todos.findIndex((t) => t.id === id);
  if (index === -1) return false;
  todos.splice(index, 1);
  return true;
}

/** Reset state — used only in tests. */
function _reset() {
  todos = [];
  nextId = 1;
}

module.exports = { getAll, getById, create, update, remove, _reset };
