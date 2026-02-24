# DevForge Pipeline

🚀 **Multi-Agent Software Development Pipeline**

An automated software development system with specialized AI agents:
- 🎯 **PM Agent** - Product Manager (generates specs)
- 👨‍💻 **Dev Agent** - Developer (writes code)
- 🧪 **QA Agent** - Quality Assurance (tests everything)
- 🚀 **Deploy Agent** - DevOps (deploys to any environment)
- 🔍 **Reverse Engineer** - Analyzes existing codebases

Inspired by the [APE (Automated Paper Evaluation)](https://ape.socialcatalystlab.org/) project.

---

## ✨ Features

- **End-to-end automation**: From idea to deployed application
- **Multi-agent collaboration**: Each agent specializes in their domain
- **Quality gates**: Testing at every stage
- **Multiple deployment targets**: Docker, Kubernetes, Vercel, AWS
- **Tournament system**: Compare different implementations
- **TrueSkill ratings**: Rank features by quality

---

### 5. Reverse Engineer Agent (`agents/re/reverse_engineer_agent.py`)

**Purpose:** Analyze existing codebases and extract specifications

**Capabilities:**
- Detects technology stack automatically
- Analyzes architecture patterns (MVC, Component-based, etc.)
- Extracts API endpoints from route files
- Identifies database schema and models
- Generates code metrics (LOC, file counts, complexity)
- Creates architecture diagrams
- Produces reconstructed PM-style specifications

**Usage:**
```bash
# Analyze local codebase
python3 agents/re/reverse_engineer_agent.py /path/to/existing/project

# Analyze GitHub repository
python3 agents/re/reverse_engineer_agent.py https://github.com/user/repo

# Analysis types: quick, full, deep
python3 agents/re/reverse_engineer_agent.py /path/to/project full
```

**Output:**
- `projects/rev_YYYYMMDD_XXXX/analysis.json` - Structured analysis data
- `projects/rev_YYYYMMDD_XXXX/RECONSTRUCTED_SPEC.md` - Human-readable specification

**Example Workflow - Reverse Engineering:**
```bash
# Step 1: Reverse engineer existing codebase
python3 agents/re/reverse_engineer_agent.py https://github.com/example/legacy-app

# Step 2: Use reconstructed spec for new development
REV_ID=$(ls -t projects/ | grep rev_ | head -1)
cp projects/$REV_ID/RECONSTRUCTED_SPEC.md projects/feat_20250225_0001/

# Step 3: Dev agent implements improved version
python3 agents/dev/dev_agent.py feat_20250225_0001
```

---

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    DevForge Pipeline                        │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  🎯 PM AGENT                                                │
│  ├── Analyzes requirements                                  │
│  ├── Generates user stories                                 │
│  ├── Creates API specifications                             │
│  ├── Designs database schema                                │
│  └── Output: feature_spec.json                              │
│                          ↓                                  │
│  👨‍💻 DEV AGENT                                               │
│  ├── Generates backend code (Node.js/Express)              │
│  ├── Generates frontend code (React/Vite)                  │
│  ├── Creates database migrations (Prisma)                  │
│  ├── Generates Docker configuration                        │
│  └── Output: codebase/                                      │
│                          ↓                                  │
│  🧪 QA AGENT                                                │
│  ├── Unit tests (backend + frontend)                       │
│  ├── Integration tests                                     │
│  ├── End-to-end tests                                      │
│  ├── Security tests                                        │
│  ├── Performance tests                                     │
│  └── Output: test_report.json                              │
│                          ↓                                  │
│  🚀 DEPLOY AGENT                                            │
│  ├── Pre-deploy checks                                     │
│  ├── Docker/K8s/AWS/Vercel deployment                      │
│  ├── Post-deploy verification                              │
│  └── Output: deployed application                          │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

---

## 🚀 Quick Start

### 1. Clone and Setup

```bash
git clone https://github.com/MattSureham/devforge-pipeline.git
cd devforge-pipeline
chmod +x devforge.sh
```

### 2. Configure API Keys

```bash
# Edit the configuration file
nano config/.env
```

Add your API keys:
```bash
# AI Model APIs
OPENAI_API_KEY="sk-..."
ANTHROPIC_API_KEY="sk-ant-..."
GEMINI_API_KEY="..."

# Optional: Deployment
DOCKER_USERNAME="..."
AWS_ACCESS_KEY="..."
```

Get API keys:
- [OpenAI](https://platform.openai.com)
- [Anthropic](https://console.anthropic.com)
- [Google AI](https://aistudio.google.com)

### 3. Run Your First Pipeline

```bash
# Interactive mode
./devforge.sh

# Or full pipeline in one command
./devforge.sh full "Task management app" "React, Node.js"
```

---

## 📖 Usage Guide

### Individual Agents

#### PM Agent - Create Feature Specification

```bash
python3 agents/pm/pm_agent.py "Your app idea" "Optional tech stack"

# Example
python3 agents/pm/pm_agent.py "E-commerce platform" "Next.js, PostgreSQL"
```

**Output:**
- `projects/feat_YYYYMMDD_XXXX/feature_spec.json`
- User stories with acceptance criteria
- API specification
- Database schema
- `README.md` with full specification

#### Dev Agent - Generate Code

```bash
python3 agents/dev/dev_agent.py feat_YYYYMMDD_XXXX

# Example
python3 agents/dev/dev_agent.py feat_20250225_0001
```

**Output:**
- `projects/feat_XXXXX/codebase/backend/` - Node.js + Express + TypeScript
- `projects/feat_XXXXX/codebase/frontend/` - React + Vite + TypeScript
- `projects/feat_XXXXX/codebase/docker-compose.yml`
- Complete working application scaffold

#### QA Agent - Test Everything

```bash
python3 agents/qa/qa_agent.py feat_YYYYMMDD_XXXX [test_types...]

# Example - run all tests
python3 agents/qa/qa_agent.py feat_20250225_0001

# Example - specific tests
python3 agents/qa/qa_agent.py feat_20250225_0001 unit integration security
```

**Test Types:**
- `unit` - Unit tests (Jest/Vitest)
- `integration` - API integration tests
- `e2e` - End-to-end tests
- `security` - Security audit
- `performance` - Load testing

**Output:**
- `data/test_results/feat_XXXXX_test_YYYYMMDD_HHMMSS.json`
- Test coverage report
- Security findings
- Performance metrics

#### Deploy Agent - Deploy Application

```bash
python3 agents/deploy/deploy_agent.py feat_YYYYMMDD_XXXX [environment] [platform]

# Examples
python3 agents/deploy/deploy_agent.py feat_20250225_0001 local docker
python3 agents/deploy/deploy_agent.py feat_20250225_0001 staging kubernetes
python3 agents/deploy/deploy_agent.py feat_20250225_0001 production aws
```

**Platforms:**
- `docker` - Docker Compose (local/dev)
- `kubernetes` - K8s manifests (staging/prod)
- `vercel` - Vercel deployment (frontend)
- `aws` - AWS ECS/RDS/S3 (production)

**Environments:**
- `local` - Local Docker
- `staging` - Staging server
- `production` - Production deployment

**Output:**
- `data/deployments/deploy_YYYYMMDD_HHMMSS.json`
- Deployment URLs
- Health check results

---

## 🏆 Tournament System

Compare different implementations:

```bash
# Register features for tournament
python3 scripts/tournament.py register feat_20250225_0001 ai
python3 scripts/tournament.py register feat_20250225_0002 ai

# Run head-to-head match
python3 scripts/tournament.py match feat_20250225_0001 feat_20250225_0002

# View leaderboard
python3 scripts/tournament.py leaderboard
```

Uses [TrueSkill](https://www.microsoft.com/en-us/research/project/trueskill-ranking-system/) Bayesian rating system:
- **μ (mu)** - Estimated skill level
- **σ (sigma)** - Uncertainty
- **Conservative rating** - μ - 3σ

---

## 📁 Project Structure

```
devforge-pipeline/
├── agents/
│   ├── pm/pm_agent.py           # Product Manager Agent
│   ├── dev/dev_agent.py         # Developer Agent
│   ├── qa/qa_agent.py           # QA Agent
│   └── deploy/deploy_agent.py   # Deploy Agent
├── projects/                     # Generated projects
│   └── feat_YYYYMMDD_XXXX/
│       ├── feature_spec.json     # PM specification
│       ├── codebase/             # Generated code
│       │   ├── backend/          # Node.js + Express
│       │   ├── frontend/         # React + Vite
│       │   └── docker-compose.yml
│       └── test_results.json     # QA results
├── data/
│   ├── test_results/             # QA reports
│   ├── deployments/              # Deployment records
│   └── tournament.json           # Tournament data
├── config/
│   └── .env                      # API keys
├── web/
│   └── index.html                # Leaderboard UI
├── devforge.sh                   # Main orchestrator
└── README.md                     # This file
```

---

## 🛠️ Generated Application Stack

### Backend
- **Runtime:** Node.js 20
- **Framework:** Express.js
- **Language:** TypeScript
- **Database:** PostgreSQL + Prisma ORM
- **Auth:** JWT (jsonwebtoken)
- **Validation:** Zod
- **Testing:** Jest + Supertest

### Frontend
- **Framework:** React 18
- **Build Tool:** Vite
- **Language:** TypeScript
- **Routing:** React Router
- **Styling:** Tailwind CSS
- **Testing:** Vitest + React Testing Library

### DevOps
- **Containerization:** Docker + Docker Compose
- **Orchestration:** Kubernetes manifests
- **CI/CD:** GitHub Actions (add your own)

---

## 🔧 Customization

### Change Tech Stack

Edit `agents/dev/dev_agent.py`:
```python
stack = {
    "frontend": {
        "name": "Vue",  # Change from React
        "framework": "Vue 3 + Vite",
    },
    "backend": {
        "name": "Python",  # Change from Node.js
        "framework": "FastAPI",
    }
}
```

### Add Custom Tests

Edit `agents/qa/qa_agent.py`:
```python
def _run_custom_tests(self, codebase_dir):
    return {
        "custom_feature_x": "test_result",
        "custom_feature_y": "test_result"
    }
```

### Change Deployment Target

Edit `agents/deploy/deploy_agent.py`:
```python
# Add new deployment method
def _deploy_gcp(self, feature_id, codebase_dir, environment):
    # Google Cloud deployment logic
    pass
```

---

## 📊 Example Workflow

```bash
# 1. PM creates specification
$ python3 agents/pm/pm_agent.py "Task management app"
🎯 PM Agent: Analyzing feature idea...
✅ PM Agent: Feature feat_20250225_0001 specified
   📋 6 user stories
   ✅ 25 acceptance criteria
   🔧 6 technical requirements

# 2. Developer generates code
$ python3 agents/dev/dev_agent.py feat_20250225_0001
👨‍💻 Dev Agent: Developing feat_20250225_0001
✅ Dev Agent: Development complete
   Stack: React + Node.js
   Backend: 12 files
   Frontend: 8 files

# 3. QA tests everything
$ python3 agents/qa/qa_agent.py feat_20250225_0001
🧪 QA Agent: Testing feat_20250225_0001
✅ QA Agent: Testing complete
   Overall Score: 87.5%
   Tests: 45/50 passed
   Coverage: 82%

# 4. Deploy to production
$ python3 agents/deploy/deploy_agent.py feat_20250225_0001 production docker
🚀 Deploy Agent: Deploying feat_20250225_0001
✅ Deployment complete
   URLs: http://localhost:3000
   Status: healthy
```

---

## 🤝 Contributing

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/amazing`)
3. Commit changes (`git commit -m 'Add amazing feature'`)
4. Push to branch (`git push origin feature/amazing`)
5. Open a Pull Request

---

## 📝 License

MIT License - See [LICENSE](LICENSE)

---

## 🙏 Acknowledgments

Inspired by:
- [APE Project](https://ape.socialcatalystlab.org/) by Social Catalyst Lab
- [OpenClaw](https://github.com/openclaw/openclaw) AI assistant framework
- [TrueSkill](https://www.microsoft.com/en-us/research/project/trueskill-ranking-system/) rating system

---

## 📧 Support

- Create an [issue](https://github.com/MattSureham/devforge-pipeline/issues)
- Check [discussions](https://github.com/MattSureham/devforge-pipeline/discussions)

---

**Happy building!** 🚀
