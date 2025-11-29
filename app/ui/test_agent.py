#!/usr/bin/env -S uv run
"""Quick test of the agent"""

from agent import HealthAgent

def test_agent():
    print("🧪 Testing PixelCare AI Agent...")
    agent = HealthAgent()
    
    print("\n💬 Sending test message...")
    response = ""
    for chunk in agent.chat("What is a normal heart rate?"):
        response += chunk
        print(chunk, end="", flush=True)
    
    print("\n\n✅ Test complete!")
    print(f"📊 Response length: {len(response)} chars")

if __name__ == "__main__":
    test_agent()
