from typing import List, Dict, Any
from thefuzz import fuzz

class Deduplicator:
    def __init__(self):
        self.similarity_threshold = 85  # 85% similarity for fuzzy matching
    
    def deduplicate_companies(self, companies: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Remove duplicate companies using fuzzy matching"""
        print("🔄 Deduplicating companies...")
        
        unique_companies = {}
        
        for company in companies:
            key = self._get_company_key(company)
            
            if key not in unique_companies:
                # Check for similar companies using fuzzy matching
                similar_key = self._find_similar_company(company, unique_companies)
                if similar_key:
                    # Merge with existing similar company
                    existing = unique_companies[similar_key]
                    unique_companies[similar_key] = self._merge_companies(existing, company)
                else:
                    # Add as new company
                    unique_companies[key] = company
            else:
                # Merge with existing exact match
                existing = unique_companies[key]
                unique_companies[key] = self._merge_companies(existing, company)
        
        return list(unique_companies.values())
    
    def _get_company_key(self, company: Dict[str, Any]) -> str:
        """Generate unique key for company (domain or name)"""
        if company.get("domain"):
            return company["domain"].lower().strip()
        return company["company_name"].lower().strip()
    
    def _find_similar_company(self, company: Dict[str, Any], existing_companies: Dict) -> str:
        """Find similar company using fuzzy string matching"""
        company_name = company["company_name"].lower()
        
        for key, existing_company in existing_companies.items():
            existing_name = existing_company["company_name"].lower()
            
            # Calculate similarity score
            similarity = fuzz.ratio(company_name, existing_name)
            
            if similarity >= self.similarity_threshold:
                print(f"🔍 Similar companies found: {company_name} ~ {existing_name} ({similarity}%)")
                return key
        
        return None
    
    def _merge_companies(self, company1: Dict[str, Any], company2: Dict[str, Any]) -> Dict[str, Any]:
        """Merge two company records"""
        merged = company1.copy()
        
        # Merge sources
        merged["source"] = list(set(company1["source"] + company2["source"]))
        
        # Merge signals - company2 signals override company1
        if "signals" in company2:
            if "signals" not in merged:
                merged["signals"] = {}
            merged["signals"].update(company2["signals"])
        
        # Merge contacts - avoid duplicates by email
        existing_emails = {contact["email"] for contact in merged["contacts"] if contact.get("email")}
        
        for contact in company2["contacts"]:
            if contact.get("email") not in existing_emails:
                merged["contacts"].append(contact)
        
        # Prefer non-null values for key fields
        for field in ["revenue", "employee_count", "funding_stage"]:
            if not merged.get(field) and company2.get(field):
                merged[field] = company2[field]
        
        return merged