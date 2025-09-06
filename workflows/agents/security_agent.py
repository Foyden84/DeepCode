"""
Security Analysis Agent for Code Implementation Workflow

This agent provides security analysis and vulnerability detection for generated code:
1. Static code analysis for common vulnerabilities
2. Dependency security scanning
3. Security best practices validation
4. Secure coding pattern recommendations
"""

import asyncio
import logging
import os
import re
from typing import Dict, Any, List, Optional
from pathlib import Path

# MCP Agent imports
from mcp_agent.agents.agent import Agent


class SecurityAgent:
    """
    Security Analysis Agent for code validation and vulnerability detection
    
    Responsibilities:
    - Analyze generated code for security vulnerabilities
    - Check dependencies for known security issues
    - Validate secure coding practices
    - Provide security recommendations and fixes
    """
    
    def __init__(self, logger: Optional[logging.Logger] = None):
        """Initialize Security Agent"""
        self.logger = logger or self._setup_default_logger()
        self.mcp_agent = None
        self.llm = None
        
    def _setup_default_logger(self) -> logging.Logger:
        """Setup default logger"""
        logger = logging.getLogger("SecurityAgent")
        logger.setLevel(logging.INFO)
        return logger
        
    async def __aenter__(self):
        """Async context manager entry"""
        await self._initialize_mcp_agent()
        return self
        
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit"""
        if self.mcp_agent:
            await self.mcp_agent.__aexit__(exc_type, exc_val, exc_tb)
            
    async def _initialize_mcp_agent(self):
        """Initialize MCP agent for security analysis"""
        try:
            # Import here to avoid circular imports
            from utils.llm_utils import get_preferred_llm_class
            
            self.mcp_agent = Agent(
                name="SecurityAnalysisAgent",
                instruction=self._get_security_analysis_prompt(),
                server_names=["code-implementation", "filesystem"]  # Use existing servers
            )
            
            await self.mcp_agent.__aenter__()
            self.llm = await self.mcp_agent.attach_llm(get_preferred_llm_class())
            
            self.logger.info("Security Agent initialized successfully")
            
        except Exception as e:
            self.logger.error(f"Failed to initialize Security Agent: {e}")
            raise
            
    def _get_security_analysis_prompt(self) -> str:
        """Get security analysis prompt"""
        # Import here to avoid circular imports
        from prompts.code_prompts import SECURITY_ANALYSIS_PROMPT
        return SECURITY_ANALYSIS_PROMPT

    async def analyze_code_security(self, code_directory: str) -> Dict[str, Any]:
        """
        Perform comprehensive security analysis of generated code
        
        Args:
            code_directory: Path to the generated code directory
            
        Returns:
            Dict containing security analysis results
        """
        try:
            self.logger.info(f"Starting security analysis for: {code_directory}")
            
            # Check if code directory exists
            if not os.path.exists(code_directory):
                return {
                    "status": "error",
                    "message": f"Code directory not found: {code_directory}"
                }
                
            # Prepare analysis message
            analysis_message = f"""Please perform a comprehensive security analysis of the code in directory: {code_directory}

Use the available MCP tools to:
1. **Read all code files** systematically using read_file or get_file_structure
2. **Analyze each file** for security vulnerabilities
3. **Check dependencies** in requirements.txt, package.json, etc.
4. **Validate secure coding practices**

Provide a detailed security report with:
- List of identified vulnerabilities with risk levels
- Specific file locations and line numbers
- Remediation recommendations
- Overall security score and summary

Focus on practical, actionable security improvements."""

            # Generate security analysis
            result = await self.llm.generate_str(message=analysis_message)
            
            self.logger.info("Security analysis completed successfully")
            
            return {
                "status": "success",
                "code_directory": code_directory,
                "analysis_result": result,
                "timestamp": str(asyncio.get_event_loop().time())
            }
            
        except Exception as e:
            self.logger.error(f"Error in security analysis: {e}")
            return {
                "status": "error",
                "code_directory": code_directory,
                "error_message": str(e)
            }
            
    async def validate_dependencies(self, code_directory: str) -> Dict[str, Any]:
        """
        Validate dependencies for known security vulnerabilities
        
        Args:
            code_directory: Path to the code directory
            
        Returns:
            Dict containing dependency security analysis
        """
        try:
            self.logger.info(f"Validating dependencies in: {code_directory}")
            
            validation_message = f"""Please analyze the dependencies in {code_directory} for security vulnerabilities.

Check for:
1. **Known CVEs** in dependency versions
2. **Outdated packages** with security patches available
3. **Malicious packages** or typosquatting
4. **Excessive permissions** in package dependencies
5. **Deprecated packages** with security implications

Look for dependency files like:
- requirements.txt (Python)
- package.json (Node.js)
- Cargo.toml (Rust)
- go.mod (Go)
- pom.xml (Java)

Provide specific recommendations for updating or replacing vulnerable dependencies."""

            result = await self.llm.generate_str(message=validation_message)
            
            return {
                "status": "success",
                "dependency_analysis": result
            }
            
        except Exception as e:
            self.logger.error(f"Error in dependency validation: {e}")
            return {
                "status": "error",
                "error_message": str(e)
            }


# Utility function for integration with existing workflow
async def run_security_analysis(
    code_directory: str, 
    logger: Optional[logging.Logger] = None
) -> Dict[str, Any]:
    """
    Run comprehensive security analysis on generated code
    
    Args:
        code_directory: Path to the generated code directory
        logger: Optional logger instance
        
    Returns:
        Dict containing complete security analysis results
    """
    async with SecurityAgent(logger=logger) as agent:
        # Perform code security analysis
        security_result = await agent.analyze_code_security(code_directory)
        
        if security_result["status"] == "success":
            # Validate dependencies
            dependency_result = await agent.validate_dependencies(code_directory)
            security_result["dependency_analysis"] = dependency_result
            
        return security_result
