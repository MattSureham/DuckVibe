#!/usr/bin/env python3
"""
DevForge - Pipeline Orchestrator
Coordinates all 6 agents: Chronicle, Web Scraper, PM, Reverse Engineer, Dev, QA, Deploy
"""

import os
import sys
import json
import subprocess
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent))
sys.path.insert(0, str(Path(__file__).parent / "agents"))

from ai_provider import get_ai_provider

class PipelineOrchestrator:
    """Main orchestrator for the DevForge pipeline"""
    
    def __init__(self, config_path: str = "config/.env"):
        self.config_path = config_path
        self.ai_provider = get_ai_provider(config_path)
        self.projects_dir = Path("projects")
        self.projects_dir.mkdir(exist_ok=True)
        
        # Initialize chronicle agent
        from chronicle.chronicle_agent import get_chronicle_agent
        self.chronicle = get_chronicle_agent(config_path)
        
        # Load configuration
        self.config = self._load_config()
    
    def _load_config(self) -> Dict:
        """Load configuration"""
        config = {}
        if Path(self.config_path).exists():
            with open(self.config_path) as f:
                for line in f:
                    if '=' in line and not line.startswith('#'):
                        key, value = line.strip().split('=', 1)
                        config[key] = value.strip('"').strip("'")
        # Environment override
        for key in os.environ:
            config[key] = os.environ[key]
        return config
    
    def run_full_pipeline(self, idea: str, tech_stack: Optional[str] = None,
                          source_codebase: Optional[str] = None) -> Dict:
        """
        Run the complete pipeline from idea/reverse-engineer to deployment
        
        Args:
            idea: New feature idea (or use source_codebase for reverse engineering)
            tech_stack: Optional preferred tech stack
            source_codebase: Optional path/URL to existing codebase to reverse engineer
        """
        pipeline_run_id = f"pipeline_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        
        # Start chronicle recording
        feature_id_placeholder = idea.replace(" ", "_")[:30]
        self.chronicle.start_session(feature_id_placeholder, "pipeline_run")
        
        print(f"\n{'='*70}")
        print(f"🚀 DEVFORGE PIPELINE: {pipeline_run_id}")
        print(f"📜 CHRONICLE: Recording all agent interactions")
        print(f"{'='*70}\n")
        
        results = {
            "pipeline_id": pipeline_run_id,
            "started_at": datetime.now().isoformat(),
            "steps": []
        }
        
        try:
            # Step 0: Reverse Engineer (if source provided)
            if source_codebase:
                print("\n📋 STEP 0: REVERSE ENGINEER")
                print("-" * 70)
                rev_result = self._run_reverse_engineer(source_codebase)
                results["steps"].append({"step": "reverse_engineer", "result": rev_result})
                
                # Chronicle: Record reverse engineering
                self.chronicle.record_agent_action(
                    "reverse_engineer", "analyze_codebase",
                    source_codebase, rev_result,
                    {"files_analyzed": rev_result.get("metrics", {}).get("total_files", 0)}
                )
                
                # Use reconstructed spec as basis
                idea = f"Rebuild and improve: {rev_result.get('spec', {}).get('title', 'Application')}"
                tech_stack = tech_stack or rev_result.get('tech_stack', {}).get('primary_language', 'React, Node.js')
            
            # Step -1: Web Scraper - Market Research (before PM)
            if not source_codebase:  # Only for new ideas, not reverse engineering
                print("\n📋 STEP -1: WEB SCRAPER - MARKET RESEARCH")
                print("-" * 70)
                scraper_result = self._run_web_scraper(idea)
                results["steps"].append({"step": "web_scraper", "result": scraper_result})
                
                # Chronicle: Record market research
                self.chronicle.record_agent_action(
                    "web_scraper", "market_research",
                    idea, scraper_result,
                    {"competitors_found": scraper_result.get("competitors_found", 0)}
                )
                
                # Chronicle: Record handoff to PM
                self.chronicle.record_handoff(
                    "web_scraper", "pm",
                    "market_research_report",
                    f"{scraper_result.get('competitors_found', 0)} competitors, {scraper_result.get('pain_points', 0)} pain points"
                )
            
            # Step 1: PM Agent
            print("\n📋 STEP 1: PRODUCT MANAGER")
            print("-" * 70)
            pm_result = self._run_pm_agent(idea, tech_stack)
            results["steps"].append({"step": "pm", "result": pm_result})
            feature_id = pm_result["feature_id"]
            
            # Chronicle: Record PM work
            self.chronicle.record_agent_action(
                "pm", "create_specification",
                idea, pm_result,
                {"user_stories": pm_result.get("user_stories_count", 0)}
            )
            
            # Chronicle: Record decision
            self.chronicle.record_decision(
                "pm", f"Build with {tech_stack or 'default stack'}",
                "Based on market research and technical requirements",
                ["Alternative stacks evaluated"]
            )
            
            # Chronicle: Record checkpoint
            self.chronicle.record_checkpoint("specification", "success", pm_result)
            
            # Chronicle: Record handoff to Dev
            self.chronicle.record_handoff(
                "pm", "dev",
                "feature_specification",
                f"{pm_result.get('user_stories_count', 0)} user stories, API spec, DB schema"
            )
            
            # Step 2: Dev Agent
            print("\n📋 STEP 2: DEVELOPER")
            print("-" * 70)
            dev_result = self._run_dev_agent(feature_id)
            results["steps"].append({"step": "dev", "result": dev_result})
            
            # Chronicle: Record Dev work
            self.chronicle.record_agent_action(
                "dev", "generate_codebase",
                feature_id, dev_result,
                {"files_generated": dev_result.get("files_generated", 0)}
            )
            
            # Chronicle: Record checkpoint
            self.chronicle.record_checkpoint("development", "success", dev_result)
            
            # Chronicle: Record handoff to QA
            self.chronicle.record_handoff(
                "dev", "qa",
                "codebase",
                f"{dev_result.get('files_generated', 0)} files in {dev_result.get('tech_stack_used', {}).get('frontend', {}).get('name', 'unknown')} + {dev_result.get('tech_stack_used', {}).get('backend', {}).get('name', 'unknown')}"
            )
            
            # Step 3: QA Agent
            print("\n📋 STEP 3: QUALITY ASSURANCE")
            print("-" * 70)
            qa_result = self._run_qa_agent(feature_id)
            results["steps"].append({"step": "qa", "result": qa_result})
            
            # Chronicle: Record QA work
            self.chronicle.record_agent_action(
                "qa", "test_feature",
                feature_id, qa_result,
                {"score": qa_result.get("overall_score", 0)}
            )
            
            # Chronicle: Record checkpoint
            self.chronicle.record_checkpoint("testing", qa_result.get("status", "unknown"), qa_result)
            
            # Check if QA passed
            qa_score = qa_result.get("test_report", {}).get("summary", {}).get("overall_score", 0)
            if qa_score < 50:
                print(f"\n⚠️  QA score ({qa_score}%) too low. Pipeline halted.")
                print("   Fix issues and re-run pipeline.")
                
                # Chronicle: Record issue
                self.chronicle.record_issue(
                    "qa", "low_test_score",
                    f"QA score {qa_score}% below threshold",
                    "Pipeline halted for fixes"
                )
                
                results["status"] = "failed_qa"
                
                # End chronicle
                self.chronicle.end_session("failed_qa")
                return results
            
            # Step 4: Deploy Agent
            print("\n📋 STEP 4: DEPLOYMENT")
            print("-" * 70)
            deploy_result = self._run_deploy_agent(feature_id)
            results["steps"].append({"step": "deploy", "result": deploy_result})
            
            # Chronicle: Record Deploy work
            self.chronicle.record_agent_action(
                "deploy", "deploy_application",
                feature_id, deploy_result,
                {"environment": "local", "platform": "docker"}
            )
            
            # Chronicle: Record handoff (final delivery)
            self.chronicle.record_handoff(
                "deploy", "user",
                "deployed_application",
                f"Available at {list(deploy_result.get('urls', {}).values())[0] if deploy_result.get('urls') else 'local'}"
            )
            
            # Chronicle: Record final checkpoint
            self.chronicle.record_checkpoint("deployment", "success", deploy_result)
            
            # Chronicle: Record collaboration across all agents
            self.chronicle.record_collaboration(
                ["web_scraper", "pm", "dev", "qa", "deploy"],
                "Full pipeline execution",
                f"Successfully built and deployed {feature_id}"
            )
            
            results["status"] = "success"
            results["feature_id"] = feature_id
            results["completed_at"] = datetime.now().isoformat()
            
            # End chronicle recording
            chronicle_report = self.chronicle.end_session("success")
            results["chronicle"] = chronicle_report
            
            # Print summary
            self._print_summary(results)
            
        except Exception as e:
            results["status"] = "failed"
            results["error"] = str(e)
            print(f"\n❌ Pipeline failed: {e}")
            
            # Chronicle: Record the failure
            self.chronicle.record_issue("pipeline", "exception", str(e))
            self.chronicle.end_session("failed")
            
            import traceback
            traceback.print_exc()
        
        # Save pipeline results
        pipeline_file = Path("data") / f"{pipeline_run_id}.json"
        pipeline_file.parent.mkdir(exist_ok=True)
        with open(pipeline_file, 'w') as f:
            json.dump(results, f, indent=2)
        
        return results
    
    def _run_reverse_engineer(self, source: str) -> Dict:
        """Run reverse engineer agent"""
        from re.reverse_engineer_agent import ReverseEngineerAgent
        
        agent = ReverseEngineerAgent(self.config_path)
        result = agent.analyze_codebase(source, "full")
        
        return {
            "analysis_id": result["id"],
            "tech_stack": result["tech_stack"],
            "spec": result["reconstructed_spec"],
            "metrics": result["code_metrics"]
        }
    
    def _run_web_scraper(self, topic: str) -> Dict:
        """Run Web Scraper agent"""
        from scraper.web_scraper_engineer import WebScraperEngineer
        
        agent = WebScraperEngineer(self.config_path)
        result = agent.research_market(topic, "medium")
        
        return {
            "research_id": result["id"],
            "competitors_found": len(result["competitors"]),
            "trends_identified": len(result["trends"]),
            "pain_points": len(result["pain_points"]),
            "insights": result["insights"]
        }
    
    def _run_pm_agent(self, idea: str, tech_stack: Optional[str]) -> Dict:
        """Run PM agent"""
        from pm.pm_agent import PMAgent
        
        agent = PMAgent(self.config_path)
        result = agent.generate_feature(idea, tech_stack)
        
        return {
            "feature_id": result["id"],
            "title": result["specification"]["title"],
            "user_stories_count": len(result["user_stories"]),
            "acceptance_criteria_count": sum(len(c["criteria"]) for c in result["acceptance_criteria"].values())
        }
    
    def _run_dev_agent(self, feature_id: str) -> Dict:
        """Run Dev agent"""
        from dev.dev_agent import DevAgent
        
        agent = DevAgent(self.config_path)
        result = agent.develop_feature(feature_id)
        
        return {
            "feature_id": feature_id,
            "tech_stack_used": result["development"]["tech_stack"],
            "files_generated": len(result["development"]["backend"]["files"]) + len(result["development"]["frontend"]["files"])
        }
    
    def _run_qa_agent(self, feature_id: str) -> Dict:
        """Run QA agent"""
        from qa.qa_agent import QAAgent
        
        agent = QAAgent(self.config_path)
        result = agent.test_feature(feature_id, ["unit", "integration"])
        
        return {
            "feature_id": feature_id,
            "test_report": result,
            "overall_score": result["summary"]["overall_score"],
            "status": result["summary"]["status"]
        }
    
    def _run_deploy_agent(self, feature_id: str, environment: str = "local",
                          platform: str = "docker") -> Dict:
        """Run Deploy agent"""
        from deploy.deploy_agent import DeployAgent
        
        agent = DeployAgent(self.config_path)
        result = agent.deploy(feature_id, environment, platform)
        
        return {
            "feature_id": feature_id,
            "deployment_id": result["deployment_id"],
            "status": result["status"],
            "urls": result.get("deployment", {}).get("urls", {})
        }
    
    def _print_summary(self, results: Dict):
        """Print pipeline summary"""
        print(f"\n{'='*70}")
        print("✅ PIPELINE COMPLETE")
        print(f"{'='*70}")
        print(f"\nPipeline ID: {results['pipeline_id']}")
        print(f"Feature ID: {results.get('feature_id', 'N/A')}")
        print(f"Status: {results['status'].upper()}")
        print(f"\nSteps Completed:")
        
        for step in results["steps"]:
            step_name = step["step"].upper()
            step_result = step["result"]
            
            if step["step"] == "pm":
                print(f"  ✅ PM: {step_result.get('title', 'N/A')}")
                print(f"     {step_result.get('user_stories_count', 0)} user stories")
            
            elif step["step"] == "reverse_engineer":
                print(f"  ✅ RE: Analyzed {step_result.get('metrics', {}).get('total_files', 0)} files")
                print(f"     Stack: {step_result.get('tech_stack', {}).get('primary_language', 'N/A')}")
            
            elif step["step"] == "web_scraper":
                print(f"  🕷️  SCRAPER: Market research complete")
                print(f"     {step_result.get('competitors_found', 0)} competitors")
                print(f"     {step_result.get('trends_identified', 0)} trends")
                print(f"     {step_result.get('pain_points', 0)} pain points")
            
            elif step["step"] == "dev":
                print(f"  ✅ DEV: Generated {step_result.get('files_generated', 0)} files")
                stack = step_result.get('tech_stack_used', {})
                print(f"     Stack: {stack.get('frontend', {}).get('name', 'N/A')} + {stack.get('backend', {}).get('name', 'N/A')}")
            
            elif step["step"] == "qa":
                score = step_result.get('overall_score', 0)
                status_icon = "✅" if score >= 70 else "⚠️"
                print(f"  {status_icon} QA: {score:.1f}% score")
            
            elif step["step"] == "deploy":
                urls = step_result.get('urls', {})
                print(f"  ✅ DEPLOY: {step_result.get('status', 'N/A')}")
                for name, url in urls.items():
                    print(f"     {name}: {url}")
        
        print(f"\n📁 Project location: projects/{results.get('feature_id', 'N/A')}/")
        print(f"📄 Pipeline record: data/{results['pipeline_id']}.json")
        
        # Print chronicle summary if available
        if "chronicle" in results:
            chronicle = results["chronicle"]
            summary = chronicle.get("summary", {})
            print(f"\n📜 CHRONICLE SUMMARY")
            print(f"   Total events: {summary.get('total_events', 0)}")
            print(f"   Handoffs: {summary.get('total_handoffs', 0)}")
            print(f"   Decisions: {summary.get('total_decisions', 0)}")
            print(f"   Collaborations: {summary.get('total_collaborations', 0)}")
            print(f"   Chronicle: data/chronicle/{chronicle.get('session_id', 'unknown')}_narrative.md")
        
        print(f"{'='*70}\n")


