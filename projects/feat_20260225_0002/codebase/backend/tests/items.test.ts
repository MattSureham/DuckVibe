import request from 'supertest';
import { app } from '../src/server';
import { prisma } from '../src/config/database';

describe('ItemsController', () => {
  let authToken: string;
  let userId: string;

  beforeEach(async () => {
    await prisma.item.deleteMany();
    await prisma.user.deleteMany();
    
    // Register and login
    const registerRes = await request(app)
      .post('/api/v1/auth/register')
      .send({ email: 'test@example.com', password: 'password123' });
    
    authToken = registerRes.body.token;
    userId = registerRes.body.user.id;
  });

  describe('POST /items', () => {
    it('should create item when authenticated', async () => {
      const response = await request(app)
        .post('/api/v1/items')
        .set('Authorization', `Bearer ${authToken}`)
        .send({ title: 'Test Item', content: 'Test content' });
      
      expect(response.status).toBe(200);
      expect(response.body.item.title).toBe('Test Item');
    });

    it('should reject unauthenticated requests', async () => {
      const response = await request(app)
        .post('/api/v1/items')
        .send({ title: 'Test Item', content: 'Test content' });
      
      expect(response.status).toBe(401);
    });
  });

  describe('GET /items', () => {
    it('should return user items', async () => {
      // Create item first
      await request(app)
        .post('/api/v1/items')
        .set('Authorization', `Bearer ${authToken}`)
        .send({ title: 'Test Item', content: 'Test' });
      
      const response = await request(app)
        .get('/api/v1/items')
        .set('Authorization', `Bearer ${authToken}`);
      
      expect(response.status).toBe(200);
      expect(response.body.items).toHaveLength(1);
    });
  });
});
