"""
ICRA Security Policy Engine

Configurable security policy enforcement for code reviews.
Allows organizations to define and enforce custom security rules.
"""

import json
import yaml
import logging
from typing import Dict, List, Any, Optional, Callable
from pathlib import Path
from datetime import datetime
import re

logger = logging.getLogger("SecurityPolicyEngine")

class SecurityPolicy:
    """Represents a single security policy"""
    
    def __init__(self, policy_data: Dict[str, Any]):
        self.id = policy_data.get("id")
        self.name = policy_data.get("name")
        self.description = policy_data.get("description")
        self.severity = policy_data.get("severity", "medium")
        self.enabled = policy_data.get("enabled", True)
        self.rules = policy_data.get("rules", [])
        self.exceptions = policy_data.get("exceptions", [])
        self.metadata = policy_data.get("metadata", {})
        
    def is_applicable(self, file_path: str, context: Dict[str, Any]) -> bool:
        """Check if policy applies to given file and context"""
        if not self.enabled:
            return False
            
        # Check file type filters
        file_types = self.metadata.get("file_types", [])
        if file_types:
            file_ext = Path(file_path).suffix.lower()
            if file_ext not in file_types:
                return False
                
        # Check path exclusions
        excluded_paths = self.metadata.get("excluded_paths", [])
        for excluded_path in excluded_paths:
            if re.search(excluded_path, file_path):
                return False
                
        return True

