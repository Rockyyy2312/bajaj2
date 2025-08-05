import logging
from typing import List, Dict, Any, Optional
import re
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)

class ClauseMaster:
    """Manage insurance clauses and provide clause matching logic"""
    
    def __init__(self):
        # Predefined insurance clause patterns and rules
        self.clause_patterns = {
            "waiting_period": {
                "keywords": ["waiting period", "waiting time", "exclusion period"],
                "patterns": [
                    r"(\d+)\s*(?:month|year)s?\s*waiting",
                    r"waiting\s*period\s*of\s*(\d+)\s*(?:month|year)s?"
                ]
            },
            "coverage_limit": {
                "keywords": ["coverage limit", "maximum coverage", "sum insured"],
                "patterns": [
                    r"(\d+(?:,\d+)*)\s*(?:lakh|lac|thousand|million)",
                    r"coverage\s*limit\s*(\d+(?:,\d+)*)"
                ]
            },
            "exclusions": {
                "keywords": ["exclusion", "not covered", "excluded"],
                "patterns": [
                    r"exclusion[s]?\s*:\s*(.*?)(?=\n|$)",
                    r"not\s*covered\s*:\s*(.*?)(?=\n|$)"
                ]
            },
            "pre_existing": {
                "keywords": ["pre-existing", "pre existing", "existing condition"],
                "patterns": [
                    r"pre-existing\s*condition[s]?\s*:\s*(.*?)(?=\n|$)"
                ]
            }
        }
        
        # Common insurance decision rules
        self.decision_rules = {
            "age_limits": {
                "min_age": 18,
                "max_age": 65
            },
            "waiting_periods": {
                "surgery": 12,  # months
                "pre_existing": 24,  # months
                "general": 3  # months
            },
            "coverage_types": {
                "surgery": ["knee", "hip", "heart", "brain", "spine"],
                "medical_conditions": ["cancer", "diabetes", "hypertension"],
                "diagnostic": ["tests", "scans", "examinations"]
            }
        }
    
    def extract_clause_info(self, clause_content: str) -> Dict[str, Any]:
        """Extract structured information from clause content"""
        clause_info = {
            "clause_type": "general",
            "waiting_period": None,
            "coverage_limit": None,
            "exclusions": [],
            "conditions": []
        }
        
        # Check for waiting period
        for pattern in self.clause_patterns["waiting_period"]["patterns"]:
            match = re.search(pattern, clause_content, re.IGNORECASE)
            if match:
                clause_info["waiting_period"] = int(match.group(1))
                clause_info["clause_type"] = "waiting_period"
                break
        
        # Check for coverage limits
        for pattern in self.clause_patterns["coverage_limit"]["patterns"]:
            match = re.search(pattern, clause_content, re.IGNORECASE)
            if match:
                amount_str = match.group(1).replace(",", "")
                clause_info["coverage_limit"] = int(amount_str)
                clause_info["clause_type"] = "coverage_limit"
                break
        
        # Check for exclusions
        for pattern in self.clause_patterns["exclusions"]["patterns"]:
            match = re.search(pattern, clause_content, re.IGNORECASE)
            if match:
                exclusions = match.group(1).split(",")
                clause_info["exclusions"] = [ex.strip() for ex in exclusions]
                clause_info["clause_type"] = "exclusion"
                break
        
        return clause_info
    
    def match_clauses_to_query(self, query: str, clauses: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Match relevant clauses to the insurance query"""
        matched_clauses = []
        query_lower = query.lower()
        
        for clause in clauses:
            relevance_score = 0.0
            clause_content = clause.get("clause_content", "").lower()
            
            # Calculate relevance based on keyword matching
            query_words = set(query_lower.split())
            clause_words = set(clause_content.split())
            
            # Simple keyword matching
            common_words = query_words.intersection(clause_words)
            if common_words:
                relevance_score = len(common_words) / len(query_words)
            
            # Check for specific medical terms
            medical_terms = ["surgery", "knee", "hip", "heart", "cancer", "diabetes"]
            for term in medical_terms:
                if term in query_lower and term in clause_content:
                    relevance_score += 0.3
            
            # Check for location matching
            locations = ["mumbai", "delhi", "pune", "bangalore", "chennai"]
            for location in locations:
                if location in query_lower and location in clause_content:
                    relevance_score += 0.2
            
            if relevance_score > 0.1:  # Minimum relevance threshold
                clause["relevance_score"] = min(relevance_score, 1.0)
                matched_clauses.append(clause)
        
        # Sort by relevance score
        matched_clauses.sort(key=lambda x: x.get("relevance_score", 0), reverse=True)
        return matched_clauses
    
    def evaluate_coverage_eligibility(self, query_entities: Dict[str, Any], matched_clauses: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Evaluate if the query is eligible for coverage based on clauses"""
        evaluation = {
            "eligible": False,
            "decision": "rejected",
            "amount": None,
            "justification": "",
            "waiting_period_info": "",
            "exclusions": [],
            "confidence_score": 0.0
        }
        
        # Check age eligibility
        age = query_entities.get("age")
        if age:
            if age < self.decision_rules["age_limits"]["min_age"] or age > self.decision_rules["age_limits"]["max_age"]:
                evaluation["justification"] = f"Age {age} is outside the eligible range ({self.decision_rules['age_limits']['min_age']}-{self.decision_rules['age_limits']['max_age']} years)"
                return evaluation
        
        # Check waiting periods
        condition = query_entities.get("condition", "").lower()
        policy_duration = query_entities.get("policy_duration")
        
        if policy_duration and condition:
            policy_months = int(policy_duration)
            
            # Determine required waiting period
            required_waiting = self.decision_rules["waiting_periods"]["general"]
            if any(surgery in condition for surgery in self.decision_rules["coverage_types"]["surgery"]):
                required_waiting = self.decision_rules["waiting_periods"]["surgery"]
            elif any(condition_name in condition for condition_name in self.decision_rules["coverage_types"]["medical_conditions"]):
                required_waiting = self.decision_rules["waiting_periods"]["pre_existing"]
            
            if policy_months < required_waiting:
                evaluation["waiting_period_info"] = f"Policy is only {policy_months} months old, but {required_waiting} months waiting period is required for {condition}"
                evaluation["justification"] = f"Waiting period not met. Required: {required_waiting} months, Current: {policy_months} months"
                return evaluation
        
        # Check coverage limits from matched clauses
        max_coverage = 0
        applicable_clauses = []
        
        for clause in matched_clauses:
            clause_info = self.extract_clause_info(clause["clause_content"])
            
            if clause_info["coverage_limit"]:
                max_coverage = max(max_coverage, clause_info["coverage_limit"])
                applicable_clauses.append(clause["clause_id"])
            
            if clause_info["exclusions"]:
                evaluation["exclusions"].extend(clause_info["exclusions"])
        
        # Determine decision
        if max_coverage > 0:
            evaluation["eligible"] = True
            evaluation["decision"] = "approved"
            evaluation["amount"] = max_coverage
            evaluation["justification"] = f"Coverage approved for {condition} with maximum amount of {max_coverage}"
            evaluation["confidence_score"] = 0.8
        else:
            evaluation["justification"] = "No applicable coverage clauses found for the query"
            evaluation["confidence_score"] = 0.3
        
        return evaluation
    
    def get_clause_summary(self, clauses: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Generate a summary of clauses"""
        summary = {
            "total_clauses": len(clauses),
            "clause_types": {},
            "coverage_limits": [],
            "waiting_periods": [],
            "exclusions": []
        }
        
        for clause in clauses:
            clause_info = self.extract_clause_info(clause["clause_content"])
            
            # Count clause types
            clause_type = clause_info["clause_type"]
            summary["clause_types"][clause_type] = summary["clause_types"].get(clause_type, 0) + 1
            
            # Collect coverage limits
            if clause_info["coverage_limit"]:
                summary["coverage_limits"].append(clause_info["coverage_limit"])
            
            # Collect waiting periods
            if clause_info["waiting_period"]:
                summary["waiting_periods"].append(clause_info["waiting_period"])
            
            # Collect exclusions
            summary["exclusions"].extend(clause_info["exclusions"])
        
        return summary
