#!/usr/bin/env python3
"""
DevForge - PM Agent (Product Manager)
Generates features, requirements, and project specifications
"""

import os
import json
import random
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional

class PMAgent:
    """Product Manager Agent - comes up with features and requirements"""
    
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
    
    def generate_feature(self, project_idea: str, tech_stack: Optional[str] = None) -> Dict:
        """
        Generate a complete feature specification from an idea
        
        Args:
            project_idea: High-level description (e.g., "Task management app")
            tech_stack: Optional tech preferences (e.g., "React, Node.js, PostgreSQL")
        """
        feature_id = self._generate_feature_id()
        feature_dir = self.projects_dir / feature_id
        feature_dir.mkdir(exist_ok=True)
        
        print(f"🎯 PM Agent: Analyzing feature idea...")
        print(f"   Idea: {project_idea}")
        
        # Generate feature specification
        spec = self._create_feature_spec(project_idea, tech_stack)
        
        # Generate user stories
        stories = self._generate_user_stories(spec)
        
        # Generate acceptance criteria
        criteria = self._generate_acceptance_criteria(spec, stories)
        
        # Generate technical requirements
        tech_reqs = self._generate_technical_requirements(spec, tech_stack)
        
        # Create API specifications (if applicable)
        api_spec = self._generate_api_spec(spec)
        
        # Generate database schema (if applicable)
        db_schema = self._generate_database_schema(spec)
        
        # Save all artifacts
        feature_data = {
            "id": feature_id,
            "idea": project_idea,
            "specification": spec,
            "user_stories": stories,
            "acceptance_criteria": criteria,
            "technical_requirements": tech_reqs,
            "api_specification": api_spec,
            "database_schema": db_schema,
            "status": "spec_ready",
            "created_at": datetime.now().isoformat(),
            "pm_agent": "v1.0"
        }
        
        self._save_feature(feature_dir, feature_data)
        
        print(f"✅ PM Agent: Feature {feature_id} specified")
        print(f"   📋 {len(stories)} user stories")
        print(f"   ✅ {sum(len(s['criteria']) for s in criteria.values())} acceptance criteria")
        print(f"   🔧 {len(tech_reqs)} technical requirements")
        
        return feature_data
    
    def _generate_feature_id(self):
        """Generate unique feature ID"""
        timestamp = datetime.now().strftime("%Y%m%d")
        existing = len(list(self.projects_dir.glob("feat_*")))
        return f"feat_{timestamp}_{existing + 1:04d}"
    
    def _create_feature_spec(self, idea: str, tech_stack: Optional[str]) -> Dict:
        """Create detailed feature specification"""
        # In production: Call Claude/GPT to analyze and expand the idea
        # For now, template-based generation
        
        feature_types = [
            "web_application", "mobile_app", "api_service", 
            "cli_tool", "data_pipeline", "automation_script"
        ]
        
        return {
            "title": idea,
            "description": f"A comprehensive solution for {idea}",
            "type": random.choice(feature_types),
            "tech_stack": tech_stack or "Modern web stack (TBD by Dev team)",
            "mvp_features": [
                f"Core {idea} functionality",
                "User authentication",
                "Basic CRUD operations",
                "Simple dashboard"
            ],
            "v2_features": [
                "Advanced analytics",
                "Third-party integrations",
                "Mobile responsiveness",
                "Performance optimizations"
            ],
            "target_users": "End users and administrators",
            "success_metrics": [
                "User adoption rate",
                "Feature completion",
                "Performance benchmarks"
            ]
        }
    
    def _generate_user_stories(self, spec: Dict) -> List[Dict]:
        """Generate user stories from spec"""
        stories = []
        
        # MVP stories
        stories.extend([
            {
                "id": "US-001",
                "role": "As a user",
                "action": f"I want to access {spec['title']}",
                "benefit": "So that I can use the core functionality",
                "priority": "high",
                "story_points": 3
            },
            {
                "id": "US-002",
                "role": "As a user",
                "action": "I want to create an account",
                "benefit": "So that I can save my data",
                "priority": "high",
                "story_points": 5
            },
            {
                "id": "US-003",
                "role": "As a user",
                "action": "I want to manage my content",
                "benefit": "So that I can organize my work",
                "priority": "high",
                "story_points": 5
            },
            {
                "id": "US-004",
                "role": "As an admin",
                "action": "I want to view user analytics",
                "benefit": "So that I can understand usage patterns",
                "priority": "medium",
                "story_points": 8
            }
        ])
        
        # Add V2 stories
        stories.extend([
            {
                "id": "US-005",
                "role": "As a user",
                "action": "I want to export my data",
                "benefit": "So that I can use it elsewhere",
                "priority": "low",
                "story_points": 3
            },
            {
                "id": "US-006",
                "role": "As a user",
                "action": "I want to receive notifications",
                "benefit": "So that I stay updated",
                "priority": "low",
                "story_points": 5
            }
        ])
        
        return stories
    
    def _generate_acceptance_criteria(self, spec: Dict, stories: List[Dict]) -> Dict:
        """Generate acceptance criteria for each story"""
        criteria = {}
        
        for story in stories:
            story_criteria = []
            
            if "account" in story['action'].lower():
                story_criteria = [
                    "User can register with email/password",
                    "User can login with credentials",
                    "User can logout",
                    "Password must be at least 8 characters",
                    "User receives confirmation email"
                ]
            elif "manage" in story['action'].lower():
                story_criteria = [
                    "User can create new items",
                    "User can read/view items",
                    "User can update items",
                    "User can delete items",
                    "Changes persist after refresh"
                ]
            elif "analytics" in story['action'].lower():
                story_criteria = [
                    "Dashboard displays user count",
                    "Charts show activity over time",
                    "Data updates in real-time",
                    "Export function works"
                ]
            else:
                story_criteria = [
                    "Feature is accessible from main navigation",
                    "Feature works on desktop and mobile",
                    "Response time is under 2 seconds",
                    "Error handling is implemented"
                ]
            
            criteria[story['id']] = {
                "story": story['action'],
                "criteria": story_criteria
            }
        
        return criteria
    
    def _generate_technical_requirements(self, spec: Dict, tech_stack: Optional[str]) -> List[Dict]:
        """Generate technical requirements"""
        requirements = []
        
        # Frontend
        requirements.append({
            "category": "Frontend",
            "requirement": "Responsive web interface",
            "technologies": ["React", "Vue", or "Angular"],
            "priority": "high"
        })
        
        # Backend
        requirements.append({
            "category": "Backend",
            "requirement": "RESTful API",
            "technologies": ["Node.js/Express", "Python/FastAPI", or "Go"],
            "priority": "high"
        })
        
        # Database
        requirements.append({
            "category": "Database",
            "requirement": "Persistent data storage",
            "technologies": ["PostgreSQL", "MongoDB", or "SQLite"],
            "priority": "high"
        })
        
        # Auth
        requirements.append({
            "category": "Authentication",
            "requirement": "Secure user authentication",
            "technologies": ["JWT", "OAuth2", "Session-based"],
            "priority": "high"
        })
        
        # Testing
        requirements.append({
            "category": "Testing",
            "requirement": "Automated test coverage",
            "technologies": ["Jest", "PyTest", "Cypress"],
            "priority": "medium"
        })
        
        # Deployment
        requirements.append({
            "category": "Deployment",
            "requirement": "Containerized deployment",
            "technologies": ["Docker", "Docker Compose"],
            "priority": "medium"
        })
        
        return requirements
    
    def _generate_api_spec(self, spec: Dict) -> Dict:
        """Generate API specification"""
        return {
            "version": "v1",
            "base_url": "/api/v1",
            "endpoints": [
                {
                    "path": "/auth/register",
                    "method": "POST",
                    "description": "Register new user",
                    "request": {"email": "string", "password": "string"},
                    "response": {"token": "string", "user": "object"}
                },
                {
                    "path": "/auth/login",
                    "method": "POST",
                    "description": "User login",
                    "request": {"email": "string", "password": "string"},
                    "response": {"token": "string", "user": "object"}
                },
                {
                    "path": "/items",
                    "method": "GET",
                    "description": "List all items",
                    "auth": True,
                    "response": {"items": "array"}
                },
                {
                    "path": "/items",
                    "method": "POST",
                    "description": "Create new item",
                    "auth": True,
                    "request": {"title": "string", "content": "string"},
                    "response": {"item": "object"}
                },
                {
                    "path": "/items/:id",
                    "method": "GET",
                    "description": "Get single item",
                    "auth": True,
                    "response": {"item": "object"}
                },
                {
                    "path": "/items/:id",
                    "method": "PUT",
                    "description": "Update item",
                    "auth": True,
                    "request": {"title": "string", "content": "string"},
                    "response": {"item": "object"}
                },
                {
                    "path": "/items/:id",
                    "method": "DELETE",
                    "description": "Delete item",
                    "auth": True,
                    "response": {"success": "boolean"}
                }
            ]
        }
    
    def _generate_database_schema(self, spec: Dict) -> Dict:
        """Generate database schema"""
        return {
            "database": "PostgreSQL",
            "tables": [
                {
                    "name": "users",
                    "columns": [
                        {"name": "id", "type": "UUID", "primary_key": True},
                        {"name": "email", "type": "VARCHAR(255)", "unique": True},
                        {"name": "password_hash", "type": "VARCHAR(255)"},
                        {"name": "created_at", "type": "TIMESTAMP"},
                        {"name": "updated_at", "type": "TIMESTAMP"}
                    ]
                },
                {
                    "name": "items",
                    "columns": [
                        {"name": "id", "type": "UUID", "primary_key": True},
                        {"name": "user_id", "type": "UUID", "foreign_key": "users.id"},
                        {"name": "title", "type": "VARCHAR(255)"},
                        {"name": "content", "type": "TEXT"},
                        {"name": "status", "type": "VARCHAR(50)"},
                        {"name": "created_at", "type": "TIMESTAMP"},
                        {"name": "updated_at", "type": "TIMESTAMP"}
                    ]
                }
            ]
        }
    
    def _save_feature(self, feature_dir: Path, feature_data: Dict):
        """Save feature specification to disk"""
        # Main metadata
        with open(feature_dir / "feature_spec.json", 'w') as f:
            json.dump(feature_data, f, indent=2)
        
        # Human-readable spec
        with open(feature_dir / "README.md", 'w') as f:
            f.write(self._generate_readme(feature_data))
    
    def _generate_readme(self, data: Dict) -> str:
        """Generate human-readable README"""
        spec = data['specification']
        
        readme = f"""# {spec['title']}

## Description
{spec['description']}

## Tech Stack
{spec['tech_stack']}

## MVP Features
"""
        for feat in spec['mvp_features']:
            readme += f"- {feat}\n"
        
        readme += "\n## User Stories\n\n"
        for story in data['user_stories'][:4]:  # Show MVP stories
            readme += f"### {story['id']} ({story['priority'].upper()})")
            readme += f"\n**{story['role']},** {story['action']}\n"
            readme += f"*{story['benefit']}*\n\n"
            readme += f"**Story Points:** {story['story_points']}\n\n"
            
            # Add acceptance criteria
            if story['id'] in data['acceptance_criteria']:
                readme += "**Acceptance Criteria:**\n"
                for criteria in data['acceptance_criteria'][story['id']]['criteria']:
                    readme += f"- [ ] {criteria}\n"
                readme += "\n"
        
        readme += "\n## API Endpoints\n\n"
        for endpoint in data['api_specification']['endpoints']:
            readme += f"### {endpoint['method']} {endpoint['path']}\n"
            readme += f"{endpoint['description']}\n\n"
        
        readme += "\n## Status\n"
        readme += f"- Current Status: {data['status']}\n"
        readme += f"- Created: {data['created_at']}\n"
        readme += "- Next Step: Awaiting development\n"
        
        return readme

if __name__ == "__main__":
    import sys
    
    if len(sys.argv) < 2:
        print("Usage: python3 pm_agent.py 'Your feature idea' [tech_stack]")
        print("Example: python3 pm_agent.py 'Task management app' 'React, Node.js'")
        sys.exit(1)
    
    idea = sys.argv[1]
    tech_stack = sys.argv[2] if len(sys.argv) > 2 else None
    
    pm = PMAgent()
    feature = pm.generate_feature(idea, tech_stack)
    
    print(f"\n📁 Feature saved to: projects/{feature['id']}/")
    print(f"📄 View spec: projects/{feature['id']}/README.md")
