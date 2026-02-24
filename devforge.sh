#!/bin/bash
# DevForge Pipeline - Main Orchestrator
# Coordinates PM, Developer, QA, and Deploy agents

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

echo "🚀 DevForge Pipeline - Multi-Agent Software Development"
echo "========================================================"
echo ""

# Check Python
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 not found. Please install Python 3.8+"
    exit 1
fi

# Check config
if [ ! -f "config/.env" ]; then
    echo "⚙️  Creating configuration file..."
    cp config/.env.example config/.env 2>/dev/null || echo "# Add your API keys here" > config/.env
    echo "✅ Created config/.env"
    echo ""
    echo "📝 Please edit config/.env and add your API keys:"
    echo "   - OPENAI_API_KEY (for GPT code generation)"
    echo "   - ANTHROPIC_API_KEY (for Claude PM/Dev)"
    echo "   - GEMINI_API_KEY (for testing)"
    echo ""
fi

# Display pipeline status
echo "📊 Pipeline Status:"
echo "-------------------"

# Count features
FEATURE_COUNT=$(ls -1 projects/ 2>/dev/null | wc -l | tr -d ' ')
echo "Features: $FEATURE_COUNT"

# Count deployments
DEPLOY_COUNT=$(ls -1 data/deployments/ 2>/dev/null | wc -l | tr -d ' ')
echo "Deployments: $DEPLOY_COUNT"

echo ""
echo "Available Commands:"
echo "-------------------"
echo ""
echo "1. PM Agent - Generate feature specification:"
echo "   python3 agents/pm/pm_agent.py 'Your app idea' 'React, Node.js'"
echo ""
echo "2. Reverse Engineer - Analyze existing code:"
echo "   python3 agents/re/reverse_engineer_agent.py /path/to/project"
echo ""
echo "3. Dev Agent - Develop the feature:"
echo "   python3 agents/dev/dev_agent.py feat_YYYYMMDD_XXXX"
echo ""
echo "4. QA Agent - Test the implementation:"
echo "   python3 agents/qa/qa_agent.py feat_YYYYMMDD_XXXX unit integration"
echo ""
echo "5. Deploy Agent - Deploy to environment:"
echo "   python3 agents/deploy/deploy_agent.py feat_YYYYMMDD_XXXX staging docker"
echo ""
echo "6. Full Pipeline - Run all agents:"
echo "   ./devforge.sh full 'Your app idea'"
echo ""
echo "7. Reverse Engineer + Rebuild - Analyze and rebuild:"
echo "   ./devforge.sh reverse https://github.com/user/repo"
echo ""

# Show recent features
if [ "$FEATURE_COUNT" -gt 0 ]; then
    echo "Recent Features:"
    echo "---------------"
    ls -lt projects/ 2>/dev/null | head -6 | tail -5 | awk '{print "  " $9}'
    echo ""
fi

# Interactive menu if no arguments
if [ $# -eq 0 ]; then
    echo "Quick Actions:"
    echo "------------"
    select action in "Create Feature (PM)" "Reverse Engineer Codebase" "Develop Feature" "Test Feature" "Deploy Feature" "Full Pipeline" "Exit"; do
        case $action in
            "Create Feature (PM)")
                read -p "Enter your app idea: " idea
                read -p "Tech stack (optional, e.g., 'React, Node.js'): " stack
                python3 agents/pm/pm_agent.py "$idea" "$stack"
                break
                ;;
            "Reverse Engineer Codebase")
                read -p "Enter path or GitHub URL: " source
                python3 agents/re/reverse_engineer_agent.py "$source"
                break
                ;;
            "Develop Feature")
                echo "Available features:"
                ls -1 projects/ 2>/dev/null | head -10
                read -p "Enter feature ID: " feat_id
                python3 agents/dev/dev_agent.py "$feat_id"
                break
                ;;
            "Test Feature")
                echo "Available features:"
                ls -1 projects/ 2>/dev/null | head -10
                read -p "Enter feature ID: " feat_id
                python3 agents/qa/qa_agent.py "$feat_id"
                break
                ;;
            "Deploy Feature")
                echo "Available features:"
                ls -1 projects/ 2>/dev/null | head -10
                read -p "Enter feature ID: " feat_id
                read -p "Environment (local/staging/production): " env
                read -p "Platform (docker/kubernetes/vercel/aws): " platform
                python3 agents/deploy/deploy_agent.py "$feat_id" "$env" "$platform"
                break
                ;;
            "Full Pipeline")
                read -p "Enter your app idea: " idea
                read -p "Tech stack (optional): " stack
                
                # Step 1: PM
                echo ""
                echo "🎯 Step 1: PM Agent generating specification..."
                python3 agents/pm/pm_agent.py "$idea" "$stack"
                FEAT_ID=$(ls -t projects/ | head -1)
                
                # Step 2: Dev
                echo ""
                echo "👨‍💻 Step 2: Dev Agent developing feature..."
                python3 agents/dev/dev_agent.py "$FEAT_ID"
                
                # Step 3: QA
                echo ""
                echo "🧪 Step 3: QA Agent testing..."
                python3 agents/qa/qa_agent.py "$FEAT_ID" unit integration
                
                # Step 4: Deploy
                echo ""
                echo "🚀 Step 4: Deploy Agent deploying..."
                python3 agents/deploy/deploy_agent.py "$FEAT_ID" local docker
                
                echo ""
                echo "✅ Full pipeline complete!"
                echo "   Feature: $FEAT_ID"
                echo "   Location: projects/$FEAT_ID/"
                break
                ;;
            "Exit")
                echo "👋 Goodbye!"
                exit 0
                ;;
        esac
    done
else
    # Handle command line arguments
    case $1 in
        "full")
            if [ -z "$2" ]; then
                echo "Usage: ./devforge.sh full 'Your app idea' [tech_stack]"
                exit 1
            fi
            
            IDEA="$2"
            STACK="${3:-}"
            
            echo "🎯 Step 1: PM Agent..."
            python3 agents/pm/pm_agent.py "$IDEA" "$STACK"
            FEAT_ID=$(ls -t projects/ | head -1)
            
            echo ""
            echo "👨‍💻 Step 2: Dev Agent..."
            python3 agents/dev/dev_agent.py "$FEAT_ID"
            
            echo ""
            echo "🧪 Step 3: QA Agent..."
            python3 agents/qa/qa_agent.py "$FEAT_ID"
            
            echo ""
            echo "🚀 Step 4: Deploy Agent..."
            python3 agents/deploy/deploy_agent.py "$FEAT_ID" local docker
            
            echo ""
            echo "✅ Pipeline complete! Check projects/$FEAT_ID/"
            ;;
        "reverse")
            if [ -z "$2" ]; then
                echo "Usage: ./devforge.sh reverse <path_or_url>"
                exit 1
            fi
            python3 agents/re/reverse_engineer_agent.py "$2"
            ;;
            shift
            python3 agents/pm/pm_agent.py "$@"
            ;;
        "dev")
            shift
            python3 agents/dev/dev_agent.py "$@"
            ;;
        "qa")
            shift
            python3 agents/qa/qa_agent.py "$@"
            ;;
        "deploy")
            shift
            python3 agents/deploy/deploy_agent.py "$@"
            ;;
        *)
            echo "Unknown command: $1"
            echo "Usage: ./devforge.sh [full|pm|dev|qa|deploy]"
            exit 1
            ;;
    esac
fi
