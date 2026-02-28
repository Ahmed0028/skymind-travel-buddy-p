"""
Test deployed agent.

Usage:
    python deployment/test_deployment.py --resource_id=<ID>
"""

import argparse
import os
from dotenv import load_dotenv
load_dotenv()

from google.cloud import aiplatform


def test_agent(resource_id: str, user_id: str = "test_user"):
    project_id = os.getenv("GOOGLE_CLOUD_PROJECT")
    location = os.getenv("GOOGLE_CLOUD_LOCATION", "global")
    
    aiplatform.init(project=project_id, location=location)
    
    from google.cloud.aiplatform import ReasoningEngine
    
    print(f"🔗 Connecting to: {resource_id}")
    agent = ReasoningEngine(resource_id)
    session = agent.create_session(user_id=user_id)
    
    print(f"✅ Connected: {agent.display_name}")
    print(f"\n💬 Chat (type 'quit' to exit)\n")
    
    while True:
        try:
            user_input = input("You: ").strip()
            if user_input.lower() in ["quit", "exit", "q"]:
                break
            if user_input:
                response = session.send_message(user_input)
                print(f"\n🤖 {response.text}\n")
        except KeyboardInterrupt:
            break
    
    print("👋 Goodbye!")


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--resource_id", required=True)
    parser.add_argument("--user_id", default="test_user")
    args = parser.parse_args()
    test_agent(args.resource_id, args.user_id)


if __name__ == "__main__":
    main()
