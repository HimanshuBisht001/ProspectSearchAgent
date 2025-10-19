import json
from typing import Dict, Any
from models import ICP

class ICPParser:
    """Parser for Ideal Customer Profile (ICP) data"""
    
    def parse_from_file(self, file_path: str) -> ICP:
        """Parse ICP configuration from JSON file"""
        with open(file_path, 'r') as f:
            data = json.load(f)
        return ICP(**data)
    
    def generate_apollo_filters(self, icp: ICP) -> Dict[str, Any]:
        """Generate Apollo API filters from ICP - OPTIMIZED for your endpoints"""
        filters = {}
        
        # Employee count filter
        if icp.employee_count_min:
            filters["organization_num_employees_ranges"] = [f"{icp.employee_count_min}.."]
        
        # Geography filter
        if icp.geography:
            filters["organization_locations"] = icp.geography
        
        # Industry filter
        if icp.industry:
            filters["organization_industries"] = icp.industry
        
        # Keyword search - use for company name search
        if icp.keywords:
            filters["q_organization_name"] = " OR ".join(icp.keywords)
        
        # Add revenue filter if available
        if icp.revenue_min or icp.revenue_max:
            revenue_filter = []
            if icp.revenue_min:
                revenue_filter.append(f"{int(icp.revenue_min/1000000)}M")
            if icp.revenue_max:
                revenue_filter.append(f"{int(icp.revenue_max/1000000)}M")
            filters["organization_estimated_revenue_range"] = ["-".join(revenue_filter)]
        
        return filters