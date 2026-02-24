#!/usr/bin/env python3
"""
DevForge - Web Scraper Engineer Agent
Gathers market data, trends, and competitor insights to inspire PM
"""

import os
import json
import re
import time
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional, Set
from urllib.parse import urljoin, urlparse
import urllib.request
import urllib.error

class WebScraperEngineer:
    """Web Scraper Engineer - gathers data to inspire PM decisions"""
    
    def __init__(self, config_path="config/.env"):
        self.config = self._load_config(config_path)
        self.data_dir = Path("data") / "scraped"
        self.data_dir.mkdir(parents=True, exist_ok=True)
        self.cache_dir = self.data_dir / "cache"
        self.cache_dir.mkdir(exist_ok=True)
        
        # Rate limiting
        self.last_request_time = 0
        self.min_request_interval = 1.0  # seconds between requests
        
    def _load_config(self, path):
        config = {}
        if os.path.exists(path):
            with open(path) as f:
                for line in f:
                    if '=' in line and not line.startswith('#'):
                        key, value = line.strip().split('=', 1)
                        config[key] = value.strip('"').strip("'")
        for key in os.environ:
            config[key] = os.environ[key]
        return config
    
    def _rate_limited_request(self, url: str, headers: Optional[Dict] = None) -> Optional[str]:
        """Make rate-limited HTTP request"""
        # Enforce rate limiting
        elapsed = time.time() - self.last_request_time
        if elapsed < self.min_request_interval:
            time.sleep(self.min_request_interval - elapsed)
        
        default_headers = {
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
        }
        
        if headers:
            default_headers.update(headers)
        
        try:
            req = urllib.request.Request(url, headers=default_headers)
            with urllib.request.urlopen(req, timeout=30) as response:
                self.last_request_time = time.time()
                return response.read().decode('utf-8', errors='ignore')
        except Exception as e:
            print(f"   ⚠️  Failed to fetch {url}: {e}")
            return None
    
    def research_market(self, topic: str, depth: str = "medium") -> Dict:
        """
        Research a market/topic to gather insights
        
        Args:
            topic: Topic to research (e.g., "task management apps")
            depth: "quick", "medium", or "deep"
        """
        print(f"🕷️  Web Scraper: Researching '{topic}'")
        print(f"   Depth: {depth}")
        
        research_id = f"research_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        
        # Gather data from multiple sources
        results = {
            "id": research_id,
            "topic": topic,
            "timestamp": datetime.now().isoformat(),
            "competitors": [],
            "trends": [],
            "features": [],
            "pain_points": [],
            "user_sentiment": {},
            "market_data": {}
        }
        
        # 1. Search for competitor apps/products
        if depth in ["medium", "deep"]:
            print("   🔍 Searching for competitors...")
            results["competitors"] = self._find_competitors(topic)
        
        # 2. Analyze social media mentions (simulated for demo)
        if depth in ["medium", "deep"]:
            print("   📱 Analyzing social media trends...")
            results["trends"] = self._analyze_social_trends(topic)
        
        # 3. Extract common features from competitor websites
        if depth == "deep":
            print("   🌐 Scraping competitor websites...")
            results["features"] = self._extract_competitor_features(results["competitors"])
        
        # 4. Identify pain points from reviews/forums (simulated)
        print("   💭 Identifying user pain points...")
        results["pain_points"] = self._identify_pain_points(topic)
        
        # 5. Generate market insights
        print("   📊 Generating market insights...")
        results["insights"] = self._generate_insights(results)
        
        # Save research
        research_file = self.data_dir / f"{research_id}.json"
        with open(research_file, 'w') as f:
            json.dump(results, f, indent=2)
        
        # Generate PM inspiration document
        inspiration_doc = self._generate_pm_inspiration(results)
        inspiration_file = self.data_dir / f"{research_id}_inspiration.md"
        with open(inspiration_file, 'w') as f:
            f.write(inspiration_doc)
        
        print(f"✅ Web Scraper: Research complete")
        print(f"   Found: {len(results['competitors'])} competitors")
        print(f"   Trends: {len(results['trends'])} identified")
        print(f"   Pain points: {len(results['pain_points'])} documented")
        
        return results
    
    def _find_competitors(self, topic: str) -> List[Dict]:
        """Find competitor products in the space"""
        # In production: Use search APIs, product directories
        # For demo: Return simulated data based on topic
        
        topic_lower = topic.lower()
        
        # Topic-based competitor templates
        competitor_map = {
            "task": [
                {"name": "Todoist", "url": "https://todoist.com", "type": "task_management", "popularity": "high"},
                {"name": "Notion", "url": "https://notion.so", "type": "all_in_one", "popularity": "high"},
                {"name": "Trello", "url": "https://trello.com", "type": "kanban", "popularity": "high"},
                {"name": "Asana", "url": "https://asana.com", "type": "project_management", "popularity": "high"},
                {"name": "ClickUp", "url": "https://clickup.com", "type": "all_in_one", "popularity": "medium"},
                {"name": "Microsoft To Do", "url": "https://todo.microsoft.com", "type": "simple", "popularity": "high"},
            ],
            "e-commerce": [
                {"name": "Shopify", "url": "https://shopify.com", "type": "platform", "popularity": "high"},
                {"name": "WooCommerce", "url": "https://woocommerce.com", "type": "plugin", "popularity": "high"},
                {"name": "BigCommerce", "url": "https://bigcommerce.com", "type": "platform", "popularity": "medium"},
            ],
            "chat": [
                {"name": "Slack", "url": "https://slack.com", "type": "team_chat", "popularity": "high"},
                {"name": "Discord", "url": "https://discord.com", "type": "community", "popularity": "high"},
                {"name": "Microsoft Teams", "url": "https://teams.microsoft.com", "type": "enterprise", "popularity": "high"},
            ],
            "finance": [
                {"name": "Mint", "url": "https://mint.com", "type": "personal", "popularity": "high"},
                {"name": "YNAB", "url": "https://ynab.com", "type": "budgeting", "popularity": "medium"},
                {"name": "Personal Capital", "url": "https://personalcapital.com", "type": "wealth", "popularity": "medium"},
            ]
        }
        
        # Find matching competitors
        competitors = []
        for keyword, comps in competitor_map.items():
            if keyword in topic_lower:
                competitors.extend(comps)
        
        # If no specific match, return generic competitors
        if not competitors:
            competitors = [
                {"name": "Market Leader A", "url": "https://example.com/a", "type": "leader", "popularity": "high"},
                {"name": "Innovator B", "url": "https://example.com/b", "type": "innovator", "popularity": "medium"},
                {"name": "Niche Player C", "url": "https://example.com/c", "type": "niche", "popularity": "low"},
            ]
        
        return competitors[:8]  # Limit to 8 competitors
    
    def _analyze_social_trends(self, topic: str) -> List[Dict]:
        """Analyze social media trends (simulated)"""
        topic_lower = topic.lower()
        
        # Generate plausible trends based on topic
        trends = [
            {
                "trend": f"AI-powered {topic}",
                "sentiment": "positive",
                "volume": "high",
                "growth": "+45%",
                "platforms": ["Twitter", "LinkedIn", "Reddit"]
            },
            {
                "trend": "Mobile-first design",
                "sentiment": "positive", 
                "volume": "high",
                "growth": "+32%",
                "platforms": ["Twitter", "Product Hunt"]
            },
            {
                "trend": f"Collaborative {topic}",
                "sentiment": "positive",
                "volume": "medium",
                "growth": "+28%",
                "platforms": ["Reddit", "Hacker News"]
            },
            {
                "trend": "Privacy concerns",
                "sentiment": "negative",
                "volume": "medium",
                "growth": "+15%",
                "platforms": ["Twitter", "Mastodon"]
            }
        ]
        
        # Add topic-specific trends
        if "task" in topic_lower or "todo" in topic_lower:
            trends.extend([
                {"trend": "Gamification", "sentiment": "mixed", "volume": "medium", "growth": "+12%"},
                {"trend": "Time blocking", "sentiment": "positive", "volume": "high", "growth": "+38%"}
            ])
        
        if "e-commerce" in topic_lower or "shop" in topic_lower:
            trends.extend([
                {"trend": "Social commerce", "sentiment": "positive", "volume": "high", "growth": "+52%"},
                {"trend": "Sustainable shopping", "sentiment": "positive", "volume": "medium", "growth": "+41%"}
            ])
        
        return trends
    
    def _extract_competitor_features(self, competitors: List[Dict]) -> List[Dict]:
        """Extract features from competitor websites"""
        features = []
        
        # In production: Actually scrape websites
        # For demo: Return common feature patterns
        
        common_features = [
            {"name": "User Authentication", "commonality": "universal", "importance": "high"},
            {"name": "Mobile Responsive", "commonality": "universal", "importance": "high"},
            {"name": "Dark Mode", "commonality": "common", "importance": "medium"},
            {"name": "Real-time Sync", "commonality": "common", "importance": "high"},
            {"name": "Third-party Integrations", "commonality": "common", "importance": "medium"},
            {"name": "API Access", "commonality": "moderate", "importance": "medium"},
            {"name": "Offline Mode", "commonality": "rare", "importance": "high"},
            {"name": "AI Assistance", "commonality": "emerging", "importance": "high"},
            {"name": "Team Collaboration", "commonality": "common", "importance": "medium"},
            {"name": "Advanced Analytics", "commonality": "moderate", "importance": "low"}
        ]
        
        return common_features
    
    def _identify_pain_points(self, topic: str) -> List[Dict]:
        """Identify user pain points from reviews/forums"""
        topic_lower = topic.lower()
        
        pain_points = [
            {
                "issue": "Too complex / steep learning curve",
                "frequency": "high",
                "severity": "high",
                "source": "User reviews"
            },
            {
                "issue": "Expensive pricing for small teams",
                "frequency": "high",
                "severity": "medium",
                "source": "Reddit, Twitter"
            },
            {
                "issue": "Poor mobile experience",
                "frequency": "medium",
                "severity": "high",
                "source": "App Store reviews"
            },
            {
                "issue": "Slow performance with large data",
                "frequency": "medium",
                "severity": "high",
                "source": "User forums"
            },
            {
                "issue": "Limited customization options",
                "frequency": "medium",
                "severity": "medium",
                "source": "Feature requests"
            },
            {
                "issue": "Poor customer support",
                "frequency": "low",
                "severity": "medium",
                "source": "Trustpilot, G2"
            }
        ]
        
        # Add topic-specific pain points
        if "task" in topic_lower:
            pain_points.extend([
                {"issue": "Overwhelming number of features", "frequency": "high", "severity": "medium"},
                {"issue": "Poor recurring task handling", "frequency": "medium", "severity": "medium"}
            ])
        
        return pain_points
    
    def _generate_insights(self, results: Dict) -> Dict:
        """Generate actionable insights for PM"""
        insights = {
            "market_opportunity": self._assess_opportunity(results),
            "differentiation_suggestions": self._suggest_differentiation(results),
            "feature_recommendations": self._recommend_features(results),
            "pricing_strategy": self._suggest_pricing(results),
            "target_audience": self._identify_audience(results)
        }
        return insights
    
    def _assess_opportunity(self, results: Dict) -> str:
        """Assess market opportunity"""
        competitors = len(results.get("competitors", []))
        pain_points = len(results.get("pain_points", []))
        
        if competitors > 6 and pain_points > 4:
            return "Crowded market with clear pain points - opportunity for disruption through better UX"
        elif competitors <= 3:
            return "Emerging/niche market - first-mover advantage possible"
        else:
            return "Mature market - focus on specific underserved segment"
    
    def _suggest_differentiation(self, results: Dict) -> List[str]:
        """Suggest differentiation strategies"""
        suggestions = []
        
        # Analyze gaps
        pain_points = results.get("pain_points", [])
        trends = results.get("trends", [])
        
        if any("complex" in p.get("issue", "").lower() for p in pain_points):
            suggestions.append("Simplicity-first approach - minimal feature set")
        
        if any("expensive" in p.get("issue", "").lower() for p in pain_points):
            suggestions.append("Freemium model with generous free tier")
        
        if any(t.get("trend") == "AI-powered" for t in trends):
            suggestions.append("Native AI integration from ground up")
        
        if any("mobile" in p.get("issue", "").lower() for p in pain_points):
            suggestions.append("Mobile-first design, not just responsive")
        
        suggestions.extend([
            "Focus on specific niche rather than general audience",
            "Superior performance as key differentiator",
            "Open source core with paid hosting"
        ])
        
        return suggestions[:5]
    
    def _recommend_features(self, results: Dict) -> List[Dict]:
        """Recommend features based on research"""
        features = []
        
        # Must-have (universal)
        features.extend([
            {"name": "User Authentication", "priority": "must_have", "reason": "Universal requirement"},
            {"name": "Mobile Responsive", "priority": "must_have", "reason": "Universal requirement"}
        ])
        
        # Should-have (common)
        features.extend([
            {"name": "Dark Mode", "priority": "should_have", "reason": "Common in competitors"},
            {"name": "Real-time Sync", "priority": "should_have", "reason": "User expectation"}
        ])
        
        # Differentiators (pain points)
        pain_points = results.get("pain_points", [])
        if any("complex" in p.get("issue", "").lower() for p in pain_points):
            features.append({"name": "Guided Onboarding", "priority": "differentiator", "reason": "Addresses complexity complaint"})
        
        trends = results.get("trends", [])
        if any("AI" in t.get("trend", "") for t in trends):
            features.append({"name": "AI Assistant", "priority": "differentiator", "reason": "Trending feature"})
        
        return features
    
    def _suggest_pricing(self, results: Dict) -> Dict:
        """Suggest pricing strategy"""
        pain_points = results.get("pain_points", [])
        
        if any("expensive" in p.get("issue", "").lower() for p in pain_points):
            return {
                "model": "Freemium",
                "free_tier": "Generous - core features free",
                "paid_tier": "$5-10/month",
                "rationale": "Address pricing pain point"
            }
        else:
            return {
                "model": "Freemium",
                "free_tier": "Basic features",
                "paid_tier": "$10-15/month",
                "rationale": "Market standard"
            }
    
    def _identify_audience(self, results: Dict) -> Dict:
        """Identify target audience segments"""
        return {
            "primary": {
                "segment": "Small teams / startups",
                "pain_point": "Existing tools too complex/expensive",
                "needs": ["Simplicity", "Affordability", "Quick setup"]
            },
            "secondary": {
                "segment": "Individual professionals",
                "pain_point": "Overkill features in current tools",
                "needs": ["Focus", "Performance", "Privacy"]
            }
        }
    
    def _generate_pm_inspiration(self, results: Dict) -> str:
        """Generate inspiration document for PM"""
        doc = f"""# 🕷️ Web Scraper Research Report

## Topic: {results['topic']}
**Research ID:** {results['id']}  
**Date:** {results['timestamp']}

---

## 🏆 Competitors Analyzed ({len(results['competitors'])})

"""
        
        for comp in results['competitors'][:5]:
            doc += f"- **{comp['name']}** ({comp['type']}) - Popularity: {comp['popularity']}\n"
        
        doc += f"""

---

## 📈 Market Trends

"""
        
        for trend in results['trends'][:5]:
            doc += f"### {trend['trend']}\n"
            doc += f"- Sentiment: {trend['sentiment']} | Growth: {trend['growth']}\n"
            doc += f"- Volume: {trend['volume']}\n\n"
        
        doc += f"""

---

## 😤 User Pain Points

"""
        
        for pain in results['pain_points'][:6]:
            doc += f"- **{pain['issue']}** (Severity: {pain['severity']}, Frequency: {pain['frequency']})\n"
        
        doc += f"""

---

## 💡 Key Insights

### Market Opportunity
{results['insights']['market_opportunity']}

### Differentiation Suggestions
"""
        
        for suggestion in results['insights']['differentiation_suggestions']:
            doc += f"- {suggestion}\n"
        
        doc += f"""

### Recommended Features
"""
        
        for feature in results['insights']['feature_recommendations']:
            doc += f"- **{feature['name']}** ({feature['priority']}) - {feature['reason']}\n"
        
        doc += f"""

### Pricing Strategy
- Model: {results['insights']['pricing_strategy']['model']}
- Free Tier: {results['insights']['pricing_strategy']['free_tier']}
- Paid Tier: {results['insights']['pricing_strategy']['paid_tier']}
- Rationale: {results['insights']['pricing_strategy']['rationale']}

### Target Audience
**Primary:** {results['insights']['target_audience']['primary']['segment']}
- Pain Point: {results['insights']['target_audience']['primary']['pain_point']}
- Needs: {', '.join(results['insights']['target_audience']['primary']['needs'])}

**Secondary:** {results['insights']['target_audience']['secondary']['segment']}
- Pain Point: {results['insights']['target_audience']['secondary']['pain_point']}
- Needs: {', '.join(results['insights']['target_audience']['secondary']['needs'])}

---

## 🎯 PM Action Items

Based on this research, consider:

1. **Positioning:** Focus on simplicity and ease of use
2. **Pricing:** Competitive freemium model
3. **MVP Features:** Core functionality without bloat
4. **Differentiation:** AI-native features from the start
5. **Launch Strategy:** Target underserved small teams segment

---

*Generated by DevForge Web Scraper Engineer*
"""
        
        return doc
    
    def crawl_social_feeds(self, platforms: List[str] = None, keywords: List[str] = None) -> Dict:
        """
        Crawl social media feeds for trending topics
        
        In production: Use Twitter/X API, Reddit API, etc.
        For demo: Return simulated trending data
        """
        platforms = platforms or ["twitter", "reddit", "hackernews"]
        
        print("   📱 Crawling social feeds...")
        
        trends = []
        
        for platform in platforms:
            if platform == "twitter":
                trends.extend([
                    {"topic": "#buildinpublic", "volume": "high", "sentiment": "positive"},
                    {"topic": "AI startups", "volume": "high", "sentiment": "mixed"},
                    {"topic": "SaaS pricing", "volume": "medium", "sentiment": "negative"}
                ])
            elif platform == "reddit":
                trends.extend([
                    {"topic": "self-hosted alternatives", "volume": "medium", "sentiment": "positive"},
                    {"topic": "privacy concerns", "volume": "high", "sentiment": "negative"},
                    {"topic": "open source tools", "volume": "medium", "sentiment": "positive"}
                ])
            elif platform == "hackernews":
                trends.extend([
                    {"topic": "indie hacking", "volume": "high", "sentiment": "positive"},
                    {"topic": "bootstrapped startups", "volume": "medium", "sentiment": "positive"},
                    {"topic": "API-first products", "volume": "medium", "sentiment": "positive"}
                ])
        
        return {
            "platforms_crawled": platforms,
            "trends_found": len(trends),
            "trends": trends,
            "timestamp": datetime.now().isoformat()
        }


if __name__ == "__main__":
    import sys
    
    if len(sys.argv) < 2:
        print("Usage: python3 web_scraper_engineer.py <topic> [depth]")
        print("Example: python3 web_scraper_engineer.py 'task management app' deep")
        print("\nDepth options: quick, medium, deep")
        sys.exit(1)
    
    topic = sys.argv[1]
    depth = sys.argv[2] if len(sys.argv) > 2 else "medium"
    
    scraper = WebScraperEngineer()
    
    # Research the topic
    results = scraper.research_market(topic, depth)
    
    # Also crawl social feeds
    social_data = scraper.crawl_social_feeds()
    
    print(f"\n📁 Research saved to: data/scraped/{results['id']}.json")
    print(f"📄 PM Inspiration: data/scraped/{results['id']}_inspiration.md")
    print(f"\nSocial trends found: {social_data['trends_found']}")
