"""
Enhanced Security Agent for ICRA

Extends the existing DeepCode security agent with advanced features for code review:
- Real-time vulnerability detection
- Configurable security policies
- Risk scoring algorithms
- Integration with code review workflow
"""

import asyncio
import logging
import os
import re
import json
from typing import Dict, Any, List, Optional, Tuple
from pathlib import Path
from datetime import datetime
import hashlib

# Import existing DeepCode security agent
import sys
sys.path.append(os.path.join(os.path.dirname(__file__), '../../../'))

try:
    from workflows.agents.security_agent import SecurityAgent as BaseSecurityAgent
    DEEPCODE_AVAILABLE = True
except ImportError:
    DEEPCODE_AVAILABLE = False
    BaseSecurityAgent = object

logger = logging.getLogger("EnhancedSecurityAgent")

class EnhancedSecurityAgent(BaseSecurityAgent if DEEPCODE_AVAILABLE else object):
    """
    Enhanced Security Agent for ICRA with advanced code review capabilities
    """
    
    def __init__(self, logger: Optional[logging.Logger] = None):
        if DEEPCODE_AVAILABLE:
            super().__init__(logger)
        else:
            self.logger = logger or self._setup_default_logger()
            
        self.security_rules = {}
        self.policy_engine = None
        self.risk_calculator = RiskCalculator()
        self.vulnerability_patterns = self._load_vulnerability_patterns()
        
    def _setup_default_logger(self) -> logging.Logger:
        """Setup default logger"""
        logger = logging.getLogger("EnhancedSecurityAgent")
        logger.setLevel(logging.INFO)
        return logger
        
    def _load_vulnerability_patterns(self) -> Dict[str, List[Dict]]:
        """Load vulnerability detection patterns"""
        return {
            "sql_injection": [
                {
                    "pattern": r"execute\s*\(\s*[\"'].*\+.*[\"']\s*\)",
                    "severity": "high",
                    "description": "Potential SQL injection via string concatenation"
                },
                {
                    "pattern": r"query\s*\(\s*f[\"'].*\{.*\}.*[\"']\s*\)",
                    "severity": "medium", 
                    "description": "Potential SQL injection via f-string formatting"
                }
            ],
            "xss": [
                {
                    "pattern": r"innerHTML\s*=\s*.*\+",
                    "severity": "high",
                    "description": "Potential XSS via innerHTML manipulation"
                },
                {
                    "pattern": r"document\.write\s*\(\s*.*\+",
                    "severity": "high",
                    "description": "Potential XSS via document.write"
                }
            ],
            "hardcoded_secrets": [
                {
                    "pattern": r"password\s*=\s*[\"'][^\"']{8,}[\"']",
                    "severity": "critical",
                    "description": "Hardcoded password detected"
                },
                {
                    "pattern": r"api_key\s*=\s*[\"'][A-Za-z0-9]{20,}[\"']",
                    "severity": "critical",
                    "description": "Hardcoded API key detected"
                }
            ],
            "insecure_crypto": [
                {
                    "pattern": r"md5\s*\(",
                    "severity": "medium",
                    "description": "Insecure MD5 hash function usage"
                },
                {
                    "pattern": r"sha1\s*\(",
                    "severity": "medium",
                    "description": "Insecure SHA1 hash function usage"
                }
            ]
        }
        
    async def analyze_code_for_review(self, code_directory: str, review_context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Comprehensive security analysis for code review
        
        Args:
            code_directory: Path to code directory
            review_context: Context information about the review
            
        Returns:
            Detailed security analysis results
        """
        try:
            self.logger.info(f"Starting enhanced security analysis for review: {review_context.get('review_id')}")
            
            analysis_result = {
                "review_id": review_context.get("review_id"),
                "status": "success",
                "timestamp": datetime.now().isoformat(),
                "security_score": 0,
                "risk_level": "unknown",
                "vulnerabilities": [],
                "policy_violations": [],
                "recommendations": [],
                "files_analyzed": 0,
                "analysis_duration": 0
            }
            
            start_time = datetime.now()
            
            # Run pattern-based vulnerability detection
            vulnerabilities = await self._detect_vulnerabilities(code_directory)
            analysis_result["vulnerabilities"] = vulnerabilities
            
            # Check policy compliance
            policy_violations = await self._check_policy_compliance(code_directory, review_context)
            analysis_result["policy_violations"] = policy_violations
            
            # Calculate security score and risk level
            security_score, risk_level = self._calculate_security_metrics(vulnerabilities, policy_violations)
            analysis_result["security_score"] = security_score
            analysis_result["risk_level"] = risk_level
            
            # Generate recommendations
            recommendations = self._generate_recommendations(vulnerabilities, policy_violations)
            analysis_result["recommendations"] = recommendations
            
            # Calculate analysis duration
            end_time = datetime.now()
            analysis_result["analysis_duration"] = (end_time - start_time).total_seconds()
            
            # Count analyzed files
            analysis_result["files_analyzed"] = self._count_code_files(code_directory)
            
            self.logger.info(f"Enhanced security analysis completed. Score: {security_score}, Risk: {risk_level}")
            
            return analysis_result
            
        except Exception as e:
            self.logger.error(f"Enhanced security analysis failed: {e}")
            return {
                "review_id": review_context.get("review_id"),
                "status": "error",
                "error": str(e),
                "timestamp": datetime.now().isoformat()
            }
            
    async def _detect_vulnerabilities(self, code_directory: str) -> List[Dict[str, Any]]:
        """Detect vulnerabilities using pattern matching"""
        vulnerabilities = []
        
        for root, dirs, files in os.walk(code_directory):
            for file in files:
                if file.endswith(('.py', '.js', '.java', '.php', '.rb', '.go')):
                    file_path = os.path.join(root, file)
                    file_vulns = await self._analyze_file_for_vulnerabilities(file_path)
                    vulnerabilities.extend(file_vulns)
                    
        return vulnerabilities
        
    async def _analyze_file_for_vulnerabilities(self, file_path: str) -> List[Dict[str, Any]]:
        """Analyze a single file for vulnerabilities"""
        vulnerabilities = []
        
        try:
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read()
                lines = content.split('\n')
                
            for vuln_type, patterns in self.vulnerability_patterns.items():
                for pattern_info in patterns:
                    pattern = pattern_info["pattern"]
                    severity = pattern_info["severity"]
                    description = pattern_info["description"]
                    
                    for line_num, line in enumerate(lines, 1):
                        if re.search(pattern, line, re.IGNORECASE):
                            vulnerabilities.append({
                                "id": self._generate_vuln_id(file_path, line_num, vuln_type),
                                "type": vuln_type,
                                "severity": severity,
                                "description": description,
                                "file_path": file_path,
                                "line_number": line_num,
                                "line_content": line.strip(),
                                "pattern_matched": pattern,
                                "confidence": self._calculate_confidence(pattern, line)
                            })
                            
        except Exception as e:
            self.logger.error(f"Error analyzing file {file_path}: {e}")
            
        return vulnerabilities
        
    async def _check_policy_compliance(self, code_directory: str, review_context: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Check code against security policies"""
        violations = []
        
        # Example policy checks
        policies = [
            {
                "name": "require_input_validation",
                "description": "All user inputs must be validated",
                "check": self._check_input_validation
            },
            {
                "name": "require_authentication",
                "description": "All endpoints must have authentication",
                "check": self._check_authentication_required
            },
            {
                "name": "no_hardcoded_secrets",
                "description": "No hardcoded secrets allowed",
                "check": self._check_no_hardcoded_secrets
            }
        ]
        
        for policy in policies:
            policy_violations = await policy["check"](code_directory)
            for violation in policy_violations:
                violation["policy_name"] = policy["name"]
                violation["policy_description"] = policy["description"]
                violations.append(violation)
                
        return violations
        
    async def _check_input_validation(self, code_directory: str) -> List[Dict[str, Any]]:
        """Check for proper input validation"""
        violations = []
        # Implementation would check for validation patterns
        return violations
        
    async def _check_authentication_required(self, code_directory: str) -> List[Dict[str, Any]]:
        """Check for authentication requirements"""
        violations = []
        # Implementation would check for auth decorators/middleware
        return violations
        
    async def _check_no_hardcoded_secrets(self, code_directory: str) -> List[Dict[str, Any]]:
        """Check for hardcoded secrets"""
        violations = []
        # This is already covered in vulnerability patterns
        return violations
        
    def _calculate_security_metrics(self, vulnerabilities: List[Dict], policy_violations: List[Dict]) -> Tuple[int, str]:
        """Calculate overall security score and risk level"""
        base_score = 100
        
        # Deduct points for vulnerabilities
        severity_weights = {"critical": 25, "high": 15, "medium": 8, "low": 3}
        
        for vuln in vulnerabilities:
            severity = vuln.get("severity", "low")
            confidence = vuln.get("confidence", 0.5)
            deduction = severity_weights.get(severity, 3) * confidence
            base_score -= deduction
            
        # Deduct points for policy violations
        for violation in policy_violations:
            base_score -= 10
            
        # Ensure score is between 0 and 100
        security_score = max(0, min(100, int(base_score)))
        
        # Determine risk level
        if security_score >= 90:
            risk_level = "low"
        elif security_score >= 70:
            risk_level = "medium"
        elif security_score >= 50:
            risk_level = "high"
        else:
            risk_level = "critical"
            
        return security_score, risk_level
        
    def _generate_recommendations(self, vulnerabilities: List[Dict], policy_violations: List[Dict]) -> List[str]:
        """Generate security recommendations"""
        recommendations = []
        
        # Vulnerability-based recommendations
        vuln_types = set(v["type"] for v in vulnerabilities)
        
        if "sql_injection" in vuln_types:
            recommendations.append("Use parameterized queries or ORM to prevent SQL injection")
            
        if "xss" in vuln_types:
            recommendations.append("Implement proper input sanitization and output encoding")
            
        if "hardcoded_secrets" in vuln_types:
            recommendations.append("Move secrets to environment variables or secure key management")
            
        if "insecure_crypto" in vuln_types:
            recommendations.append("Use secure cryptographic algorithms (SHA-256, bcrypt)")
            
        # Policy-based recommendations
        if policy_violations:
            recommendations.append("Review and address security policy violations")
            recommendations.append("Implement automated policy checking in CI/CD pipeline")
            
        # General recommendations
        if len(vulnerabilities) > 5:
            recommendations.append("Consider implementing a security code review process")
            
        return recommendations
        
    def _generate_vuln_id(self, file_path: str, line_num: int, vuln_type: str) -> str:
        """Generate unique vulnerability ID"""
        content = f"{file_path}:{line_num}:{vuln_type}"
        return hashlib.md5(content.encode()).hexdigest()[:12]
        
    def _calculate_confidence(self, pattern: str, line: str) -> float:
        """Calculate confidence score for pattern match"""
        # Simple confidence calculation based on pattern complexity
        if len(pattern) > 50:
            return 0.9
        elif len(pattern) > 30:
            return 0.7
        else:
            return 0.5
            
    def _count_code_files(self, code_directory: str) -> int:
        """Count number of code files analyzed"""
        count = 0
        for root, dirs, files in os.walk(code_directory):
            for file in files:
                if file.endswith(('.py', '.js', '.java', '.php', '.rb', '.go')):
                    count += 1
        return count

class RiskCalculator:
    """Calculate risk scores for security findings"""
    
    def __init__(self):
        self.risk_factors = {
            "severity": {"critical": 1.0, "high": 0.8, "medium": 0.5, "low": 0.2},
            "confidence": {"high": 1.0, "medium": 0.7, "low": 0.4},
            "exploitability": {"easy": 1.0, "medium": 0.6, "hard": 0.3}
        }
        
    def calculate_risk_score(self, vulnerability: Dict[str, Any]) -> float:
        """Calculate risk score for a vulnerability"""
        severity_score = self.risk_factors["severity"].get(vulnerability.get("severity", "low"), 0.2)
        confidence_score = vulnerability.get("confidence", 0.5)
        
        # Base risk calculation
        risk_score = severity_score * confidence_score
        
        # Adjust based on context
        if vulnerability.get("file_path", "").endswith(("auth.py", "login.py", "security.py")):
            risk_score *= 1.5  # Higher risk for security-related files
            
        return min(1.0, risk_score)

# Factory function for creating enhanced security agent
async def create_enhanced_security_agent(logger: Optional[logging.Logger] = None) -> EnhancedSecurityAgent:
    """Create and initialize enhanced security agent"""
    agent = EnhancedSecurityAgent(logger)
    if DEEPCODE_AVAILABLE:
        await agent.__aenter__()
    return agent