class SecurityPolicyEngine:
    """
    Security Policy Engine for enforcing configurable security rules
    """
    
    def __init__(self, policy_config_path: Optional[str] = None):
        self.policies = {}
        self.policy_validators = {}
        self.config_path = policy_config_path
        self._register_default_validators()
        
        if policy_config_path:
            self.load_policies_from_file(policy_config_path)
        else:
            self._load_default_policies()
            
    def _register_default_validators(self):
        """Register default policy validators"""
        self.policy_validators = {
            "pattern_match": self._validate_pattern_match,
            "function_call": self._validate_function_call,
            "import_restriction": self._validate_import_restriction,
            "complexity_limit": self._validate_complexity_limit,
            "authentication_required": self._validate_authentication_required,
            "input_validation": self._validate_input_validation,
            "secure_headers": self._validate_secure_headers,
            "crypto_standards": self._validate_crypto_standards
        }
        
    def _load_default_policies(self):
        """Load default security policies"""
        default_policies = [
            {
                "id": "no_hardcoded_secrets",
                "name": "No Hardcoded Secrets",
                "description": "Prevent hardcoded passwords, API keys, and other secrets",
                "severity": "critical",
                "enabled": True,
                "rules": [
                    {
                        "type": "pattern_match",
                        "patterns": [
                            r"password\s*=\s*[\"'][^\"']{8,}[\"']",
                            r"api_key\s*=\s*[\"'][A-Za-z0-9]{20,}[\"']",
                            r"secret\s*=\s*[\"'][^\"']{10,}[\"']",
                            r"token\s*=\s*[\"'][A-Za-z0-9]{20,}[\"']"
                        ]
                    }
                ],
                "metadata": {
                    "file_types": [".py", ".js", ".java", ".php", ".rb", ".go"],
                    "excluded_paths": ["test/", "tests/", "spec/"]
                }
            },
            {
                "id": "sql_injection_prevention",
                "name": "SQL Injection Prevention",
                "description": "Prevent SQL injection vulnerabilities",
                "severity": "high",
                "enabled": True,
                "rules": [
                    {
                        "type": "pattern_match",
                        "patterns": [
                            r"execute\s*\(\s*[\"'].*\+.*[\"']\s*\)",
                            r"query\s*\(\s*[\"'].*\+.*[\"']\s*\)",
                            r"sql\s*=\s*[\"'].*\+.*[\"']"
                        ]
                    }
                ],
                "metadata": {
                    "file_types": [".py", ".java", ".php", ".rb"]
                }
            },
            {
                "id": "insecure_crypto",
                "name": "Insecure Cryptography",
                "description": "Prevent use of insecure cryptographic functions",
                "severity": "medium",
                "enabled": True,
                "rules": [
                    {
                        "type": "function_call",
                        "functions": ["md5", "sha1", "des", "rc4"]
                    }
                ],
                "metadata": {
                    "file_types": [".py", ".js", ".java", ".php", ".rb", ".go"]
                }
            },
            {
                "id": "authentication_endpoints",
                "name": "Authentication Required",
                "description": "Ensure authentication is required for sensitive endpoints",
                "severity": "high",
                "enabled": True,
                "rules": [
                    {
                        "type": "authentication_required",
                        "endpoint_patterns": [
                            r"@app\.route\s*\(\s*[\"']/admin",
                            r"@app\.route\s*\(\s*[\"']/api/user",
                            r"@app\.route\s*\(\s*[\"']/dashboard"
                        ]
                    }
                ],
                "metadata": {
                    "file_types": [".py", ".js", ".java", ".php", ".rb"]
                }
            }
        ]
        
        for policy_data in default_policies:
            policy = SecurityPolicy(policy_data)
            self.policies[policy.id] = policy
            
    def load_policies_from_file(self, file_path: str):
        """Load policies from configuration file"""
        try:
            with open(file_path, 'r') as f:
                if file_path.endswith('.yaml') or file_path.endswith('.yml'):
                    config = yaml.safe_load(f)
                else:
                    config = json.load(f)
                    
            policies_data = config.get("policies", [])
            for policy_data in policies_data:
                policy = SecurityPolicy(policy_data)
                self.policies[policy.id] = policy
                
            logger.info(f"Loaded {len(policies_data)} policies from {file_path}")
            
        except Exception as e:
            logger.error(f"Failed to load policies from {file_path}: {e}")
            
    def evaluate_policies(self, file_path: str, file_content: str, context: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Evaluate all applicable policies against a file"""
        violations = []
        
        for policy in self.policies.values():
            if policy.is_applicable(file_path, context):
                policy_violations = self._evaluate_policy(policy, file_path, file_content, context)
                violations.extend(policy_violations)
                
        return violations
        
    def _evaluate_policy(self, policy: SecurityPolicy, file_path: str, file_content: str, context: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Evaluate a single policy against a file"""
        violations = []
        
        for rule in policy.rules:
            rule_type = rule.get("type")
            validator = self.policy_validators.get(rule_type)
            
            if validator:
                rule_violations = validator(rule, file_path, file_content, context)
                for violation in rule_violations:
                    violations.append({
                        "policy_id": policy.id,
                        "policy_name": policy.name,
                        "policy_description": policy.description,
                        "severity": policy.severity,
                        "file_path": file_path,
                        "violation_type": rule_type,
                        **violation
                    })
                    
        return violations
        
    def _validate_pattern_match(self, rule: Dict, file_path: str, file_content: str, context: Dict) -> List[Dict[str, Any]]:
        """Validate pattern matching rules"""
        violations = []
        patterns = rule.get("patterns", [])
        lines = file_content.split('\n')
        
        for pattern in patterns:
            for line_num, line in enumerate(lines, 1):
                if re.search(pattern, line, re.IGNORECASE):
                    violations.append({
                        "line_number": line_num,
                        "line_content": line.strip(),
                        "pattern_matched": pattern,
                        "description": f"Pattern match violation: {pattern}"
                    })
                    
        return violations
        
    def _validate_function_call(self, rule: Dict, file_path: str, file_content: str, context: Dict) -> List[Dict[str, Any]]:
        """Validate function call restrictions"""
        violations = []
        functions = rule.get("functions", [])
        lines = file_content.split('\n')
        
        for func_name in functions:
            pattern = rf"\b{func_name}\s*\("
            for line_num, line in enumerate(lines, 1):
                if re.search(pattern, line, re.IGNORECASE):
                    violations.append({
                        "line_number": line_num,
                        "line_content": line.strip(),
                        "function_name": func_name,
                        "description": f"Restricted function call: {func_name}"
                    })
                    
        return violations
        
    def _validate_import_restriction(self, rule: Dict, file_path: str, file_content: str, context: Dict) -> List[Dict[str, Any]]:
        """Validate import restrictions"""
        violations = []
        restricted_imports = rule.get("imports", [])
        lines = file_content.split('\n')
        
        for import_name in restricted_imports:
            pattern = rf"import\s+{import_name}|from\s+{import_name}\s+import"
            for line_num, line in enumerate(lines, 1):
                if re.search(pattern, line, re.IGNORECASE):
                    violations.append({
                        "line_number": line_num,
                        "line_content": line.strip(),
                        "import_name": import_name,
                        "description": f"Restricted import: {import_name}"
                    })
                    
        return violations
        
    def _validate_complexity_limit(self, rule: Dict, file_path: str, file_content: str, context: Dict) -> List[Dict[str, Any]]:
        """Validate complexity limits"""
        violations = []
        max_complexity = rule.get("max_complexity", 10)
        
        # Simple complexity calculation (count of if/for/while statements)
        complexity_patterns = [r'\bif\b', r'\bfor\b', r'\bwhile\b', r'\belif\b', r'\bexcept\b']
        lines = file_content.split('\n')
        
        current_function = None
        function_complexity = 0
        
        for line_num, line in enumerate(lines, 1):
            # Detect function definitions
            func_match = re.search(r'def\s+(\w+)', line)
            if func_match:
                if current_function and function_complexity > max_complexity:
                    violations.append({
                        "line_number": line_num - 1,
                        "function_name": current_function,
                        "complexity": function_complexity,
                        "max_allowed": max_complexity,
                        "description": f"Function complexity ({function_complexity}) exceeds limit ({max_complexity})"
                    })
                    
                current_function = func_match.group(1)
                function_complexity = 0
                
            # Count complexity indicators
            for pattern in complexity_patterns:
                if re.search(pattern, line):
                    function_complexity += 1
                    
        return violations
        
    def _validate_authentication_required(self, rule: Dict, file_path: str, file_content: str, context: Dict) -> List[Dict[str, Any]]:
        """Validate authentication requirements"""
        violations = []
        endpoint_patterns = rule.get("endpoint_patterns", [])
        lines = file_content.split('\n')
        
        for pattern in endpoint_patterns:
            for line_num, line in enumerate(lines, 1):
                if re.search(pattern, line):
                    # Check if authentication decorator is present in nearby lines
                    auth_found = False
                    for check_line_num in range(max(1, line_num - 5), min(len(lines), line_num + 2)):
                        check_line = lines[check_line_num - 1]
                        if re.search(r'@login_required|@auth_required|@authenticate', check_line):
                            auth_found = True
                            break
                            
                    if not auth_found:
                        violations.append({
                            "line_number": line_num,
                            "line_content": line.strip(),
                            "description": "Endpoint missing authentication requirement"
                        })
                        
        return violations
        
    def _validate_input_validation(self, rule: Dict, file_path: str, file_content: str, context: Dict) -> List[Dict[str, Any]]:
        """Validate input validation requirements"""
        violations = []
        # Implementation would check for input validation patterns
        return violations
        
    def _validate_secure_headers(self, rule: Dict, file_path: str, file_content: str, context: Dict) -> List[Dict[str, Any]]:
        """Validate secure headers requirements"""
        violations = []
        # Implementation would check for security headers
        return violations
        
    def _validate_crypto_standards(self, rule: Dict, file_path: str, file_content: str, context: Dict) -> List[Dict[str, Any]]:
        """Validate cryptographic standards"""
        violations = []
        # Implementation would check for proper crypto usage
        return violations
        
    def get_policy_summary(self) -> Dict[str, Any]:
        """Get summary of loaded policies"""
        enabled_count = sum(1 for p in self.policies.values() if p.enabled)
        severity_counts = {}
        
        for policy in self.policies.values():
            if policy.enabled:
                severity = policy.severity
                severity_counts[severity] = severity_counts.get(severity, 0) + 1
                
        return {
            "total_policies": len(self.policies),
            "enabled_policies": enabled_count,
            "disabled_policies": len(self.policies) - enabled_count,
            "severity_distribution": severity_counts
        }

# Global policy engine instance
security_policy_engine = SecurityPolicyEngine()
