import os
import aiohttp
import asyncio
from typing import List, Dict, Any
from dotenv import load_dotenv

load_dotenv()

class HunterClient:
    """Hunter.io API Client - For finding company emails and contacts"""
    
    def __init__(self):
        self.api_key = os.getenv('HUNTER_API_KEY')
        self.base_url = "https://api.hunter.io/v2"
    
    async def find_emails(self, domain: str, job_titles: List[str] = None) -> List[Dict[str, Any]]:
        """Find emails for a company domain"""
        if not self.api_key:
            print("⚠️  No Hunter API key found")
            return []
        
        # Search for company emails
        url = f"{self.base_url}/domain-search"
        params = {
            "domain": domain,
            "api_key": self.api_key,
            "limit": 10
        }
        
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(url, params=params) as response:
                    if response.status == 200:
                        data = await response.json()
                        return self._parse_hunter_contacts(data, job_titles)
                    else:
                        print(f"   ❌ Hunter error {response.status} for {domain}")
                        return []
        except Exception as e:
            print(f"   ❌ Hunter error: {e}")
            return []
    
    async def enrich_companies_with_contacts(self, companies: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Enrich companies with real email contacts from Hunter"""
        print("📧 Finding real contacts with Hunter.io...")
        
        for company in companies:
            domain = company.get("domain", "")
            company_name = company.get("company_name", "")
            
            # Skip if no valid domain
            if not domain or not isinstance(domain, str) or not domain.endswith('.com'):
                print(f"   ⚠️  Skipping {company_name} - invalid domain: {domain}")
                continue
            
            print(f"   Finding contacts for: {company_name}")
            
            # Determine relevant job titles based on ICP
            job_titles = ["CTO", "VP Engineering", "Chief Data Officer", "Head of Data"]
            
            contacts = await self.find_emails(domain, job_titles)
            
            if contacts:
                # Replace generated contacts with real ones
                company["contacts"] = contacts
                print(f"   ✅ Found {len(contacts)} real contacts")
            else:
                print(f"   ⚠️  No contacts found for {company_name}")
            
            # Rate limiting - Hunter free tier: 50 requests/month
            await asyncio.sleep(3)
        
        return companies
    
    def _parse_hunter_contacts(self, data: Dict[str, Any], target_titles: List[str] = None) -> List[Dict[str, Any]]:
        """Parse Hunter response into contact format"""
        contacts = []
        emails = data.get("data", {}).get("emails", [])
        
        for email_data in emails:
            # Filter by job title if specified
            position = email_data.get("position", "").lower()
            
            if target_titles:
                # Check if position matches any target title
                matches = any(title.lower() in position for title in target_titles)
                if not matches:
                    continue
            
            contact = {
                "name": f"{email_data.get('first_name', '')} {email_data.get('last_name', '')}".strip(),
                "title": email_data.get("position", ""),
                "email": email_data.get("value", ""),
                "linkedin": email_data.get("linkedin", ""),
                "confidence": email_data.get("confidence", 0) / 100.0,  # Convert to 0-1 scale
                "hunter_verified": True
            }
            
            if contact["email"]:
                contacts.append(contact)
        
        return contacts[:5]  # Return top 5 contacts