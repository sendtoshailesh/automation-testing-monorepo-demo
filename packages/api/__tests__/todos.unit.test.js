const todos = require('../src/todos');

beforeEach(() => {
  todos._reset();
});

describe('todos store — unit tests', () => {
  describe('create()', () => {
    it('creates a todo with the given title', () => {
      const todo = todos.create('Buy milk');
      expect(todo).toEqual({ id: 1, title: 'Buy milk', completed: false });
    });

    it('trims whitespace from title', () => {
      const todo = todos.create('  Walk the dog  ');
      expect(todo.title).toBe('Walk the dog');
    });

    it('auto-increments the id', () => {
      const first = todos.create('Task 1');
      const second = todos.create('Task 2');
      expect(second.id).toBe(first.id + 1);
    });

    it('throws when title is empty', () => {
      expect(() => todos.create('')).toThrow('title must be a non-empty string');
    });

    it('throws when title is whitespace only', () => {
      expect(() => todos.create('   ')).toThrow('title must be a non-empty string');
    });

    it('throws when title is not a string', () => {
      expect(() => todos.create(42)).toThrow('title must be a non-empty string');
    });
  });

  describe('getAll()', () => {
    it('returns an empty array when no todos exist', () => {
      expect(todos.getAll()).toEqual([]);
    });

    it('returns all created todos', () => {
      todos.create('Task A');
      todos.create('Task B');
      const all = todos.getAll();
      expect(all).toHaveLength(2);
      expect(all[0].title).toBe('Task A');
      expect(all[1].title).toBe('Task B');
    });

    it('returns a copy so mutations do not affect the store', () => {
      todos.create('Task A');
      const all = todos.getAll();
      all.push({ id: 99, title: 'Injected', completed: false });
      expect(todos.getAll()).toHaveLength(1);
    });
  });

  describe('getById()', () => {
    it('returns the matching todo', () => {
      const created = todos.create('Find me');
      expect(todos.getById(created.id)).toEqual(created);
    });

    it('returns null when no match is found', () => {
      expect(todos.getById(999)).toBeNull();
    });
  });

  describe('update()', () => {
    it('updates the title', () => {
      const todo = todos.create('Old title');
      const updated = todos.update(todo.id, { title: 'New title' });
      expect(updated.title).toBe('New title');
    });

    it('updates the completed flag', () => {
      const todo = todos.create('Do something');
      const updated = todos.update(todo.id, { completed: true });
      expect(updated.completed).toBe(true);
    });

    it('returns null for a non-existent id', () => {
      expect(todos.update(999, { title: 'X' })).toBeNull();
    });

    it('throws when new title is empty', () => {
      const todo = todos.create('Valid');
      expect(() => todos.update(todo.id, { title: '' })).toThrow(
        'title must be a non-empty string'
      );
    });
  });

  describe('remove()', () => {
    it('removes an existing todo and returns true', () => {
      const todo = todos.create('Delete me');
      expect(todos.remove(todo.id)).toBe(true);
      expect(todos.getById(todo.id)).toBeNull();
    });

    it('returns false when todo does not exist', () => {
      expect(todos.remove(999)).toBe(false);
    });
  });
});
