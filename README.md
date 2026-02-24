> 🦆 If it looks like a duck, swims like a duck, and **codes** like a duck... it's probably **DuckVibe**.
> 
> *"We don't check if our agents are human developers. We just check if they can quack out good code."*

---

# 🦆 DuckVibe

**Vibe-coded software by a squad of duck agents.**

An automated software development system with specialized AI agents:
- 🕷️ **Web Scraper Duck** - Market research and competitor analysis
- 🎯 **PM Duck** - Product Manager (generates specs)
- 🔍 **Reverse Engineer Duck** - Analyzes existing codebases
- 👨‍💻 **Dev Duck** - Developer (writes code)
- 🧪 **QA Duck** - Quality Assurance (tests everything)
- 🚀 **Deploy Duck** - DevOps (deploys to any environment)
- 📜 **Chronicle Duck** - Records all duck interactions

---

## ✨ Features

- **End-to-end automation**: From idea to deployed application
- **Multi-agent collaboration**: 7 ducks working together
- **Multi-agent collaboration**: 7 specialized agents working together
- **Multiple AI providers**: OpenAI, Anthropic, Gemini, Minimax, Moonshot, Ollama (local)
- **Quality gates**: Testing at every stage
- **Multiple deployment targets**: Docker, Kubernetes, Vercel, AWS
- **Tournament system**: Compare different implementations
- **TrueSkill ratings**: Rank features by quality
- **Reverse engineering**: Analyze and rebuild existing codebases

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
# OpenAI (GPT-4, GPT-3.5)
OPENAI_API_KEY="sk-..."

# Anthropic (Claude)
ANTHROPIC_API_KEY="sk-ant-..."

# Google (Gemini)
GEMINI_API_KEY="..."

# Minimax (Chinese LLM)
MINIMAX_API_KEY="..."
MINIMAX_GROUP_ID="..."

# Moonshot AI (Chinese LLM)
MOONSHOT_API_KEY="..."

# Ollama (Local LLM)
OLLAMA_ENABLED="true"
OLLAMA_BASE_URL="http://localhost:11434"
OLLAMA_DEFAULT_MODEL="llama3.2"

# Optional: Deployment
DOCKER_USERNAME="..."
AWS_ACCESS_KEY="..."
```

Get API keys:
- [OpenAI](https://platform.openai.com)
- [Anthropic](https://console.anthropic.com)
- [Google AI](https://aistudio.google.com)
- [Minimax](https://www.minimaxi.com/)
- [Moonshot](https://www.moonshot.cn/)
- [Ollama](https://ollama.com) - Local models

### 3. Configure Agent Models

Assign specific AI models to each agent in `config/.env`:

```bash
# PM Agent uses Claude for best reasoning
PM_AGENT_MODEL="anthropic"
PM_AGENT_MODEL_NAME="claude-3-5-sonnet-20241022"

# Reverse Engineer uses local model for cost efficiency
REVERSE_ENGINEER_MODEL="ollama"
REVERSE_ENGINEER_MODEL_NAME="codellama"

# Dev Agent uses Claude for code generation
DEV_AGENT_MODEL="anthropic"
DEV_AGENT_MODEL_NAME="claude-3-5-sonnet-20241022"

# QA Agent uses GPT-4 for thorough testing
QA_AGENT_MODEL="openai"
QA_AGENT_MODEL_NAME="gpt-4o"

# Deploy Agent uses GPT-4o-mini for speed
DEPLOY_AGENT_MODEL="openai"
DEPLOY_AGENT_MODEL_NAME="gpt-4o-mini"

# Fallback if primary fails
FALLBACK_MODEL="ollama"
FALLBACK_MODEL_NAME="llama3.2"
```

### 4. Run the Pipeline

```bash
# Interactive mode
./devforge.sh

# Full pipeline from idea
./devforge.sh full "Task management app" "React, Node.js"

# Reverse engineer + rebuild
./devforge.sh reverse https://github.com/user/legacy-app

# Unified pipeline command
python3 pipeline.py full "Your app idea"
python3 pipeline.py reverse /path/to/existing/project
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

#### Reverse Engineer Agent - Analyze Existing Code

```bash
python3 agents/re/reverse_engineer_agent.py <source_path>

# Analyze local codebase
python3 agents/re/reverse_engineer_agent.py /path/to/project

# Analyze GitHub repository  
python3 agents/re/reverse_engineer_agent.py https://github.com/user/repo
```

