#!/usr/bin/env python3
"""
DevForge - Chronicle Agent (Historian)
Records and documents all agent interactions and collaboration
"""

import os
import json
import time
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Any
import threading

class ChronicleAgent:
    """
    Chronicle Agent - The historian of the DevForge pipeline
    Records every interaction, decision, and collaboration between agents
    """
    
    def __init__(self, config_path="config/.env"):
        self.config = self._load_config(config_path)
        self.chronicle_dir = Path("data") / "chronicle"
        self.chronicle_dir.mkdir(parents=True, exist_ok=True)
        
        # Current session
        self.session_id = None
        self.event_log = []
        self.start_time = None
        
        # Thread-safe logging
        self.lock = threading.Lock()
        
    def _load_config(self, path):
        config = {}
        if os.path.exists(path):
            with open(path) as f:
                for line in f:
                    if '=' in line and not line.startswith('#'):
                        key, value = line.strip().split('=', 1)
                        config[key] = value.strip('"').strip("'")
        return config
    
    def start_session(self, feature_id: str, trigger: str = "manual") -> str:
        """Start a new recording session"""
        self.session_id = f"session_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{feature_id}"
        self.start_time = time.time()
        self.event_log = []
        
        self._record_event({
            "type": "session_start",
            "timestamp": datetime.now().isoformat(),
            "feature_id": feature_id,
            "trigger": trigger,
            "chronicle_agent_version": "1.0"
        })
        
        print(f"📜 Chronicle: Started recording session {self.session_id}")
        return self.session_id
    
    def record_agent_action(self, agent_name: str, action: str, 
                           input_data: Any, output_data: Any,
                           metadata: Dict = None) -> None:
        """
        Record an agent performing an action
        
        Args:
            agent_name: Name of the agent (pm, dev, qa, etc.)
            action: What the agent did
            input_data: What the agent received
            output_data: What the agent produced
            metadata: Additional context
        """
        event = {
            "type": "agent_action",
            "timestamp": datetime.now().isoformat(),
            "agent": agent_name,
            "action": action,
            "input_summary": self._summarize_data(input_data),
            "output_summary": self._summarize_data(output_data),
            "duration_ms": metadata.get("duration_ms") if metadata else None,
            "metadata": metadata or {}
        }
        
        self._record_event(event)
        
        # Print real-time update
        print(f"   📜 [{agent_name}] {action}")
    
    def record_handoff(self, from_agent: str, to_agent: str,
                      artifact_name: str, artifact_summary: str) -> None:
        """
        Record a handoff between two agents
        
        Example: PM hands off spec to Dev
        """
        event = {
            "type": "handoff",
            "timestamp": datetime.now().isoformat(),
            "from_agent": from_agent,
            "to_agent": to_agent,
            "artifact": artifact_name,
            "artifact_summary": artifact_summary
        }
        
        self._record_event(event)
        
        # Visual handoff indicator
        print(f"   📜 🤝 {from_agent} → {to_agent}: {artifact_name}")
    
    def record_decision(self, agent_name: str, decision: str,
                       rationale: str, alternatives_considered: List[str] = None) -> None:
        """Record why an agent made a particular decision"""
        event = {
            "type": "decision",
            "timestamp": datetime.now().isoformat(),
            "agent": agent_name,
            "decision": decision,
            "rationale": rationale,
            "alternatives": alternatives_considered or []
        }
        
        self._record_event(event)
    
    def record_collaboration(self, agents: List[str], activity: str,
                            result: str) -> None:
        """Record multiple agents collaborating"""
        event = {
            "type": "collaboration",
            "timestamp": datetime.now().isoformat(),
            "agents": agents,
            "activity": activity,
            "result": result
        }
        
        self._record_event(event)
        
        agents_str = " + ".join(agents)
        print(f"   📜 🤝 {agents_str} collaborated: {activity}")
    
    def record_checkpoint(self, stage: str, status: str, 
                         metrics: Dict = None) -> None:
        """Record a pipeline checkpoint"""
        event = {
            "type": "checkpoint",
            "timestamp": datetime.now().isoformat(),
            "stage": stage,
            "status": status,
            "metrics": metrics or {},
            "elapsed_seconds": time.time() - self.start_time if self.start_time else 0
        }
        
        self._record_event(event)
        
        status_icon = "✅" if status == "success" else "⚠️" if status == "warning" else "❌"
        print(f"   📜 {status_icon} Checkpoint: {stage} - {status}")
    
    def record_issue(self, agent_name: str, issue_type: str,
                    description: str, resolution: str = None) -> None:
        """Record an issue and its resolution"""
        event = {
            "type": "issue",
            "timestamp": datetime.now().isoformat(),
            "agent": agent_name,
            "issue_type": issue_type,
            "description": description,
            "resolution": resolution,
            "resolved": resolution is not None
        }
        
        self._record_event(event)
        
        status = "✅" if resolution else "❌"
        print(f"   📜 {status} Issue [{agent_name}]: {issue_type}")
    
    def end_session(self, final_status: str = "completed") -> Dict:
        """End the recording session and generate final report"""
        duration = time.time() - self.start_time if self.start_time else 0
        
        self._record_event({
            "type": "session_end",
            "timestamp": datetime.now().isoformat(),
            "final_status": final_status,
            "total_duration_seconds": duration,
            "total_events": len(self.event_log)
        })
        
        # Generate comprehensive report
        report = self._generate_report()
        
        # Save everything
        self._save_chronicle(report)
        
        print(f"📜 Chronicle: Session ended - {final_status}")
        print(f"   Total events recorded: {len(self.event_log)}")
        print(f"   Duration: {duration:.1f}s")
        
        return report
    
    def _record_event(self, event: Dict) -> None:
        """Thread-safe event recording"""
        with self.lock:
            event["sequence_number"] = len(self.event_log) + 1
            self.event_log.append(event)
    
    def _summarize_data(self, data: Any, max_length: int = 200) -> str:
        """Create a concise summary of data"""
        if data is None:
            return "None"
        
        if isinstance(data, str):
            if len(data) > max_length:
                return data[:max_length] + "..."
            return data
        
        if isinstance(data, dict):
            keys = list(data.keys())[:5]
            return f"Dict with keys: {', '.join(keys)}"
        
        if isinstance(data, list):
            return f"List with {len(data)} items"
        
        return str(data)[:max_length]
    
    def _generate_report(self) -> Dict:
        """Generate comprehensive collaboration report"""
        
        # Analyze event log
        agent_actions = {}
        handoffs = []
        decisions = []
        issues = []
        collaboration_patterns = []
        
        for event in self.event_log:
            if event["type"] == "agent_action":
                agent = event["agent"]
                if agent not in agent_actions:
                    agent_actions[agent] = []
                agent_actions[agent].append(event)
            
            elif event["type"] == "handoff":
                handoffs.append(event)
            
            elif event["type"] == "decision":
                decisions.append(event)
            
            elif event["type"] == "issue":
                issues.append(event)
            
            elif event["type"] == "collaboration":
                collaboration_patterns.append(event)
        
        # Calculate metrics
        total_duration = time.time() - self.start_time if self.start_time else 0
        
        report = {
            "session_id": self.session_id,
            "generated_at": datetime.now().isoformat(),
            "summary": {
                "total_events": len(self.event_log),
                "total_agents_involved": len(agent_actions),
                "total_handoffs": len(handoffs),
                "total_decisions": len(decisions),
                "total_issues": len(issues),
                "total_collaborations": len(collaboration_patterns),
                "duration_seconds": total_duration
            },
            "agent_statistics": self._calculate_agent_stats(agent_actions),
            "timeline": self._generate_timeline(),
            "handoff_chain": self._visualize_handoffs(handoffs),
            "decision_log": decisions,
            "issues_encountered": issues,
            "collaboration_patterns": collaboration_patterns,
            "bottlenecks": self._identify_bottlenecks(),
            "recommendations": self._generate_recommendations()
        }
        
        return report
    
    def _calculate_agent_stats(self, agent_actions: Dict) -> Dict:
        """Calculate statistics for each agent"""
        stats = {}
        
        for agent, actions in agent_actions.items():
            total_duration = sum(
                a.get("duration_ms", 0) for a in actions if a.get("duration_ms")
            )
            
            stats[agent] = {
                "actions_count": len(actions),
                "total_duration_ms": total_duration,
                "avg_duration_ms": total_duration / len(actions) if actions else 0,
                "actions": [a["action"] for a in actions[:5]]  # Sample actions
            }
        
        return stats
    
    def _generate_timeline(self) -> List[Dict]:
        """Generate a visual timeline of events"""
        timeline = []
        
        for event in self.event_log:
            timeline.append({
                "time": event["timestamp"],
                "sequence": event.get("sequence_number", 0),
                "type": event["type"],
                "description": self._describe_event(event)
            })
        
        return timeline
    
    def _describe_event(self, event: Dict) -> str:
        """Create human-readable description of an event"""
        event_type = event["type"]
        
        if event_type == "agent_action":
            return f"{event['agent']} performed: {event['action']}"
        
        elif event_type == "handoff":
            return f"{event['from_agent']} passed {event['artifact']} to {event['to_agent']}"
        
        elif event_type == "decision":
            return f"{event['agent']} decided: {event['decision']}"
        
        elif event_type == "collaboration":
            agents = " + ".join(event["agents"])
            return f"{agents} collaborated on: {event['activity']}"
        
        elif event_type == "issue":
            status = "RESOLVED" if event["resolved"] else "UNRESOLVED"
            return f"Issue [{event['agent']}]: {event['issue_type']} ({status})"
        
        elif event_type == "checkpoint":
            return f"Checkpoint: {event['stage']} - {event['status']}"
        
        return f"{event_type}: {event.get('action', 'unknown')}"
    
    def _visualize_handoffs(self, handoffs: List[Dict]) -> str:
        """Create ASCII visualization of handoffs"""
        if not handoffs:
            return "No handoffs recorded"
        
        lines = []
        lines.append("\n📋 Handoff Chain:\n")
        
        for i, handoff in enumerate(handoffs, 1):
            from_agent = handoff["from_agent"]
            to_agent = handoff["to_agent"]
            artifact = handoff["artifact"]
            
            lines.append(f"   Step {i}:")
            lines.append(f"   ┌─ {from_agent}")
            lines.append(f"   │  creates: {artifact}")
            lines.append(f"   ↓")
            lines.append(f"   └─ {to_agent} receives")
            lines.append("")
        
        return "\n".join(lines)
    
    def _identify_bottlenecks(self) -> List[Dict]:
        """Identify bottlenecks in the pipeline"""
        bottlenecks = []
        
        # Find long-duration actions
        for event in self.event_log:
            if event["type"] == "agent_action" and event.get("duration_ms"):
                if event["duration_ms"] > 60000:  # > 1 minute
                    bottlenecks.append({
                        "type": "long_execution",
                        "agent": event["agent"],
                        "action": event["action"],
                        "duration_ms": event["duration_ms"],
                        "recommendation": "Consider optimizing or parallelizing this step"
                    })
        
        # Find unresolved issues
        unresolved = [e for e in self.event_log if e["type"] == "issue" and not e.get("resolved")]
        if unresolved:
            bottlenecks.append({
                "type": "unresolved_issues",
                "count": len(unresolved),
                "issues": [e["description"] for e in unresolved],
                "recommendation": "Resolve outstanding issues before deployment"
            })
        
        return bottlenecks
    
    def _generate_recommendations(self) -> List[str]:
        """Generate recommendations based on the chronicle"""
        recommendations = []
        
        # Analyze handoffs
        handoff_events = [e for e in self.event_log if e["type"] == "handoff"]
        if len(handoff_events) > 5:
            recommendations.append("Consider parallelizing some agent tasks to reduce sequential handoffs")
        
        # Check for retry patterns
        retry_actions = {}
        for event in self.event_log:
            if event["type"] == "agent_action":
                key = (event["agent"], event["action"])
                retry_actions[key] = retry_actions.get(key, 0) + 1
        
        for (agent, action), count in retry_actions.items():
            if count > 3:
                recommendations.append(f"{agent} performed '{action}' {count} times - consider caching or optimization")
        
        # General recommendations
        recommendations.extend([
            "All agent interactions were logged successfully",
            "Review the handoff chain for potential optimizations",
            "Consider adding more granular checkpoints for better visibility"
        ])
        
        return recommendations
    
    def _save_chronicle(self, report: Dict) -> None:
        """Save the chronicle to disk"""
        # Save JSON report
        json_path = self.chronicle_dir / f"{self.session_id}.json"
        with open(json_path, 'w') as f:
            json.dump(report, f, indent=2)
        
        # Generate Markdown narrative
        md_path = self.chronicle_dir / f"{self.session_id}_narrative.md"
        with open(md_path, 'w') as f:
            f.write(self._generate_narrative(report))
        
        print(f"   📜 Chronicle saved:")
        print(f"      JSON: {json_path}")
        print(f"      Narrative: {md_path}")
    
    def _generate_narrative(self, report: Dict) -> str:
        """Generate a human-readable narrative of the session"""
        summary = report["summary"]
        
        narrative = f"""# 📜 Chronicle Narrative

## Session: {report['session_id']}
**Generated:** {report['generated_at']}

---

## Executive Summary

This session involved **{summary['total_agents_involved']} agents** collaborating over **{summary['duration_seconds']:.1f} seconds**.

- 📝 **{summary['total_events']}** events recorded
- 🤝 **{summary['total_handoffs']}** handoffs between agents
- 💡 **{summary['total_decisions']}** decisions made
- ⚠️ **{summary['total_issues']}** issues encountered
- 🤝 **{summary['total_collaborations']}** collaboration events

---

## Agent Performance

"""
        
        for agent, stats in report["agent_statistics"].items():
            narrative += f"### {agent.upper()}\n"
            narrative += f"- Actions: {stats['actions_count']}\n"
            narrative += f"- Total time: {stats['total_duration_ms']/1000:.1f}s\n"
            narrative += f"- Average time per action: {stats['avg_duration_ms']:.0f}ms\n"
            narrative += f"- Sample actions: {', '.join(stats['actions'])}\n\n"
        
        narrative += f"""
---

## Timeline of Events

"""
        
        for event in report["timeline"][:20]:  # First 20 events
            narrative += f"**{event['sequence']}.** [{event['time']}] {event['description']}\n\n"
        
        if len(report["timeline"]) > 20:
            narrative += f"... and {len(report['timeline']) - 20} more events\n\n"
        
        narrative += f"""
---

## Handoff Chain

{report['handoff_chain']}

---

## Decisions Made

"""
        
        for decision in report["decision_log"]:
            narrative += f"**{decision['agent']}** decided:\n"
            narrative += f"> {decision['decision']}\n\n"
            narrative += f"*Rationale:* {decision['rationale']}\n\n"
            if decision['alternatives']:
                narrative += f"*Alternatives considered:* {', '.join(decision['alternatives'])}\n\n"
            narrative += "---\n\n"
        
        if report["issues_encountered"]:
            narrative += f"""
## Issues Encountered

"""
            for issue in report["issues_encountered"]:
                status = "✅ Resolved" if issue['resolved'] else "❌ Unresolved"
                narrative += f"- **{issue['issue_type']}** ({status})\n"
                narrative += f"  - Agent: {issue['agent']}\n"
                narrative += f"  - {issue['description']}\n"
                if issue['resolution']:
                    narrative += f"  - Resolution: {issue['resolution']}\n"
                narrative += "\n"
        
        if report["bottlenecks"]:
            narrative += f"""
## Bottlenecks Identified

"""
            for bottleneck in report["bottlenecks"]:
                narrative += f"- **{bottleneck['type']}**\n"
                narrative += f"  - {bottleneck.get('recommendation', 'No recommendation')}\n\n"
        
        narrative += f"""
## Recommendations

"""
        for rec in report["recommendations"]:
            narrative += f"- {rec}\n"
        
        narrative += f"""

---

## Key Insights

### How Agents Collaborated

"""
        
        for collab in report["collaboration_patterns"]:
            agents = " + ".join(collab["agents"])
            narrative += f"- **{agents}** worked together on: {collab['activity']}\n"
            narrative += f"  - Result: {collab['result']}\n\n"
        
        narrative += f"""
### Workflow Pattern

"""
        
        # Describe the workflow pattern
        handoffs = report["handoff_chain"]
        if "PM" in str(handoffs) and "Dev" in str(handoffs):
            narrative += """The pipeline followed a **waterfall-like pattern**:
1. PM created specifications
2. Dev implemented based on specs
3. QA tested the implementation
4. Deploy shipped to production

This is a traditional sequential workflow suitable for well-defined projects.
"""
        
        narrative += f"""
---

*Recorded by Chronicle Agent v1.0*  
*"Preserving the history of AI collaboration"*
"""
        
        return narrative


