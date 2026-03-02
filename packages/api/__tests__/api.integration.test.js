const request = require('supertest');
const app = require('../src/app');
const todos = require('../src/todos');

beforeEach(() => {
  todos._reset();
});

describe('API integration tests — /todos', () => {
  describe('GET /health', () => {
    it('returns 200 with status ok', async () => {
      const res = await request(app).get('/health');
      expect(res.status).toBe(200);
      expect(res.body).toEqual({ status: 'ok' });
    });
  });

  describe('GET /todos', () => {
    it('returns an empty array initially', async () => {
      const res = await request(app).get('/todos');
      expect(res.status).toBe(200);
      expect(res.body).toEqual([]);
    });

    it('returns all todos after creation', async () => {
      todos.create('Task A');
      todos.create('Task B');
      const res = await request(app).get('/todos');
      expect(res.status).toBe(200);
      expect(res.body).toHaveLength(2);
    });
  });

  describe('POST /todos', () => {
    it('creates a new todo and returns 201', async () => {
      const res = await request(app)
        .post('/todos')
        .send({ title: 'Write tests' });
      expect(res.status).toBe(201);
      expect(res.body).toMatchObject({ title: 'Write tests', completed: false });
      expect(typeof res.body.id).toBe('number');
    });

    it('returns 400 when title is missing', async () => {
      const res = await request(app).post('/todos').send({});
      expect(res.status).toBe(400);
      expect(res.body).toHaveProperty('error');
    });

    it('returns 400 when title is empty', async () => {
      const res = await request(app).post('/todos').send({ title: '' });
      expect(res.status).toBe(400);
    });
  });

  describe('GET /todos/:id', () => {
    it('returns the correct todo by id', async () => {
      const todo = todos.create('Find me');
      const res = await request(app).get(`/todos/${todo.id}`);
      expect(res.status).toBe(200);
      expect(res.body).toMatchObject({ id: todo.id, title: 'Find me' });
    });

    it('returns 404 for a non-existent id', async () => {
      const res = await request(app).get('/todos/999');
      expect(res.status).toBe(404);
    });
  });

  describe('PATCH /todos/:id', () => {
    it('updates a todo title', async () => {
      const todo = todos.create('Old title');
      const res = await request(app)
        .patch(`/todos/${todo.id}`)
        .send({ title: 'New title' });
      expect(res.status).toBe(200);
      expect(res.body.title).toBe('New title');
    });

    it('marks a todo as completed', async () => {
      const todo = todos.create('Finish task');
      const res = await request(app)
        .patch(`/todos/${todo.id}`)
        .send({ completed: true });
      expect(res.status).toBe(200);
      expect(res.body.completed).toBe(true);
    });

    it('returns 404 for a non-existent id', async () => {
      const res = await request(app).patch('/todos/999').send({ title: 'X' });
      expect(res.status).toBe(404);
    });

    it('returns 400 when new title is empty', async () => {
      const todo = todos.create('Valid');
      const res = await request(app)
        .patch(`/todos/${todo.id}`)
        .send({ title: '' });
      expect(res.status).toBe(400);
    });
  });

  describe('DELETE /todos/:id', () => {
    it('deletes a todo and returns 204', async () => {
      const todo = todos.create('Remove me');
      const res = await request(app).delete(`/todos/${todo.id}`);
      expect(res.status).toBe(204);
    });

    it('returns 404 when the todo does not exist', async () => {
      const res = await request(app).delete('/todos/999');
      expect(res.status).toBe(404);
    });
  });
});
