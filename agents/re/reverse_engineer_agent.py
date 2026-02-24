#!/usr/bin/env python3
"""
DevForge - Reverse Engineer Agent
Analyzes existing codebases and extracts specifications
"""

import os
import json
import re
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Set
import subprocess

class ReverseEngineerAgent:
    """Reverse Engineer Agent - analyzes code and extracts specs"""
    
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
    
    def analyze_codebase(self, source_path: str, analysis_type: str = "full") -> Dict:
        """
        Analyze an existing codebase and extract specifications
        
        Args:
            source_path: Path to existing codebase (local dir or GitHub URL)
            analysis_type: "quick", "full", or "deep"
        """
        source = Path(source_path)
        
        if not source.exists():
            # Try to clone if it's a URL
            if source_path.startswith(('http://', 'https://', 'git@')):
                source = self._clone_repository(source_path)
            else:
                raise FileNotFoundError(f"Source not found: {source_path}")
        
        feature_id = self._generate_feature_id()
        analysis_dir = self.projects_dir / feature_id
        analysis_dir.mkdir(exist_ok=True)
        
        print(f"🔍 Reverse Engineer: Analyzing {source_path}")
        print(f"   Analysis type: {analysis_type}")
        
        # Perform analysis
        tech_stack = self._detect_tech_stack(source)
        architecture = self._analyze_architecture(source, tech_stack)
        api_endpoints = self._extract_api_endpoints(source, tech_stack)
        database_schema = self._extract_database_schema(source, tech_stack)
        dependencies = self._analyze_dependencies(source, tech_stack)
        code_metrics = self._calculate_metrics(source)
        
        # Generate reconstructed specification
        spec = self._reconstruct_specification(
            source, tech_stack, architecture, api_endpoints, 
            database_schema, dependencies, code_metrics
        )
        
        # Generate documentation
        docs = self._generate_documentation(source, spec, tech_stack)
        
        # Create architecture diagrams (text-based)
        diagrams = self._create_architecture_diagrams(architecture, tech_stack)
        
        # Save analysis
        analysis_data = {
            "id": feature_id,
            "source_path": str(source_path),
            "analysis_type": analysis_type,
            "tech_stack": tech_stack,
            "architecture": architecture,
            "api_endpoints": api_endpoints,
            "database_schema": database_schema,
            "dependencies": dependencies,
            "code_metrics": code_metrics,
            "reconstructed_spec": spec,
            "documentation": docs,
            "diagrams": diagrams,
            "status": "analyzed",
            "analyzed_at": datetime.now().isoformat(),
            "reverse_engineer_agent": "v1.0"
        }
        
        self._save_analysis(analysis_dir, analysis_data)
        
        print(f"✅ Reverse Engineer: Analysis complete")
        print(f"   Tech Stack: {tech_stack.get('primary_language', 'Unknown')}")
        print(f"   Files Analyzed: {code_metrics.get('total_files', 0)}")
        print(f"   LOC: {code_metrics.get('lines_of_code', 0):,}")
        print(f"   API Endpoints: {len(api_endpoints)}")
        
        return analysis_data
    
    def _clone_repository(self, url: str) -> Path:
        """Clone a Git repository"""
        clone_dir = self.projects_dir / "cloned" / Path(url).stem
        clone_dir.parent.mkdir(parents=True, exist_ok=True)
        
        print(f"   Cloning {url}...")
        subprocess.run(
            ["git", "clone", "--depth", "1", url, str(clone_dir)],
            capture_output=True,
            check=True
        )
        
        return clone_dir
    
    def _generate_feature_id(self):
        """Generate unique analysis ID"""
        timestamp = datetime.now().strftime("%Y%m%d")
        existing = len(list(self.projects_dir.glob("rev_*")))
        return f"rev_{timestamp}_{existing + 1:04d}"
    
    def _detect_tech_stack(self, source: Path) -> Dict:
        """Detect the technology stack used"""
        stack = {
            "primary_language": None,
            "framework": None,
            "frontend": {},
            "backend": {},
            "database": None,
            "deployment": {}
        }
        
        # Check for package.json (Node.js)
        if (source / "package.json").exists():
            with open(source / "package.json") as f:
                pkg = json.load(f)
                deps = {**pkg.get("dependencies", {}), **pkg.get("devDependencies", {})}
                
                stack["primary_language"] = "JavaScript/TypeScript"
                
                # Detect framework
                if "react" in deps:
                    stack["frontend"]["framework"] = "React"
                if "vue" in deps:
                    stack["frontend"]["framework"] = "Vue"
                if "express" in deps:
                    stack["backend"]["framework"] = "Express"
                if "next" in deps:
                    stack["framework"] = "Next.js"
                
                # Detect testing
                if "jest" in deps:
                    stack["testing"] = "Jest"
                if "vitest" in deps:
                    stack["testing"] = "Vitest"
        
        # Check for Python
        if (source / "requirements.txt").exists() or (source / "pyproject.toml").exists():
            stack["primary_language"] = "Python"
            
            if (source / "requirements.txt").exists():
                with open(source / "requirements.txt") as f:
                    reqs = f.read()
                    if "django" in reqs.lower():
                        stack["backend"]["framework"] = "Django"
                    if "flask" in reqs.lower():
                        stack["backend"]["framework"] = "Flask"
                    if "fastapi" in reqs.lower():
                        stack["backend"]["framework"] = "FastAPI"
        
        # Check for Docker
        if (source / "Dockerfile").exists() or (source / "docker-compose.yml").exists():
            stack["deployment"]["containerization"] = "Docker"
        
        # Check for database
        if (source / "prisma").exists():
            stack["database"] = "Prisma ORM"
        elif (source / "migrations").exists():
            stack["database"] = "SQL-based"
        
        # Detect language from file extensions
        file_counts = {}
        for ext in ['.js', '.ts', '.jsx', '.tsx', '.py', '.go', '.rs', '.java']:
            count = len(list(source.rglob(f"*{ext}")))
            if count > 0:
                file_counts[ext] = count
        
        if file_counts:
            primary_ext = max(file_counts, key=file_counts.get)
            lang_map = {
                '.js': 'JavaScript', '.ts': 'TypeScript', '.jsx': 'React',
                '.tsx': 'React/TypeScript', '.py': 'Python', '.go': 'Go',
                '.rs': 'Rust', '.java': 'Java'
            }
            if not stack["primary_language"]:
                stack["primary_language"] = lang_map.get(primary_ext, 'Unknown')
        
        return stack
    
    def _analyze_architecture(self, source: Path, tech_stack: Dict) -> Dict:
        """Analyze the architecture patterns used"""
        architecture = {
            "pattern": "Unknown",
            "layers": [],
            "components": [],
            "entry_points": []
        }
        
        # Look for common patterns
        structure = {
            "has_src": (source / "src").exists(),
            "has_controllers": len(list(source.rglob("*controller*"))) > 0,
            "has_models": len(list(source.rglob("*model*"))) > 0,
            "has_services": len(list(source.rglob("*service*"))) > 0,
            "has_components": len(list(source.rglob("*component*"))) > 0,
            "has_routes": len(list(source.rglob("*route*"))) > 0,
        }
        
        # Detect MVC/MVVM/MVP
        if structure["has_models"] and structure["has_controllers"]:
            architecture["pattern"] = "MVC"
            architecture["layers"] = ["Model", "View", "Controller"]
        elif structure["has_components"] and structure["has_services"]:
            architecture["pattern"] = "Component-Based"
            architecture["layers"] = ["Components", "Services", "Data Layer"]
        
        # Find entry points
        entry_files = ["index.js", "main.js", "app.js", "server.js", "main.py", "app.py"]
        for entry in entry_files:
            if (source / entry).exists():
                architecture["entry_points"].append(entry)
            elif (source / "src" / entry).exists():
                architecture["entry_points"].append(f"src/{entry}")
        
        # Detect components
        if structure["has_components"]:
            comp_files = list(source.rglob("*component*"))[:10]
            architecture["components"] = [f.name for f in comp_files]
        
        return architecture
    
    def _extract_api_endpoints(self, source: Path, tech_stack: Dict) -> List[Dict]:
        """Extract API endpoints from the codebase"""
        endpoints = []
        
        # Look for Express routes
        route_files = list(source.rglob("*route*")) + list(source.rglob("*Route*"))
        
        for route_file in route_files:
            if route_file.suffix in ['.js', '.ts']:
                try:
                    with open(route_file) as f:
                        content = f.read()
                        
                        # Simple regex to find Express routes
                        route_patterns = [
                            r"(router\.|app\.)?(get|post|put|delete|patch)\s*\(\s*['\"]([^'\"]+)['\"]",
                            r"@(\w+)\s*\(\s*['\"]([^'\"]+)['\"]"  # Decorator style
                        ]
                        
                        for pattern in route_patterns:
                            matches = re.findall(pattern, content)
                            for match in matches:
                                if len(match) >= 2:
                                    method = match[-2] if isinstance(match[-2], str) else "GET"
                                    path = match[-1]
                                    
                                    endpoints.append({
                                        "method": method.upper(),
                                        "path": path,
                                        "source_file": str(route_file.relative_to(source)),
                                        "inferred": True
                                    })
                except:
                    pass
        
        # Remove duplicates
        seen = set()
        unique_endpoints = []
        for ep in endpoints:
            key = f"{ep['method']} {ep['path']}"
            if key not in seen:
                seen.add(key)
                unique_endpoints.append(ep)
        
        return unique_endpoints[:20]  # Limit to 20 endpoints
    
    def _extract_database_schema(self, source: Path, tech_stack: Dict) -> Dict:
        """Extract database schema from the codebase"""
        schema = {
            "type": "Unknown",
            "tables": [],
            "models": []
        }
        
        # Check for Prisma schema
        prisma_schema = source / "prisma" / "schema.prisma"
        if prisma_schema.exists():
            schema["type"] = "Prisma"
            try:
                with open(prisma_schema) as f:
                    content = f.read()
                    # Extract model names
                    models = re.findall(r"model\s+(\w+)\s*{", content)
                    schema["models"] = models
            except:
                pass
        
        # Check for SQL migrations
        migrations_dir = source / "migrations"
        if migrations_dir.exists():
            schema["type"] = "SQL Migrations"
            migration_files = list(migrations_dir.glob("*.sql"))[:5]
            for mig_file in migration_files:
                try:
                    with open(mig_file) as f:
                        content = f.read()
                        tables = re.findall(r"CREATE TABLE\s+(?:IF NOT EXISTS\s+)?(\w+)", content, re.IGNORECASE)
                        schema["tables"].extend(tables)
                except:
                    pass
            schema["tables"] = list(set(schema["tables"]))[:10]
        
        # Check for model files
        model_files = list(source.rglob("*model*"))
        if model_files and not schema["models"]:
            schema["type"] = "Code Models"
            schema["models"] = [f.stem for f in model_files[:10]]
        
        return schema
    
    def _analyze_dependencies(self, source: Path, tech_stack: Dict) -> Dict:
        """Analyze project dependencies"""
        deps = {
            "production": [],
            "development": [],
            "total_count": 0
        }
        
        # Node.js dependencies
        pkg_file = source / "package.json"
        if pkg_file.exists():
            with open(pkg_file) as f:
                pkg = json.load(f)
                prod_deps = list(pkg.get("dependencies", {}).keys())
                dev_deps = list(pkg.get("devDependencies", {}).keys())
                
                deps["production"] = prod_deps[:20]
                deps["development"] = dev_deps[:20]
                deps["total_count"] = len(prod_deps) + len(dev_deps)
                
                # Identify key dependencies
                deps["key_dependencies"] = []
                for dep in prod_deps[:10]:
                    if dep in ['react', 'vue', 'express', 'next', 'nestjs']:
                        deps["key_dependencies"].append(dep)
        
        # Python dependencies
        req_file = source / "requirements.txt"
        if req_file.exists():
            with open(req_file) as f:
                py_deps = [line.strip() for line in f if line.strip() and not line.startswith('#')]
                deps["production"] = py_deps[:20]
                deps["total_count"] = len(py_deps)
        
        return deps
    
    def _calculate_metrics(self, source: Path) -> Dict:
        """Calculate code metrics"""
        metrics = {
            "total_files": 0,
            "lines_of_code": 0,
            "blank_lines": 0,
            "comment_lines": 0,
            "file_types": {}
        }
        
        code_extensions = {'.js', '.ts', '.jsx', '.tsx', '.py', '.go', '.rs', '.java', '.rb', '.php', '.swift', '.kt'}
        
        for file_path in source.rglob("*"):
            if file_path.is_file() and file_path.suffix in code_extensions:
                # Skip node_modules and similar
                if any(part.startswith('.') or part in ['node_modules', 'venv', '__pycache__'] 
                       for part in file_path.parts):
                    continue
                
                metrics["total_files"] += 1
                metrics["file_types"][file_path.suffix] = metrics["file_types"].get(file_path.suffix, 0) + 1
                
                try:
                    with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                        for line in f:
                            metrics["lines_of_code"] += 1
                            stripped = line.strip()
                            if not stripped:
                                metrics["blank_lines"] += 1
                            elif stripped.startswith(('#', '//', '/*', '*')):
                                metrics["comment_lines"] += 1
                except:
                    pass
        
        return metrics
    
    def _reconstruct_specification(self, source: Path, tech_stack: Dict, 
                                   architecture: Dict, api_endpoints: List[Dict],
                                   database_schema: Dict, dependencies: Dict,
                                   code_metrics: Dict) -> Dict:
        """Reconstruct PM-style specification from analysis"""
        
        # Infer purpose from directory name and structure
        purpose = source.name.replace('-', ' ').replace('_', ' ').title()
        
        spec = {
            "title": purpose,
            "description": f"A {tech_stack.get('primary_language', 'software')} application using {architecture.get('pattern', 'standard')} architecture",
            "purpose": f"Based on analysis of {code_metrics.get('total_files', 0)} files with {code_metrics.get('lines_of_code', 0):,} lines of code",
            "tech_stack_summary": tech_stack,
            "architecture_pattern": architecture.get("pattern"),
            "entry_points": architecture.get("entry_points", []),
            "inferred_features": self._infer_features(source, api_endpoints, database_schema),
            "api_summary": {
                "total_endpoints": len(api_endpoints),
                "endpoints_by_method": {}
            },
            "database_summary": database_schema,
            "reconstruction_confidence": "medium"
        }
        
        # Count endpoints by method
        for ep in api_endpoints:
            method = ep.get("method", "UNKNOWN")
            spec["api_summary"]["endpoints_by_method"][method] = \
                spec["api_summary"]["endpoints_by_method"].get(method, 0) + 1
        
        return spec
    
    def _infer_features(self, source: Path, api_endpoints: List[Dict], database_schema: Dict) -> List[str]:
        """Infer features from code structure"""
        features = []
        
        # Infer from API endpoints
        endpoint_paths = [ep.get("path", "") for ep in api_endpoints]
        
        if any("auth" in p or "login" in p for p in endpoint_paths):
            features.append("User authentication system")
        
        if any("user" in p for p in endpoint_paths):
            features.append("User management")
        
        if any(p.startswith("/api/") for p in endpoint_paths):
            features.append("RESTful API")
        
        # Infer from database
        if database_schema.get("models"):
            for model in database_schema["models"][:3]:
                features.append(f"{model} data management")
        
        # Default features
        if not features:
            features = ["Data management", "API endpoints", "Business logic"]
        
        return features
    
    def _generate_documentation(self, source: Path, spec: Dict, tech_stack: Dict) -> Dict:
        """Generate documentation from analysis"""
        return {
            "overview": f"# {spec['title']}\n\n{spec['description']}",
            "architecture": f"""## Architecture

**Pattern:** {spec.get('architecture_pattern', 'Unknown')}
**Primary Language:** {tech_stack.get('primary_language', 'Unknown')}
**Framework:** {tech_stack.get('framework', tech_stack.get('backend', {}).get('framework', 'Unknown'))}

### Entry Points
{chr(10).join(['- ' + ep for ep in spec.get('entry_points', [])])}

### Inferred Features
{chr(10).join(['- ' + f for f in spec.get('inferred_features', [])])}
""",
            "api_documentation": self._generate_api_docs(spec.get('api_endpoints', [])),
            "setup_instructions": self._generate_setup_instructions(tech_stack)
        }
    
    def _generate_api_docs(self, endpoints: List[Dict]) -> str:
        """Generate API documentation"""
        if not endpoints:
            return "No API endpoints detected."
        
        docs = "## API Endpoints\n\n"
        for ep in endpoints[:15]:
            docs += f"### {ep.get('method', 'GET')} {ep.get('path', '/')}\n"
            docs += f"- Source: `{ep.get('source_file', 'unknown')}`\n"
            docs += f"- Inferred: {ep.get('inferred', True)}\n\n"
        
        return docs
    
    def _generate_setup_instructions(self, tech_stack: Dict) -> str:
        """Generate setup instructions based on tech stack"""
        instructions = "## Setup Instructions\n\n"
        
        lang = tech_stack.get('primary_language', '')
        
        if 'JavaScript' in lang or 'TypeScript' in lang:
            instructions += """```bash
# Install dependencies
npm install

# Run development server
npm run dev

# Run tests
npm test
```
"""
        elif 'Python' in lang:
            instructions += """```bash
# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\\Scripts\\activate

# Install dependencies
pip install -r requirements.txt

# Run application
python app.py
```
"""
        
        if tech_stack.get('deployment', {}).get('containerization') == 'Docker':
            instructions += """
### Docker Setup
```bash
# Build and run with Docker Compose
docker-compose up -d
```
"""
        
        return instructions
    
    def _create_architecture_diagrams(self, architecture: Dict, tech_stack: Dict) -> Dict:
        """Create text-based architecture diagrams"""
        diagrams = {}
        
        # High-level architecture
        diagrams["high_level"] = """
┌─────────────────────────────────────────────┐
│              Application Architecture         │
├─────────────────────────────────────────────┤
│                                             │
│   ┌─────────────┐      ┌─────────────────┐ │
│   │   Frontend  │──────▶│     Backend     │ │
│   └─────────────┘      └─────────────────┘ │
│                                │            │
│                                ▼            │
│                        ┌─────────────────┐ │
│                        │    Database     │ │
│                        └─────────────────┘ │
│                                             │
└─────────────────────────────────────────────┘
"""
        
        # Layer diagram
        pattern = architecture.get("pattern", "Layered")
        layers = architecture.get("layers", ["Presentation", "Business Logic", "Data"])
        
        diagrams["layers"] = f"""
┌─────────────────────────────────────────────┐
│           {pattern} Architecture           │
├─────────────────────────────────────────────┤
"""
        for i, layer in enumerate(layers):
            diagrams["layers"] += f"│  {'  ' * i}┌───────────────┐{'  ' * (len(layers) - i - 1)}  │\n"
            diagrams["layers"] += f"│  {'  ' * i}│  {layer:^13} │{'  ' * (len(layers) - i - 1)}  │\n"
            diagrams["layers"] += f"│  {'  ' * i}└───────────────┘{'  ' * (len(layers) - i - 1)}  │\n"
        
        diagrams["layers"] += "└─────────────────────────────────────────────┘\n"
        
        return diagrams
    
    def _save_analysis(self, analysis_dir: Path, analysis_data: Dict):
        """Save analysis to disk"""
        # Save JSON
        with open(analysis_dir / "analysis.json", 'w') as f:
            json.dump(analysis_data, f, indent=2)
        
        # Generate comprehensive report
        with open(analysis_dir / "RECONSTRUCTED_SPEC.md", 'w') as f:
            f.write(self._generate_full_report(analysis_data))
    
    def _generate_full_report(self, data: Dict) -> str:
        """Generate comprehensive Markdown report"""
        spec = data.get("reconstructed_spec", {})
        tech = data.get("tech_stack", {})
        metrics = data.get("code_metrics", {})
        
        report = f"""# 🔍 Reverse Engineering Report

## {spec.get('title', 'Unknown Application')}

**Source:** `{data.get('source_path', 'Unknown')}`  
**Analyzed:** {data.get('analyzed_at', 'Unknown')}  
**Analysis Type:** {data.get('analysis_type', 'full')}

---

## 📊 Code Metrics

| Metric | Value |
|--------|-------|
| Total Files | {metrics.get('total_files', 0)} |
| Lines of Code | {metrics.get('lines_of_code', 0):,} |
| Blank Lines | {metrics.get('blank_lines', 0):,} |
| Comment Lines | {metrics.get('comment_lines', 0):,} |
| Code-to-Comment Ratio | {metrics.get('lines_of_code', 0) / max(1, metrics.get('comment_lines', 1)):.1f}:1 |

### File Types
"""
        
        for ext, count in sorted(metrics.get('file_types', {}).items(), key=lambda x: x[1], reverse=True):
            report += f"- `{ext}`: {count} files\n"
        
        report += f"""

---

## 🛠️ Technology Stack

- **Primary Language:** {tech.get('primary_language', 'Unknown')}
- **Framework:** {tech.get('framework', tech.get('backend', {}).get('framework', 'Unknown'))}
- **Architecture:** {spec.get('architecture_pattern', 'Unknown')}
- **Database:** {tech.get('database', 'Unknown')}
- **Testing:** {tech.get('testing', 'Not detected')}
- **Containerization:** {tech.get('deployment', {}).get('containerization', 'None')}

### Dependencies
- **Total:** {data.get('dependencies', {}).get('total_count', 0)} packages
- **Production:** {len(data.get('dependencies', {}).get('production', []))}
- **Development:** {len(data.get('dependencies', {}).get('development', []))}

### Key Dependencies
"""
        
        for dep in data.get('dependencies', {}).get('key_dependencies', [])[:10]:
            report += f"- `{dep}`\n"
        
        report += f"""

---

## 🏗️ Architecture

{data.get('diagrams', {}).get('high_level', '')}

### Layers
{data.get('diagrams', {}).get('layers', '')}

### Entry Points
"""
        
        for ep in spec.get('entry_points', []):
            report += f"- `{ep}`\n"
        
        report += f"""

---

## 🔌 API Endpoints ({spec.get('api_summary', {}).get('total_endpoints', 0)} detected)

### By Method
"""
        
        for method, count in spec.get('api_summary', {}).get('endpoints_by_method', {}).items():
            report += f"- {method}: {count}\n"
        
        report += "\n### Endpoint Details\n\n"
        for ep in data.get('api_endpoints', [])[:15]:
            report += f"**{ep.get('method', 'GET')}** `{ep.get('path', '/')}`\n"
            report += f"- Source: `{ep.get('source_file', 'unknown')}`\n\n"
        
        report += f"""

---

## 💾 Database Schema

**Type:** {data.get('database_schema', {}).get('type', 'Unknown')}

### Models/Tables
"""
        
        for model in data.get('database_schema', {}).get('models', []):
            report += f"- `{model}`\n"
        
        for table in data.get('database_schema', {}).get('tables', []):
            report += f"- `{table}`\n"
        
        report += f"""

---

## ✨ Inferred Features

Based on code analysis:

"""
        
        for feature in spec.get('inferred_features', []):
            report += f"- {feature}\n"
        
        report += f"""

---

## 📝 Reconstructed Specification

{data.get('documentation', {}).get('overview', '')}

{data.get('documentation', {}).get('architecture', '')}

{data.get('documentation', {}).get('api_documentation', '')}

---

## 🚀 Setup Instructions

{data.get('documentation', {}).get('setup_instructions', 'No specific instructions available.')}

---

## 📋 Reconstruction Notes

- **Confidence Level:** {spec.get('reconstruction_confidence', 'unknown')}
- **Analysis Version:** {data.get('reverse_engineer_agent', 'v1.0')}

### Limitations
This reconstruction is based on static code analysis. Dynamic behavior, business logic details, and specific implementation nuances may not be fully captured.

---

*Generated by DevForge Reverse Engineer Agent*
"""
        
        return report

if __name__ == "__main__":
    import sys
    
    if len(sys.argv) < 2:
        print("Usage: python3 reverse_engineer_agent.py <source_path> [analysis_type]")
        print("Example: python3 reverse_engineer_agent.py /path/to/existing/project full")
        print("Example: python3 reverse_engineer_agent.py https://github.com/user/repo")
        sys.exit(1)
    
    source = sys.argv[1]
    analysis_type = sys.argv[2] if len(sys.argv) > 2 else "full"
    
    re_agent = ReverseEngineerAgent()
    analysis = re_agent.analyze_codebase(source, analysis_type)
    
    print(f"\n📁 Analysis saved to: projects/{analysis['id']}/")
    print(f"📄 Full report: projects/{analysis['id']}/RECONSTRUCTED_SPEC.md")