def get_chronicle_agent(config_path: str = "config/.env") -> ChronicleAgent:
    """Get or create Chronicle agent singleton"""
    # Simple singleton pattern
    if not hasattr(get_chronicle_agent, '_instance'):
        get_chronicle_agent._instance = ChronicleAgent(config_path)
    return get_chronicle_agent._instance


if __name__ == "__main__":
    import sys
    
    # Demo mode
    chronicle = ChronicleAgent()
    
    if len(sys.argv) > 1 and sys.argv[1] == "demo":
        print("📜 Chronicle Agent Demo Mode\n")
        
        # Start session
        chronicle.start_session("demo_feature", "demo")
        
        # Simulate agent actions
        chronicle.record_agent_action("web_scraper", "market_research", 
                                     "task management app", 
                                     "6 competitors found",
                                     {"duration_ms": 5000})
        
        chronicle.record_handoff("web_scraper", "pm", 
                                "market_research_report", 
                                "6 competitors, 8 pain points")
        
        chronicle.record_agent_action("pm", "create_specification",
                                     "market research",
                                     "feature_spec.json",
                                     {"duration_ms": 8000})
        
        chronicle.record_decision("pm", "Use React + Node.js",
                                 "Best fit for team expertise",
                                 ["Vue + Django", "Angular + Java"])
        
        chronicle.record_handoff("pm", "dev", "feature_spec", "6 user stories, API spec")
        
        chronicle.record_agent_action("dev", "generate_code",
                                     "feature spec",
                                     "codebase/ with 20 files",
                                     {"duration_ms": 45000})
        
        chronicle.record_checkpoint("development", "success", {"files": 20})
        
        # End and generate report
        report = chronicle.end_session("success")
        
        print(f"\n📊 Report generated with {report['summary']['total_events']} events")
    else:
        print("Usage: python3 chronicle_agent.py demo")
        print("\nThe Chronicle Agent records all agent interactions.")
        print("It's automatically used by the pipeline orchestrator.")
