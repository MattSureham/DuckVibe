import { Request, Response } from 'express';
import { PrismaClient } from '@prisma/client';
import { z } from 'zod';

const prisma = new PrismaClient();

const itemSchema = z.object({
  title: z.string().min(1).max(255),
  content: z.string().optional(),
  status: z.enum(['active', 'archived']).default('active')
});

export const ItemsController = {
  async list(req: Request, res: Response) {
    try {
      const userId = (req as any).userId;
      const items = await prisma.item.findMany({
        where: { userId },
        orderBy: { createdAt: 'desc' }
      });
      res.json({ items });
    } catch (error) {
      res.status(500).json({ error: 'Failed to fetch items' });
    }
  },
  
  async create(req: Request, res: Response) {
    try {
      const userId = (req as any).userId;
      const data = itemSchema.parse(req.body);
      
      const item = await prisma.item.create({
        data: { ...data, userId }
      });
      
      res.json({ item });
    } catch (error) {
      res.status(400).json({ error: 'Invalid input' });
    }
  },
  
  async get(req: Request, res: Response) {
    try {
      const userId = (req as any).userId;
      const { id } = req.params;
      
      const item = await prisma.item.findFirst({
        where: { id, userId }
      });
      
      if (!item) {
        return res.status(404).json({ error: 'Item not found' });
      }
      
      res.json({ item });
    } catch (error) {
      res.status(500).json({ error: 'Failed to fetch item' });
    }
  },
  
  async update(req: Request, res: Response) {
    try {
      const userId = (req as any).userId;
      const { id } = req.params;
      const data = itemSchema.parse(req.body);
      
      const item = await prisma.item.updateMany({
        where: { id, userId },
        data
      });
      
      if (item.count === 0) {
        return res.status(404).json({ error: 'Item not found' });
      }
      
      res.json({ success: true });
    } catch (error) {
      res.status(400).json({ error: 'Invalid input' });
    }
  },
  
  async delete(req: Request, res: Response) {
    try {
      const userId = (req as any).userId;
      const { id } = req.params;
      
      await prisma.item.deleteMany({
        where: { id, userId }
      });
      
      res.json({ success: true });
    } catch (error) {
      res.status(500).json({ error: 'Failed to delete item' });
    }
  }
};