**Output:**
- `projects/rev_YYYYMMDD_XXXX/analysis.json` - Structured analysis
- `projects/rev_YYYYMMDD_XXXX/RECONSTRUCTED_SPEC.md` - Full specification

---

#### Web Scraper Agent - Market Research

```bash
python3 agents/scraper/web_scraper_engineer.py <topic> [depth]

# Quick research
python3 agents/scraper/web_scraper_engineer.py "task management app" quick

# Deep research with competitor analysis
python3 agents/scraper/web_scraper_engineer.py "e-commerce platform" deep
```

**Capabilities:**
- **Competitor Analysis** - Identifies top competitors in the space
- **Trend Detection** - Analyzes social media and forums for trends
- **Pain Point Mining** - Extracts user complaints and feature requests
- **Feature Extraction** - Documents common features across competitors
- **Pricing Intelligence** - Suggests pricing based on market analysis
- **Social Feed Crawling** - Gathers inspiration from Twitter, Reddit, HN

**Output:**
- `data/scraped/research_YYYYMMDD_HHMMSS.json` - Research data
- `data/scraped/research_YYYYMMDD_HHMMSS_inspiration.md` - PM inspiration doc

**Example PM Inspiration Output:**
```markdown
## Competitors Analyzed (6)
- Todoist, Notion, Trello, Asana, ClickUp, Microsoft To Do

## Market Trends
- AI-powered features (+45% growth)
- Mobile-first design (+32% growth)
- Collaborative features (+28% growth)

## User Pain Points
- Too complex / steep learning curve
- Expensive pricing for small teams
- Poor mobile experience

## Differentiation Suggestions
- Simplicity-first approach
- Generous freemium model
- Mobile-native design
```

---

#### Chronicle Agent - Record Everything

The Chronicle Agent automatically records all agent interactions throughout the pipeline:

```bash
# The Chronicle Agent runs automatically with the pipeline
python3 pipeline.py full "Your app idea"

# Or run standalone to review a session
python3 agents/chronicle/chronicle_agent.py demo
```

**What it Records:**
- 🤝 **Handoffs** - When one agent passes work to another
- 💡 **Decisions** - Why agents made specific choices
- ✅ **Actions** - What each agent did
- ⚠️ **Issues** - Problems encountered and resolutions
- 📊 **Metrics** - Performance and timing data

**Output:**
- `data/chronicle/session_YYYYMMDD_HHMMSS_feature_id.json` - Structured event log
- `data/chronicle/session_YYYYMMDD_HHMMSS_feature_id_narrative.md` - Human-readable story

**Example Chronicle Output:**
```
📜 CHRONICLE SUMMARY
   Total events: 47
   Handoffs: 6
   Decisions: 3
   Collaborations: 1

Agent Performance:
- WEB_SCRAPER: 1 actions, 5.2s total
- PM: 1 actions, 8.1s total
- DEV: 1 actions, 45.3s total
- QA: 1 actions, 23.7s total
- DEPLOY: 1 actions, 12.4s total

Handoff Chain:
   web_scraper → pm: market_research_report
   pm → dev: feature_specification
   dev → qa: codebase
   qa → deploy: tested_application
   deploy → user: deployed_application
```

**Why Chronicle Agent?**
- **Transparency**: See exactly how agents collaborate
- **Debugging**: Identify bottlenecks and failures
- **Optimization**: Find ways to improve the pipeline
- **Documentation**: Auto-generate project history
- **Learning**: Understand multi-agent decision-making

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
│   ├── ai_provider.py           # Unified AI provider interface
│   ├── pm/pm_agent.py           # Product Manager Agent
│   ├── re/reverse_engineer_agent.py  # Reverse Engineer Agent
│   ├── scraper/web_scraper_engineer.py  # Web Scraper Agent
│   ├── dev/dev_agent.py         # Developer Agent
│   ├── qa/qa_agent.py           # QA Agent
│   ├── deploy/deploy_agent.py   # Deploy Agent
│   └── chronicle/chronicle_agent.py  # Chronicle Agent (records everything)
├── projects/                     # Generated projects
│   ├── feat_YYYYMMDD_XXXX/      # Feature projects
│   └── rev_YYYYMMDD_XXXX/       # Reverse engineering projects
├── data/
│   ├── scraped/                  # Web scraper research
│   ├── test_results/             # QA reports
│   ├── deployments/              # Deployment records
│   ├── chronicle/                # Chronicle recordings
│   └── tournament.json           # Tournament data
├── config/
│   └── .env                      # API keys
├── web/
│   └── index.html                # Leaderboard UI
├── pipeline.py                   # Unified pipeline orchestrator
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
