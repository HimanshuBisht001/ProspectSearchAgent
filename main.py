import asyncio
import json
import sys
import os

# Add src to Python path
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from agent import ProspectSearchAgent

async def main():
    print("=" * 60)
    print("🤖 PROSPECTSEARCHAGENT - B2B Prospect Finder")
    print("=" * 60)
    print("✅ Features:")
    print("   • Takes ICP JSON configuration")
    print("   • Uses SerpApi job listings to find companies")
    print("   • Focuses on real API data only")
    print("   • Returns structured JSON output")
    print("=" * 60)
    
    # Load ICP configuration from file
    try:
        with open('config/icp_example.json', 'r') as f:
            icp_config = json.load(f)
    except FileNotFoundError:
        print("❌ ICP config file not found at config/icp_example.json")
        return
    except json.JSONDecodeError:
        print("❌ Invalid JSON in ICP config file")
        return
    
    print("\n📋 ICP CONFIGURATION:")
    print(f"   Industries: {icp_config.get('industry', [])}")
    print(f"   Geography: {icp_config.get('geography', [])}")
    print(f"   Employee Min: {icp_config.get('employee_count_min', 0)}+")
    print(f"   Revenue Range: ${icp_config.get('revenue_min', 0):,} - ${icp_config.get('revenue_max', 0):,}")
    print(f"   Keywords: {icp_config.get('keywords', [])}")
    
    signals = icp_config.get('signals', {})
    print(f"   Signals: Funding={signals.get('funding', False)}, Hiring={signals.get('hiring_data_roles', False)}")
    print(f"   Tech Stack: {signals.get('tech_stack', [])}")
    
    # Initialize and run the agent
    agent = ProspectSearchAgent()
    
    print("\n🚀 Starting prospect search...")
    prospects = await agent.search_prospects(icp_config)
    
    # Save results
    results_file = agent.save_results(prospects)
    
    # Display summary
    agent.display_summary(prospects)
    
    # Show sample output
    if prospects:
        print(f"\n📄 SAMPLE OUTPUT (First Prospect):")
        print("-" * 50)
        print(json.dumps(prospects[0], indent=2))
    
    print(f"\n💾 Complete results saved to: {results_file}")
    print("✅ Prospect search completed successfully!")

if __name__ == "__main__":
    asyncio.run(main())