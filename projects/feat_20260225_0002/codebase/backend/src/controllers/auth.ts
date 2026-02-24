import { Request, Response } from 'express';
import bcrypt from 'bcryptjs';
import jwt from 'jsonwebtoken';
import { PrismaClient } from '@prisma/client';
import { z } from 'zod';

const prisma = new PrismaClient();

const loginSchema = z.object({
  email: z.string().email(),
  password: z.string().min(8)
});

const registerSchema = z.object({
  email: z.string().email(),
  password: z.string().min(8)
});

export const AuthController = {
  async register(req: Request, res: Response) {
    try {
      const { email, password } = registerSchema.parse(req.body);
      
      const existingUser = await prisma.user.findUnique({ where: { email } });
      if (existingUser) {
        return res.status(400).json({ error: 'User already exists' });
      }
      
      const hashedPassword = await bcrypt.hash(password, 10);
      const user = await prisma.user.create({
        data: { email, passwordHash: hashedPassword }
      });
      
      const token = jwt.sign(
        { userId: user.id },
        process.env.JWT_SECRET || 'dev-secret',
        { expiresIn: '7d' }
      );
      
      res.json({
        token,
        user: { id: user.id, email: user.email }
      });
    } catch (error) {
      res.status(400).json({ error: 'Invalid input' });
    }
  },
  
  async login(req: Request, res: Response) {
    try {
      const { email, password } = loginSchema.parse(req.body);
      
      const user = await prisma.user.findUnique({ where: { email } });
      if (!user || !await bcrypt.compare(password, user.passwordHash)) {
        return res.status(401).json({ error: 'Invalid credentials' });
      }
      
      const token = jwt.sign(
        { userId: user.id },
        process.env.JWT_SECRET || 'dev-secret',
        { expiresIn: '7d' }
      );
      
      res.json({
        token,
        user: { id: user.id, email: user.email }
      });
    } catch (error) {
      res.status(400).json({ error: 'Invalid input' });
    }
  }
};
