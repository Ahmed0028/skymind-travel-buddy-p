"""
Deploy Lufthansa Travel Buddy to Vertex AI Agent Engine

Usage:
    python deployment/deploy.py --create
    python deployment/deploy.py --list
    python deployment/deploy.py --delete --resource_id=<ID>
"""

import argparse
import os
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from dotenv import load_dotenv
load_dotenv()

from google.cloud import aiplatform


def get_config():
    project_id = os.getenv("GOOGLE_CLOUD_PROJECT")
    location = os.getenv("GOOGLE_CLOUD_LOCATION", "global")
    if not project_id:
        raise ValueError("GOOGLE_CLOUD_PROJECT is required")
    return project_id, location


def create_agent():
    project_id, location = get_config()
    
    print(f"🚀 Deploying to Vertex AI Agent Engine...")
    print(f"   Project: {project_id}")
    print(f"   Location: {location}")
    
    aiplatform.init(project=project_id, location=location)
    
    from google.adk.cli.utils.agent_loader import AgentLoader
    from google.adk.deployment import deploy_to_agent_engine
    
    agent_loader = AgentLoader(agents_dir=Path(__file__).parent.parent)
    agent = agent_loader.load_agent("travel_buddy")
    
    print(f"   Agent: {agent.name}")
    
    remote_agent = deploy_to_agent_engine(
        agent=agent,
        project=project_id,
        location=location,
        display_name="Lufthansa Travel Buddy",
        description="Proactive disruption manager for Lufthansa business travelers",
    )
    
    print(f"\n✅ Deployed!")
    print(f"   Resource ID: {remote_agent.resource_name}")
    return remote_agent


def list_agents():
    project_id, location = get_config()
    aiplatform.init(project=project_id, location=location)
    
    from google.cloud.aiplatform import ReasoningEngine
    
    print(f"📋 Agents in {project_id}:\n")
    for agent in ReasoningEngine.list():
        print(f"   {agent.resource_name}")
        print(f"   Name: {agent.display_name}")
        print()


def delete_agent(resource_id: str):
    project_id, location = get_config()
    aiplatform.init(project=project_id, location=location)
    
    from google.cloud.aiplatform import ReasoningEngine
    
    ReasoningEngine(resource_id).delete()
    print(f"✅ Deleted: {resource_id}")


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--create", action="store_true")
    parser.add_argument("--list", action="store_true")
    parser.add_argument("--delete", action="store_true")
    parser.add_argument("--resource_id", type=str)
    
    args = parser.parse_args()
    
    if args.create:
        create_agent()
    elif args.list:
        list_agents()
    elif args.delete and args.resource_id:
        delete_agent(args.resource_id)
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