def main():
    """Main entry point"""
    import argparse
    
    parser = argparse.ArgumentParser(description="DevForge Pipeline Orchestrator")
    parser.add_argument("command", choices=[
        "full", "reverse", "pm", "dev", "qa", "deploy", "pipeline"
    ], help="Command to run")
    parser.add_argument("input", nargs="?", help="Input (idea, feature_id, or source path)")
    parser.add_argument("--tech-stack", "-t", help="Preferred tech stack")
    parser.add_argument("--env", "-e", default="local", help="Deployment environment")
    parser.add_argument("--platform", "-p", default="docker", help="Deployment platform")
    
    args = parser.parse_args()
    
    orchestrator = PipelineOrchestrator()
    
    if args.command == "full":
        if not args.input:
            print("Error: 'full' command requires an idea. Example:")
            print("  python3 pipeline.py full 'Task management app'")
            sys.exit(1)
        
        orchestrator.run_full_pipeline(args.input, args.tech_stack)
    
    elif args.command == "reverse":
        if not args.input:
            print("Error: 'reverse' command requires a source path or URL. Example:")
            print("  python3 pipeline.py reverse /path/to/project")
            print("  python3 pipeline.py reverse https://github.com/user/repo")
            sys.exit(1)
        
        orchestrator.run_full_pipeline(
            idea="Reconstructed application",
            source_codebase=args.input
        )
    
    elif args.command == "pipeline":
        # Run full pipeline with all steps
        if not args.input:
            print("Error: 'pipeline' command requires an idea")
            sys.exit(1)
        
        orchestrator.run_full_pipeline(args.input, args.tech_stack)
    
    elif args.command in ["pm", "dev", "qa", "deploy"]:
        # Run individual agent
        if not args.input:
            print(f"Error: '{args.command}' command requires a feature_id or input")
            sys.exit(1)
        
        if args.command == "pm":
            result = orchestrator._run_pm_agent(args.input, args.tech_stack)
        elif args.command == "dev":
            result = orchestrator._run_dev_agent(args.input)
        elif args.command == "qa":
            result = orchestrator._run_qa_agent(args.input)
        elif args.command == "deploy":
            result = orchestrator._run_deploy_agent(args.input, args.env, args.platform)
        
        print(json.dumps(result, indent=2))
    
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
