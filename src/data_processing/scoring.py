from typing import List, Dict, Any

class ConfidenceScorer:
    def calculate_confidence(self, companies: List[Dict[str, Any]], icp_config: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Calculate confidence scores using the required formula:
        score = 0.4*industry_match + 0.3*funding_signal + 0.2*hiring_signal + 0.1*employee_match
        """
        print("📊 Calculating confidence scores...")
        
        for company in companies:
            score = 0.0
            
            # 1. Industry match (40%)
            industry_score = self._calculate_industry_match(company, icp_config)
            score += industry_score * 0.4
            
            # 2. Funding signals (30%)
            funding_score = self._calculate_funding_score(company, icp_config)
            score += funding_score * 0.3
            
            # 3. Hiring signals (20%)
            hiring_score = self._calculate_hiring_score(company, icp_config)
            score += hiring_score * 0.2
            
            # 4. Employee count match (10%)
            employee_score = self._calculate_employee_score(company, icp_config)
            score += employee_score * 0.1
            
            company["confidence"] = round(score, 2)
        
        # Sort by confidence score (highest first)
        return sorted(companies, key=lambda x: x["confidence"], reverse=True)
    
    def _calculate_industry_match(self, company: Dict[str, Any], icp_config: Dict[str, Any]) -> float:
        """Calculate industry match score (0-1)"""
        icp_industries = icp_config.get("industry", [])
        if not icp_industries:
            return 0.0
        
        company_industry = company.get("industry", "").lower()
        if not company_industry:
            return 0.0
        
        for target_industry in icp_industries:
            if target_industry.lower() in company_industry:
                return 1.0
        
        # Partial match check
        for target_industry in icp_industries:
            target_words = set(target_industry.lower().split())
            company_words = set(company_industry.split())
            
            if target_words.intersection(company_words):
                return 0.5
        
        return 0.0
    
    def _calculate_funding_score(self, company: Dict[str, Any], icp_config: Dict[str, Any]) -> float:
        """Calculate funding signal score (0-1)"""
        icp_signals = icp_config.get("signals", {})
        if not icp_signals.get("funding", False):
            return 0.0
        
        signals = company.get("signals", {})
        
        if signals.get("new_funding"):
            # Higher score for more recent/larger funding
            funding_amount = signals.get("funding_amount", 0)
            if funding_amount > 50000000:  # $50M+
                return 1.0
            elif funding_amount > 10000000:  # $10M+
                return 0.8
            else:
                return 0.6
        elif signals.get("funding_round"):
            # Has funding history but not recent
            return 0.3
        
        return 0.0
    
    def _calculate_hiring_score(self, company: Dict[str, Any], icp_config: Dict[str, Any]) -> float:
        """Calculate hiring signal score (0-1)"""
        icp_signals = icp_config.get("signals", {})
        if not icp_signals.get("hiring_data_roles", False):
            return 0.0
        
        signals = company.get("signals", {})
        
        if signals.get("recent_hiring"):
            return 1.0
        
        return 0.0
    
    def _calculate_employee_score(self, company: Dict[str, Any], icp_config: Dict[str, Any]) -> float:
        """Calculate employee count match score (0-1)"""
        employee_min = icp_config.get("employee_count_min")
        if not employee_min or not company.get("employee_count"):
            return 0.0
        
        employee_count = company["employee_count"]
        
        if employee_count >= employee_min:
            # Perfect match or larger
            return 1.0
        elif employee_count >= employee_min * 0.8:
            # Close match (within 20%)
            return 0.5
        elif employee_count >= employee_min * 0.5:
            # Partial match (within 50%)
            return 0.2
        
        return 0.0