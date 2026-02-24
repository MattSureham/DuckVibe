#!/usr/bin/env python3
"""
DevForge - Developer Agent
Writes code based on PM specifications
"""

import os
import json
import subprocess
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional

class DevAgent:
    """Developer Agent - writes code from specifications"""
    
    def __init__(self, config_path="config/.env"):
        self.config = self._load_config(config_path)
        self.projects_dir = Path("projects")
        self.projects_dir.mkdir(exist_ok=True)
        
    def _load_config(self, path):
        config = {}
        if os.path.exists(path):
            with open(path) as f:
                for line in f:
                    if '=' in line and not line.startswith('#'):
                        key, value = line.strip().split('=', 1)
                        config[key] = value.strip('"')
        for key in ['OPENAI_API_KEY', 'ANTHROPIC_API_KEY']:
            if os.environ.get(key):
                config[key] = os.environ.get(key)
        return config
    
    def develop_feature(self, feature_id: str, tech_preferences: Optional[Dict] = None) -> Dict:
        """
        Develop a feature from PM specification
        
        Args:
            feature_id: Feature to develop (e.g., "feat_20250225_0001")
            tech_preferences: Override tech stack choices
        """
        feature_dir = self.projects_dir / feature_id
        
        if not feature_dir.exists():
            raise FileNotFoundError(f"Feature {feature_id} not found. Run PM agent first.")
        
        # Load feature spec
        with open(feature_dir / "feature_spec.json") as f:
            feature_data = json.load(f)
        
        print(f"👨‍💻 Dev Agent: Developing {feature_id}")
        print(f"   Feature: {feature_data['specification']['title']}")
        
        # Setup project structure
        codebase_dir = feature_dir / "codebase"
        codebase_dir.mkdir(exist_ok=True)
        
        # Generate tech stack (or use preferences)
        stack = self._select_tech_stack(feature_data, tech_preferences)
        
        # Generate backend code
        backend_code = self._generate_backend(feature_data, stack)
        self._save_backend_code(codebase_dir, backend_code, stack)
        
        # Generate frontend code
        frontend_code = self._generate_frontend(feature_data, stack)
        self._save_frontend_code(codebase_dir, frontend_code, stack)
        
        # Generate database migrations
        migrations = self._generate_database_migrations(feature_data, stack)
        self._save_migrations(codebase_dir, migrations, stack)
        
        # Generate configuration files
        config_files = self._generate_config_files(feature_data, stack)
        self._save_config_files(codebase_dir, config_files)
        
        # Generate Docker configuration
        docker_config = self._generate_docker_config(stack)
        self._save_docker_config(codebase_dir, docker_config)
        
        # Create setup instructions
        setup_guide = self._generate_setup_guide(feature_data, stack)
        
        # Update feature status
        feature_data['status'] = 'developed'
        feature_data['development'] = {
            "tech_stack": stack,
            "backend": backend_code,
            "frontend": frontend_code,
            "migrations": migrations,
            "docker": docker_config,
            "setup_guide": setup_guide,
            "developed_at": datetime.now().isoformat(),
            "dev_agent": "v1.0"
        }
        
        with open(feature_dir / "feature_spec.json", 'w') as f:
            json.dump(feature_data, f, indent=2)
        
        # Save setup guide
        with open(codebase_dir / "SETUP.md", 'w') as f:
            f.write(setup_guide)
        
        print(f"✅ Dev Agent: Development complete")
        print(f"   Stack: {stack['frontend']['name']} + {stack['backend']['name']}")
        print(f"   Backend: {len(backend_code)} files")
        print(f"   Frontend: {len(frontend_code)} files")
        print(f"   Database: {len(migrations)} migrations")
        
        return feature_data
    
    def _select_tech_stack(self, feature_data: Dict, preferences: Optional[Dict]) -> Dict:
        """Select or use preferred tech stack"""
        if preferences:
            return preferences
        
        # Default modern stack
        return {
            "frontend": {
                "name": "React",
                "language": "TypeScript",
                "framework": "React 18 + Vite",
                "styling": "Tailwind CSS",
                "state_management": "React Context"
            },
            "backend": {
                "name": "Node.js",
                "language": "TypeScript",
                "framework": "Express.js",
                "runtime": "Node.js 20"
            },
            "database": {
                "name": "PostgreSQL",
                "orm": "Prisma",
                "hosting": "Local/Docker"
            },
            "auth": {
                "method": "JWT",
                "library": "jsonwebtoken"
            },
            "testing": {
                "unit": "Jest",
                "e2e": "Playwright"
            }
        }
    
    def _generate_backend(self, feature_data: Dict, stack: Dict) -> Dict:
        """Generate backend code structure"""
        api_spec = feature_data.get('api_specification', {})
        db_schema = feature_data.get('database_schema', {})
        
        backend = {
            "structure": {
                "src/": {
                    "controllers/": "API controllers",
                    "models/": "Database models",
                    "routes/": "API routes",
                    "middleware/": "Auth, validation middleware",
                    "services/": "Business logic",
                    "utils/": "Helper functions",
                    "config/": "Configuration"
                },
                "tests/": "Test files",
                "prisma/": "Database schema and migrations"
            },
            "files": {}
        }
        
        # Generate package.json
        backend["files"]["package.json"] = json.dumps({
            "name": f"{feature_data['id']}-backend",
            "version": "1.0.0",
            "scripts": {
                "dev": "tsx watch src/server.ts",
                "build": "tsc",
                "start": "node dist/server.js",
                "test": "jest",
                "db:migrate": "prisma migrate dev",
                "db:generate": "prisma generate"
            },
            "dependencies": {
                "express": "^4.18.2",
                "cors": "^2.8.5",
                "helmet": "^7.0.0",
                "bcryptjs": "^2.4.3",
                "jsonwebtoken": "^9.0.2",
                "@prisma/client": "^5.0.0",
                "zod": "^3.22.0",
                "dotenv": "^16.3.0"
            },
            "devDependencies": {
                "@types/express": "^4.17.17",
                "@types/cors": "^2.8.13",
                "@types/bcryptjs": "^2.4.2",
                "@types/jsonwebtoken": "^9.0.2",
                "@types/node": "^20.0.0",
                "typescript": "^5.0.0",
                "tsx": "^3.12.0",
                "jest": "^29.0.0",
                "@types/jest": "^29.0.0",
                "ts-jest": "^29.0.0",
                "prisma": "^5.0.0"
            }
        }, indent=2)
        
        # Generate server.ts
        backend["files"]["src/server.ts"] = '''import express from 'express';
import cors from 'cors';
import helmet from 'helmet';
import dotenv from 'dotenv';
import { authRoutes } from './routes/auth';
import { itemRoutes } from './routes/items';
import { errorHandler } from './middleware/error';

dotenv.config();

const app = express();
const PORT = process.env.PORT || 3001;

// Middleware
app.use(helmet());
app.use(cors());
app.use(express.json());

// Routes
app.use('/api/v1/auth', authRoutes);
app.use('/api/v1/items', itemRoutes);

// Health check
app.get('/health', (req, res) => {
  res.json({ status: 'ok', timestamp: new Date().toISOString() });
});

// Error handling
app.use(errorHandler);

app.listen(PORT, () => {
  console.log(`Server running on port ${PORT}`);
});
'''
        
        # Generate auth controller
        backend["files"]["src/controllers/auth.ts"] = '''import { Request, Response } from 'express';
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
'''
        
        # Generate items controller
        backend["files"]["src/controllers/items.ts"] = '''import { Request, Response } from 'express';
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
'''
        
        # Generate auth middleware
        backend["files"]["src/middleware/auth.ts"] = '''import { Request, Response, NextFunction } from 'express';
import jwt from 'jsonwebtoken';

export const authMiddleware = (req: Request, res: Response, next: NextFunction) => {
  const token = req.headers.authorization?.replace('Bearer ', '');
  
  if (!token) {
    return res.status(401).json({ error: 'No token provided' });
  }
  
  try {
    const decoded = jwt.verify(token, process.env.JWT_SECRET || 'dev-secret') as any;
    (req as any).userId = decoded.userId;
    next();
  } catch (error) {
    res.status(401).json({ error: 'Invalid token' });
  }
};
'''
        
        # Generate routes
        backend["files"]["src/routes/auth.ts"] = '''import { Router } from 'express';
import { AuthController } from '../controllers/auth';

const router = Router();

router.post('/register', AuthController.register);
router.post('/login', AuthController.login);

export { router as authRoutes };
'''
        
        backend["files"]["src/routes/items.ts"] = '''import { Router } from 'express';
import { ItemsController } from '../controllers/items';
import { authMiddleware } from '../middleware/auth';

const router = Router();

router.use(authMiddleware);

router.get('/', ItemsController.list);
router.post('/', ItemsController.create);
router.get('/:id', ItemsController.get);
router.put('/:id', ItemsController.update);
router.delete('/:id', ItemsController.delete);

export { router as itemRoutes };
'''
        
        # Generate error middleware
        backend["files"]["src/middleware/error.ts"] = '''import { Request, Response, NextFunction } from 'express';

export const errorHandler = (
  err: Error,
  req: Request,
  res: Response,
  next: NextFunction
) => {
  console.error(err.stack);
  res.status(500).json({ error: 'Internal server error' });
};
'''
        
        # Generate TypeScript config
        backend["files"]["tsconfig.json"] = json.dumps({
            "compilerOptions": {
                "target": "ES2020",
                "module": "commonjs",
                "lib": ["ES2020"],
                "outDir": "./dist",
                "rootDir": "./src",
                "strict": True,
                "esModuleInterop": True,
                "skipLibCheck": True,
                "forceConsistentCasingInFileNames": True,
                "resolveJsonModule": True,
                "declaration": True,
                "declarationMap": True,
                "sourceMap": True
            },
            "include": ["src/**/*"],
            "exclude": ["node_modules", "dist"]
        }, indent=2)
        
        return backend
    
    def _save_backend_code(self, codebase_dir: Path, backend: Dict, stack: Dict):
        """Save backend code to disk"""
        backend_dir = codebase_dir / "backend"
        backend_dir.mkdir(exist_ok=True)
        
        for file_path, content in backend["files"].items():
            full_path = backend_dir / file_path
            full_path.parent.mkdir(parents=True, exist_ok=True)
            with open(full_path, 'w') as f:
                f.write(content)
    
    def _generate_frontend(self, feature_data: Dict, stack: Dict) -> Dict:
        """Generate frontend code"""
        frontend = {
            "structure": {
                "src/": {
                    "components/": "React components",
                    "pages/": "Page components",
                    "hooks/": "Custom React hooks",
                    "services/": "API services",
                    "types/": "TypeScript types",
                    "utils/": "Helper functions"
                },
                "public/": "Static assets"
            },
            "files": {}
        }
        
        # Generate package.json
        frontend["files"]["package.json"] = json.dumps({
            "name": f"{feature_data['id']}-frontend",
            "private": True,
            "version": "1.0.0",
            "type": "module",
            "scripts": {
                "dev": "vite",
                "build": "tsc && vite build",
                "preview": "vite preview",
                "test": "vitest"
            },
            "dependencies": {
                "react": "^18.2.0",
                "react-dom": "^18.2.0",
                "react-router-dom": "^6.20.0",
                "axios": "^1.6.0"
            },
            "devDependencies": {
                "@types/react": "^18.2.0",
                "@types/react-dom": "^18.2.0",
                "@vitejs/plugin-react": "^4.2.0",
                "autoprefixer": "^10.4.0",
                "postcss": "^8.4.0",
                "tailwindcss": "^3.3.0",
                "typescript": "^5.0.0",
                "vite": "^5.0.0",
                "vitest": "^1.0.0"
            }
        }, indent=2)
        
        # Generate main App component
        frontend["files"]["src/App.tsx"] = '''import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import { AuthProvider } from './contexts/AuthContext';
import { Layout } from './components/Layout';
import { Home } from './pages/Home';
import { Login } from './pages/Login';
import { Register } from './pages/Register';
import { Dashboard } from './pages/Dashboard';
import { ProtectedRoute } from './components/ProtectedRoute';

function App() {
  return (
    <AuthProvider>
      <Router>
        <Layout>
          <Routes>
            <Route path="/" element={<Home />} />
            <Route path="/login" element={<Login />} />
            <Route path="/register" element={<Register />} />
            <Route path="/dashboard" element={
              <ProtectedRoute>
                <Dashboard />
              </ProtectedRoute>
            } />
          </Routes>
        </Layout>
      </Router>
    </AuthProvider>
  );
}

export default App;
'''
        
        # Generate auth context
        frontend["files"]["src/contexts/AuthContext.tsx"] = '''import React, { createContext, useContext, useState, useEffect } from 'react';
import { authService } from '../services/auth';

interface User {
  id: string;
  email: string;
}

interface AuthContextType {
  user: User | null;
  login: (email: string, password: string) => Promise<void>;
  register: (email: string, password: string) => Promise<void>;
  logout: () => void;
  loading: boolean;
}

const AuthContext = createContext<AuthContextType | undefined>(undefined);

export const AuthProvider: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  const [user, setUser] = useState<User | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const token = localStorage.getItem('token');
    if (token) {
      // Verify token and set user
      setLoading(false);
    } else {
      setLoading(false);
    }
  }, []);

  const login = async (email: string, password: string) => {
    const response = await authService.login(email, password);
    localStorage.setItem('token', response.token);
    setUser(response.user);
  };

  const register = async (email: string, password: string) => {
    const response = await authService.register(email, password);
    localStorage.setItem('token', response.token);
    setUser(response.user);
  };

  const logout = () => {
    localStorage.removeItem('token');
    setUser(null);
  };

  return (
    <AuthContext.Provider value={{ user, login, register, logout, loading }}>
      {children}
    </AuthContext.Provider>
  );
};

export const useAuth = () => {
  const context = useContext(AuthContext);
  if (!context) throw new Error('useAuth must be used within AuthProvider');
  return context;
};
'''
        
        # Generate auth service
        frontend["files"]["src/services/auth.ts"] = '''import axios from 'axios';

const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:3001/api/v1';

const api = axios.create({
  baseURL: API_URL,
});

api.interceptors.request.use((config) => {
  const token = localStorage.getItem('token');
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

export const authService = {
  async login(email: string, password: string) {
    const response = await api.post('/auth/login', { email, password });
    return response.data;
  },
  
  async register(email: string, password: string) {
    const response = await api.post('/auth/register', { email, password });
    return response.data;
  }
};

export { api };
'''
        
        # Generate pages
        frontend["files"]["src/pages/Login.tsx"] = '''import { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { useAuth } from '../contexts/AuthContext';

export const Login = () => {
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [error, setError] = useState('');
  const { login } = useAuth();
  const navigate = useNavigate();

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    try {
      await login(email, password);
      navigate('/dashboard');
    } catch (err) {
      setError('Invalid credentials');
    }
  };

  return (
    <div className="min-h-screen flex items-center justify-center bg-gray-50">
      <div className="max-w-md w-full space-y-8 p-8 bg-white rounded-lg shadow">
        <h2 className="text-3xl font-bold text-center">Sign In</h2>
        {error && <p className="text-red-500 text-center">{error}</p>}
        <form onSubmit={handleSubmit} className="space-y-6">
          <div>
            <label className="block text-sm font-medium text-gray-700">Email</label>
            <input
              type="email"
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              className="mt-1 block w-full px-3 py-2 border border-gray-300 rounded-md"
              required
            />
          </div>
          <div>
            <label className="block text-sm font-medium text-gray-700">Password</label>
            <input
              type="password"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              className="mt-1 block w-full px-3 py-2 border border-gray-300 rounded-md"
              required
            />
          </div>
          <button
            type="submit"
            className="w-full py-2 px-4 bg-blue-600 text-white rounded-md hover:bg-blue-700"
          >
            Sign In
          </button>
        </form>
      </div>
    </div>
  );
};
'''
        
        return frontend
    
    def _save_frontend_code(self, codebase_dir: Path, frontend: Dict, stack: Dict):
        """Save frontend code to disk"""
        frontend_dir = codebase_dir / "frontend"
        frontend_dir.mkdir(exist_ok=True)
        
        for file_path, content in frontend["files"].items():
            full_path = frontend_dir / file_path
            full_path.parent.mkdir(parents=True, exist_ok=True)
            with open(full_path, 'w') as f:
                f.write(content)
    
    def _generate_database_migrations(self, feature_data: Dict, stack: Dict) -> List[Dict]:
        """Generate database migrations"""
        migrations = []
        
        # Prisma schema
        migrations.append({
            "name": "schema.prisma",
            "content": '''generator client {
  provider = "prisma-client-js"
}

datasource db {
  provider = "postgresql"
  url      = env("DATABASE_URL")
}

model User {
  id            String   @id @default(uuid())
  email         String   @unique
  passwordHash  String
  createdAt     DateTime @default(now())
  updatedAt     DateTime @updatedAt
  items         Item[]
}

model Item {
  id        String   @id @default(uuid())
  userId    String
  user      User     @relation(fields: [userId], references: [id])
  title     String
  content   String?
  status    String   @default("active")
  createdAt DateTime @default(now())
  updatedAt DateTime @updatedAt
}
'''
        })
        
        # Initial migration SQL
        migrations.append({
            "name": "migrations/20240101000000_init/migration.sql",
            "content": '''-- CreateTable
CREATE TABLE "User" (
    "id" TEXT NOT NULL,
    "email" TEXT NOT NULL,
    "passwordHash" TEXT NOT NULL,
    "createdAt" TIMESTAMP(3) NOT NULL DEFAULT CURRENT_TIMESTAMP,
    "updatedAt" TIMESTAMP(3) NOT NULL,

    CONSTRAINT "User_pkey" PRIMARY KEY ("id")
);

-- CreateTable
CREATE TABLE "Item" (
    "id" TEXT NOT NULL,
    "userId" TEXT NOT NULL,
    "title" TEXT NOT NULL,
    "content" TEXT,
    "status" TEXT NOT NULL DEFAULT 'active',
    "createdAt" TIMESTAMP(3) NOT NULL DEFAULT CURRENT_TIMESTAMP,
    "updatedAt" TIMESTAMP(3) NOT NULL,

    CONSTRAINT "Item_pkey" PRIMARY KEY ("id")
);

-- CreateIndex
CREATE UNIQUE INDEX "User_email_key" ON "User"("email");

-- AddForeignKey
ALTER TABLE "Item" ADD CONSTRAINT "Item_userId_fkey" FOREIGN KEY ("userId") REFERENCES "User"("id") ON DELETE RESTRICT ON UPDATE CASCADE;
'''
        })
        
        return migrations
    
    def _save_migrations(self, codebase_dir: Path, migrations: List[Dict], stack: Dict):
        """Save database migrations"""
        backend_dir = codebase_dir / "backend"
        prisma_dir = backend_dir / "prisma"
        prisma_dir.mkdir(exist_ok=True)
        
        for migration in migrations:
            if migration["name"].startswith("migrations/"):
                parts = migration["name"].split("/")
                mig_dir = prisma_dir / "/".join(parts[:-1])
                mig_dir.mkdir(parents=True, exist_ok=True)
                with open(mig_dir / parts[-1], 'w') as f:
                    f.write(migration["content"])
            else:
                with open(prisma_dir / migration["name"], 'w') as f:
                    f.write(migration["content"])
    
    def _generate_config_files(self, feature_data: Dict, stack: Dict) -> Dict:
        """Generate configuration files"""
        return {
            ".env.example": '''# Backend
PORT=3001
DATABASE_URL="postgresql://user:password@localhost:5432/dbname"
JWT_SECRET="your-secret-key-here"

# Frontend
VITE_API_URL=http://localhost:3001/api/v1
''',
            ".gitignore": '''# Dependencies
node_modules/

# Build
dist/
build/

# Environment
.env
.env.local

# IDE
.vscode/
.idea/

# OS
.DS_Store
'''
        }
    
    def _save_config_files(self, codebase_dir: Path, configs: Dict):
        """Save configuration files"""
        for name, content in configs.items():
            with open(codebase_dir / name, 'w') as f:
                f.write(content)
    
    def _generate_docker_config(self, stack: Dict) -> Dict:
        """Generate Docker configuration"""
        return {
            "docker-compose.yml": '''version: '3.8'

services:
  postgres:
    image: postgres:15-alpine
    environment:
      POSTGRES_USER: devforge
      POSTGRES_PASSWORD: devforge
      POSTGRES_DB: devforge
    ports:
      - "5432:5432"
    volumes:
      - postgres_data:/var/lib/postgresql/data

  backend:
    build: ./backend
    ports:
      - "3001:3001"
    environment:
      - DATABASE_URL=postgresql://devforge:devforge@postgres:5432/devforge
      - JWT_SECRET=dev-secret-change-in-production
    depends_on:
      - postgres
    volumes:
      - ./backend:/app
      - /app/node_modules

  frontend:
    build: ./frontend
    ports:
      - "3000:3000"
    environment:
      - VITE_API_URL=http://localhost:3001/api/v1
    volumes:
      - ./frontend:/app
      - /app/node_modules

volumes:
  postgres_data:
''',
            "backend/Dockerfile": '''FROM node:20-alpine

WORKDIR /app

COPY package*.json ./
RUN npm install

COPY . .
RUN npx prisma generate

EXPOSE 3001

CMD ["npm", "run", "dev"]
''',
            "frontend/Dockerfile": '''FROM node:20-alpine

WORKDIR /app

COPY package*.json ./
RUN npm install

COPY . .

EXPOSE 3000

CMD ["npm", "run", "dev"]
'''
        }
    
    def _save_docker_config(self, codebase_dir: Path, docker_config: Dict):
        """Save Docker configuration"""
        # Main docker-compose
        with open(codebase_dir / "docker-compose.yml", 'w') as f:
            f.write(docker_config["docker-compose.yml"])
        
        # Backend Dockerfile
        backend_dir = codebase_dir / "backend"
        with open(backend_dir / "Dockerfile", 'w') as f:
            f.write(docker_config["backend/Dockerfile"])
        
        # Frontend Dockerfile
        frontend_dir = codebase_dir / "frontend"
        with open(frontend_dir / "Dockerfile", 'w') as f:
            f.write(docker_config["frontend/Dockerfile"])
    
    def _generate_setup_guide(self, feature_data: Dict, stack: Dict) -> str:
        """Generate setup instructions"""
        return f'''# Setup Guide

## Prerequisites

- Node.js 20+
- PostgreSQL 15+
- Docker (optional)

## Quick Start

### Option 1: Docker (Recommended)

```bash
# Start all services
docker-compose up -d

# Run migrations
cd backend
npx prisma migrate dev

# Access
# Frontend: http://localhost:3000
# Backend API: http://localhost:3001
# Database: localhost:5432
```

### Option 2: Local Development

**1. Database**
```bash
# Start PostgreSQL
# Create database named 'devforge'
```

**2. Backend**
```bash
cd backend
cp .env.example .env
# Edit .env with your database URL
npm install
npx prisma migrate dev
npm run dev
```

**3. Frontend**
```bash
cd frontend
cp .env.example .env
npm install
npm run dev
```

## Development Workflow

1. **Start backend**: `npm run dev` (port 3001)
2. **Start frontend**: `npm run dev` (port 3000)
3. **Run tests**: `npm test`
4. **Database changes**: `npx prisma migrate dev`

## Project Structure

```
codebase/
├── backend/          # Node.js + Express + TypeScript
│   ├── src/
│   │   ├── controllers/   # API controllers
│   │   ├── routes/        # API routes
│   │   ├── middleware/    # Auth, error handling
│   │   └── ...
│   └── prisma/       # Database schema
├── frontend/         # React + TypeScript + Vite
│   └── src/
│       ├── components/    # React components
│       ├── pages/         # Page components
│       ├── contexts/      # React contexts
│       └── services/      # API services
└── docker-compose.yml
```

## API Endpoints

- `POST /api/v1/auth/register` - Register new user
- `POST /api/v1/auth/login` - User login
- `GET /api/v1/items` - List items
- `POST /api/v1/items` - Create item
- `GET /api/v1/items/:id` - Get item
- `PUT /api/v1/items/:id` - Update item
- `DELETE /api/v1/items/:id` - Delete item

## Next Steps

1. Customize UI components in `frontend/src/components/`
2. Add business logic in `backend/src/services/`
3. Write tests in `backend/tests/` and `frontend/src/__tests__/`
4. Deploy using Docker or cloud platform

Generated by DevForge Pipeline
Feature: {feature_data['id']}
Stack: {stack['frontend']['name']} + {stack['backend']['name']}
'''

if __name__ == "__main__":
    import sys
    
    if len(sys.argv) < 2:
        print("Usage: python3 dev_agent.py <feature_id>")
        print("Example: python3 dev_agent.py feat_20250225_0001")
        sys.exit(1)
    
    dev = DevAgent()
    feature = dev.develop_feature(sys.argv[1])
    
    print(f"\n📁 Codebase saved to: projects/{feature['id']}/codebase/")
    print(f"📄 Setup guide: projects/{feature['id']}/codebase/SETUP.md")
