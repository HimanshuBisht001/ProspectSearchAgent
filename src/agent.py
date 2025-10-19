import asyncio
import json
from typing import List, Dict, Any
from pathlib import Path
from datetime import datetime

# Import API clients
from api_clients.serpapi_client import SerpApiClient
from api_clients.smart_enricher import SmartCompanyEnricher
from api_clients.hunter_client import HunterClient

# Import processors
from data_processing.deduplicator import Deduplicator
from data_processing.scoring import ConfidenceScorer

class ProspectSearchAgent:
    def __init__(self):
        self.serpapi_client = SerpApiClient()
        self.smart_enricher = SmartCompanyEnricher()  # Replace Clearbit
        self.hunter_client = HunterClient()
        self.deduplicator = Deduplicator()
        self.scorer = ConfidenceScorer()
    
    async def search_prospects(self, icp_config: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Multi-stage prospect search pipeline with REAL DATA ONLY:
        1. SerpApi: Find companies via job listings
        2. Smart Enricher: Analyze job data for company insights
        3. Hunter: Find real email contacts
        4. Deduplicate and score
        """
        print("🚀 Starting Multi-API Prospect Search Pipeline...")
        print("=" * 60)
        
        try:
            # STAGE 1: Find companies via job listings
            print("\n📍 STAGE 1: Finding Companies via Job Listings")
            print("-" * 60)
            serpapi_filters = self._generate_serpapi_filters(icp_config)
            companies = await self.serpapi_client.search_companies(serpapi_filters)
            
            if not companies:
                print("❌ No companies found from job listings")
                return []
            
            print(f"✅ Found {len(companies)} companies from job listings")
            
            # STAGE 2: Smart enrichment using job data (instead of Clearbit)
            print("\n📍 STAGE 2: Analyzing Company Data from Job Listings")
            print("-" * 60)
            companies = await self.smart_enricher.enrich_companies_batch(companies)
            print(f"✅ Enhanced {len(companies)} companies with job data analysis")
            
            # STAGE 3: Find real contacts with Hunter
            print("\n📍 STAGE 3: Finding Real Contacts with Hunter.io")
            print("-" * 60)
            companies = await self.hunter_client.enrich_companies_with_contacts(companies)
            print(f"✅ Added contacts to {len(companies)} companies")
            
            # STAGE 4: Deduplicate
            print("\n📍 STAGE 4: Deduplicating Companies")
            print("-" * 60)
            companies = self.deduplicator.deduplicate_companies(companies)
            print(f"✅ {len(companies)} unique companies after deduplication")
            
            # STAGE 5: Calculate confidence scores
            print("\n📍 STAGE 5: Calculating Confidence Scores")
            print("-" * 60)
            companies = self.scorer.calculate_confidence(companies, icp_config)
            companies.sort(key=lambda x: x['confidence'], reverse=True)
            print(f"✅ Scored and ranked {len(companies)} companies")
            
            print("\n" + "=" * 60)
            print(f"🎯 PIPELINE COMPLETE: {len(companies)} qualified prospects")
            print("=" * 60)
            
            return companies
            
        except Exception as e:
            print(f"❌ Error in prospect search pipeline: {e}")
            import traceback
            traceback.print_exc()
            return []
    
    def _generate_serpapi_filters(self, icp_config: Dict[str, Any]) -> Dict[str, Any]:
        """Generate search filters for SerpApi based on ICP config"""
        geography = icp_config.get("geography", ["USA"])[0]
        signals = icp_config.get('signals', {})
        
        # We're using simple queries that work - no complex combinations
        return {
            "location": geography,
            "signals": signals
        }
    
    def save_results(self, prospects: List[Dict[str, Any]], filename: str = None):
        """Save results to JSON file"""
        if not filename:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"prospects_{timestamp}.json"
        
        output_dir = Path(__file__).parent.parent / "outputs"
        output_dir.mkdir(exist_ok=True)
        
        filepath = output_dir / filename
        
        with open(filepath, 'w') as f:
            json.dump(prospects, f, indent=2, default=str)
        
        print(f"💾 Results saved to: {filepath}")
        return str(filepath)
    
    def display_summary(self, prospects: List[Dict[str, Any]]):
        """Display a summary of results"""
        if not prospects:
            print("❌ No prospects found")
            return
        
        print("\n" + "=" * 60)
        print("📊 PROSPECT SEARCH SUMMARY")
        print("=" * 60)
        
        print(f"Total Prospects Found: {len(prospects)}")
        
        # Confidence levels
        high_confidence = [p for p in prospects if p["confidence"] >= 0.7]
        medium_confidence = [p for p in prospects if 0.4 <= p["confidence"] < 0.7]
        low_confidence = [p for p in prospects if p["confidence"] < 0.4]
        
        print(f"🎯 High Confidence (≥0.7): {len(high_confidence)}")
        print(f"📊 Medium Confidence (0.4-0.7): {len(medium_confidence)}")
        print(f"📈 Low Confidence (<0.4): {len(low_confidence)}")
        
        # Data sources
        smart_enriched = [p for p in prospects if p.get("smart_enriched")]
        hunter_contacts = [p for p in prospects if any(c.get("hunter_verified") for c in p.get("contacts", []))]
        
        print(f"\n📊 Data Quality:")
        print(f"   Smart Enriched: {len(smart_enriched)}")
        print(f"   Hunter Verified Contacts: {len(hunter_contacts)}")
        
        # Hiring statistics
        hiring_companies = [p for p in prospects if p.get("signals", {}).get("recent_hiring")]
        print(f"   Companies Currently Hiring: {len(hiring_companies)}")
        
        # Top prospects
        if prospects:
            print(f"\n🏆 TOP 5 RECOMMENDATIONS:")
            print("-" * 60)
            
            for i, prospect in enumerate(prospects[:5], 1):
                print(f"\n{i}. {prospect['company_name']}")
                print(f"   Confidence: {prospect['confidence']:.2f}")
                print(f"   Industry: {prospect['industry']}")
                print(f"   Employees: {prospect.get('employee_count', 'N/A')}")
                print(f"   Location: {prospect['location']}")
                
                # Data sources
                sources = prospect.get('source', [])
                if prospect.get('smart_enriched'):
                    sources.append('Smart Analysis')
                print(f"   Data Sources: {', '.join(sources)}")
                
                # Signals
                signals = []
                if prospect.get("signals", {}).get("recent_hiring"):
                    job_title = prospect.get("signals", {}).get("job_title", "Hiring")
                    signals.append(f"📈 {job_title}")
                
                if signals:
                    print(f"   Signals: {' | '.join(signals)}")
                
                # Real contacts
                if prospect.get('contacts'):
                    contact = prospect['contacts'][0]
                    verified = "✓ VERIFIED" if contact.get('hunter_verified') else ""
                    print(f"   Contact: {contact['name']} - {contact['title']} {verified}")
                    if contact.get('email'):
                        print(f"   Email: {contact['email']}")