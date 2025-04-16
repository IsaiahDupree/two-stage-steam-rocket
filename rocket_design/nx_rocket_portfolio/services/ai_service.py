"""
AI Service Module for Rocket Design
Provides comprehensive AI capabilities using OpenAI API
"""

import os
import json
import time
import logging
import traceback
from typing import Dict, List, Any, Optional, Union
from datetime import datetime

import openai
from openai import OpenAI
from openai.types.chat import ChatCompletion

# Import the fallback responses module
from nx_rocket_portfolio.services.fallback_responses import generate_fallback_design_response

# Import configuration
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from config import (
    OPENAI_API_KEY, 
    OPENAI_MODEL, 
    OPENAI_TEMPERATURE, 
    OPENAI_MAX_TOKENS,
    AI_FEATURES_ENABLED,
    USE_CACHE,
    DEMO_MODE
)

# Configure logging
logger = logging.getLogger(__name__)

class AIService:
    """Service for handling AI interactions and rocket design assistance"""
    
    def __init__(self):
        """Initialize the AI service with OpenAI client"""
        if not OPENAI_API_KEY:
            logger.warning("OpenAI API key not found. AI features will not work properly.")
            self.ai_available = False
        else:
            try:
                self.client = OpenAI(api_key=OPENAI_API_KEY)
                self.ai_available = True
                logger.info(f"AI service initialized with model {OPENAI_MODEL}")
            except Exception as e:
                logger.error(f"Failed to initialize OpenAI client: {str(e)}")
                self.ai_available = False
        
        # Cache for storing recent AI responses
        self.response_cache = {}
        
        # Load rocket engineering knowledge base
        self.engineering_knowledge = self._load_engineering_knowledge()
    
    def _load_engineering_knowledge(self) -> Dict:
        """Load rocket engineering knowledge and constraints"""
        try:
            knowledge_path = os.path.join(
                os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
                'data',
                'rocket_engineering_knowledge.json'
            )
            
            if os.path.exists(knowledge_path):
                with open(knowledge_path, 'r') as f:
                    return json.load(f)
            else:
                logger.warning(f"Engineering knowledge file not found at {knowledge_path}")
                return {}
        except Exception as e:
            logger.error(f"Error loading engineering knowledge: {str(e)}")
            return {}
    
    def process_design_prompt(self, prompt: str, current_model: Dict) -> Dict:
        """
        Process a natural language prompt for AI-assisted design
        
        Args:
            prompt (str): User's design request in natural language
            current_model (dict): Current rocket model parameters
            
        Returns:
            dict: Response with message and optional model changes
        """
        if DEMO_MODE or not self.ai_available or not AI_FEATURES_ENABLED:
            logger.info("Using demo/fallback mode for AI response.")
            return self._fallback_design_response(prompt, current_model)
        
        # Create cache key from prompt and model
        cache_key = f"{prompt}_{hash(json.dumps(current_model, sort_keys=True))}"
        
        # Check cache first if enabled
        if USE_CACHE and cache_key in self.response_cache:
            logger.info("Using cached AI response")
            return self.response_cache[cache_key]
        
        try:
            # Create a comprehensive system prompt with engineering knowledge
            system_prompt = self._create_design_system_prompt(current_model)
            
            # Format the user prompt with details about the current model
            user_prompt = self._format_user_design_prompt(prompt, current_model)
            
            # Call OpenAI API
            response = self.client.chat.completions.create(
                model=OPENAI_MODEL,
                temperature=OPENAI_TEMPERATURE,
                max_tokens=OPENAI_MAX_TOKENS,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                response_format={"type": "json_object"}
            )
            
            # Parse the response
            result = self._parse_design_response(response)
            
            # Cache the result if caching is enabled
            if USE_CACHE:
                self.response_cache[cache_key] = result
            
            return result
        
        except Exception as e:
            logger.error(f"Error processing AI design prompt: {str(e)}")
            logger.error(traceback.format_exc())
            return {
                "message": f"I apologize, but I encountered an error processing your design request: {str(e)}. Please try again or adjust your prompt.",
                "modelChanges": None,
                "changeDescription": None
            }
    
    def _create_design_system_prompt(self, current_model: Dict) -> str:
        """
        Create a comprehensive system prompt for the AI with engineering context
        
        Args:
            current_model (dict): Current rocket model parameters
            
        Returns:
            str: System prompt for the AI
        """
        # Extract relevant engineering constraints for the current rocket type
        rocket_type = "steam_rocket" if "steam" in current_model.get("name", "").lower() else "general"
        
        # Create the system prompt with engineering knowledge and constraints
        system_prompt = f"""You are an expert aerospace engineering AI assistant specializing in rocket design. 
You have extensive knowledge of structural engineering, fluid dynamics, materials science, and propulsion systems.

Your task is to provide detailed design recommendations for a rocket based on the user's request.
Analyze the current rocket design parameters and suggest improvements that align with sound engineering principles.

Current rocket type: {rocket_type}

Please format your response as a valid JSON object with the following structure:
{{
    "message": "Detailed explanation of your design recommendations",
    "modelChanges": {{
        "firstStage": {{ [Suggested parameter changes for first stage] }},
        "secondStage": {{ [Suggested parameter changes for second stage] }},
        "noseCone": {{ [Suggested parameter changes for nose cone] }},
        "fins": {{ [Suggested parameter changes for fins] }}
    }},
    "changeDescription": "Brief summary of changes"
}}

Only include parameters that need to be changed, and ensure all values are appropriate for a rocket. Use metric units.
Parameter values must be numeric (not strings) for dimensions, and valid string values for materials and shapes.
Ensure your recommendations are based on real aerospace engineering principles and obey the laws of physics.
"""
        
        # Add specific engineering knowledge depending on rocket type
        if rocket_type == "steam_rocket":
            system_prompt += f"""
For steam rockets specifically, consider:
- Appropriate pressure vessel design with safety factors
- Thermal management for steam systems
- Suitable materials for steam temperatures (typically 100-200°C)
- Wall thickness appropriate for pressure (typically 0.3-1.0 MPa)
"""
        
        return system_prompt
    
    def _format_user_design_prompt(self, prompt: str, current_model: Dict) -> str:
        """
        Format the user's prompt with additional context about the current model
        
        Args:
            prompt (str): User's design request
            current_model (dict): Current rocket model parameters
            
        Returns:
            str: Formatted user prompt
        """
        # Extract key parameters for context
        first_stage = current_model.get("firstStage", {})
        second_stage = current_model.get("secondStage", {})
        nose_cone = current_model.get("noseCone", {})
        fins = current_model.get("fins", {})
        
        # Format a comprehensive prompt with current parameters
        formatted_prompt = f"""
User Request: {prompt}

Current Rocket Model Parameters:
- Name: {current_model.get("name", "Two-Stage Steam Rocket")}
- Version: {current_model.get("version", "v1.0")}

First Stage:
- Diameter: {first_stage.get("diameter", 1.2)} meters
- Length: {first_stage.get("length", 7.2)} meters
- Material: {first_stage.get("material", "aluminum-2024")}

Second Stage:
- Diameter: {second_stage.get("diameter", 0.8)} meters
- Length: {second_stage.get("length", 3.2)} meters
- Material: {second_stage.get("material", "aluminum-7075")}

Nose Cone:
- Shape: {nose_cone.get("shape", "conical")}
- Length: {nose_cone.get("length", 1.0)} meters

Fins:
- Count: {fins.get("count", 4)}
- Shape: {fins.get("shape", "trapezoidal")}
- Span: {fins.get("span", 0.5)} meters

Based on my request and these current parameters, suggest engineering improvements that follow best practices for rocket design.
"""
        return formatted_prompt
    
    def _parse_design_response(self, response: ChatCompletion) -> Dict:
        """
        Parse the AI response into the expected format
        
        Args:
            response: OpenAI API response
            
        Returns:
            dict: Parsed response with message and model changes
        """
        try:
            # Extract the content from the response
            content = response.choices[0].message.content
            
            # Parse the JSON response
            parsed = json.loads(content)
            
            # Validate the response structure
            if "message" not in parsed:
                logger.warning("AI response missing 'message' field")
                parsed["message"] = "I've analyzed your design request and have some recommendations."
            
            if "modelChanges" not in parsed:
                logger.warning("AI response missing 'modelChanges' field")
                parsed["modelChanges"] = None
            
            if "changeDescription" not in parsed:
                logger.warning("AI response missing 'changeDescription' field")
                parsed["changeDescription"] = "AI-recommended design changes"
            
            return parsed
            
        except json.JSONDecodeError:
            logger.error(f"Failed to parse AI response as JSON: {response.choices[0].message.content}")
            return {
                "message": response.choices[0].message.content,
                "modelChanges": None,
                "changeDescription": "AI design recommendations"
            }
        except Exception as e:
            logger.error(f"Error parsing AI response: {str(e)}")
            return {
                "message": "I've analyzed your design and have suggestions, but there was an error formatting the response.",
                "modelChanges": None,
                "changeDescription": None
            }
    
    def _fallback_design_response(self, prompt: str, current_model: Dict) -> Dict:
        """
        Generate a fallback response when AI is unavailable
        
        Args:
            prompt (str): User's design request
            current_model (dict): Current rocket model parameters
            
        Returns:
            dict: Fallback response with simulated recommendations
        """
        # Use the external fallback response generator
        return generate_fallback_design_response(prompt, current_model)
    
    def analyze_rocket_design(self, model: Dict) -> str:
        """
        Analyze rocket design for performance, stability, and structural integrity
        
        Args:
            model (dict): Rocket model parameters
            
        Returns:
            str: Analysis results and recommendations
        """
        if not self.ai_available or not AI_FEATURES_ENABLED:
            logger.warning("AI features not available or disabled. Using fallback analysis.")
            return self._fallback_design_analysis(model)
        
        try:
            # Create system prompt for analysis
            system_prompt = """You are an expert aerospace engineering AI assistant specializing in rocket analysis.
Your task is to provide a detailed evaluation of a rocket design.
Consider structural integrity, flight stability, aerodynamics, and overall performance.
Format your response as Markdown with clear sections and bullet points.
Include specific engineering calculations where relevant.
Keep your analysis technical but understandable to an engineering student."""
            
            # Format user prompt with model details
            user_prompt = self._format_analysis_prompt(model)
            
            # Call OpenAI API
            response = self.client.chat.completions.create(
                model=OPENAI_MODEL,
                temperature=OPENAI_TEMPERATURE,
                max_tokens=OPENAI_MAX_TOKENS,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ]
            )
            
            # Return the response content
            return response.choices[0].message.content
            
        except Exception as e:
            logger.error(f"Error analyzing rocket design: {str(e)}")
            logger.error(traceback.format_exc())
            return self._fallback_design_analysis(model)
    
    def _format_analysis_prompt(self, model: Dict) -> str:
        """
        Format the analysis prompt with detailed model parameters
        
        Args:
            model (dict): Rocket model parameters
            
        Returns:
            str: Formatted analysis prompt
        """
        # Extract key parameters
        first_stage = model.get("firstStage", {})
        second_stage = model.get("secondStage", {})
        nose_cone = model.get("noseCone", {})
        fins = model.get("fins", {})
        
        # Calculate derived parameters
        total_length = (
            first_stage.get("length", 7.2) +
            second_stage.get("length", 3.2) +
            nose_cone.get("length", 1.0)
        )
        first_diameter = first_stage.get("diameter", 1.2)
        aspect_ratio = total_length / first_diameter if first_diameter > 0 else 0
        
        # Format comprehensive analysis prompt
        return f"""Please analyze this rocket design based on aerospace engineering principles:

Rocket Name: {model.get("name", "Two-Stage Steam Rocket")}
Total Length: {total_length:.2f} meters
Aspect Ratio: {aspect_ratio:.2f}

First Stage:
- Diameter: {first_stage.get("diameter", 1.2)} meters
- Length: {first_stage.get("length", 7.2)} meters
- Material: {first_stage.get("material", "aluminum-2024")}

Second Stage:
- Diameter: {second_stage.get("diameter", 0.8)} meters
- Length: {second_stage.get("length", 3.2)} meters
- Material: {second_stage.get("material", "aluminum-7075")}

Nose Cone:
- Shape: {nose_cone.get("shape", "conical")}
- Length: {nose_cone.get("length", 1.0)} meters

Fins:
- Count: {fins.get("count", 4)}
- Shape: {fins.get("shape", "trapezoidal")}
- Span: {fins.get("span", 0.5)} meters

Provide a comprehensive analysis including:
1. Structural integrity assessment
2. Flight stability calculation
3. Aerodynamic performance
4. Potential failure modes
5. Safety factor evaluation
6. Specific recommendations for improvements

This is a steam-powered rocket, so consider appropriate pressure vessel design principles and thermal management."""
    
    def _fallback_design_analysis(self, model: Dict) -> str:
        """
        Generate a fallback analysis when AI is unavailable
        
        Args:
            model (dict): Rocket model parameters
            
        Returns:
            str: Simulated analysis
        """
        # Extract key parameters
        first_stage = model.get("firstStage", {})
        second_stage = model.get("secondStage", {})
        nose_cone = model.get("noseCone", {})
        
        # Calculate derived parameters
        total_length = (
            first_stage.get("length", 7.2) +
            second_stage.get("length", 3.2) +
            nose_cone.get("length", 1.0)
        )
        first_diameter = first_stage.get("diameter", 1.2)
        aspect_ratio = total_length / first_diameter if first_diameter > 0 else 0
        
        # Create a basic analysis based on engineering principles
        analysis = f"""# Rocket Design Analysis

## Geometry Assessment
{'✅' if 5 <= aspect_ratio <= 12 else '⚠️'} **Aspect Ratio**: Your rocket's aspect ratio of {aspect_ratio:.1f} is {'within the optimal range of 5-12' if 5 <= aspect_ratio <= 12 else 'outside the recommended range of 5-12, which may impact performance'}.

{'✅' if first_stage.get("diameter", 1.2) >= second_stage.get("diameter", 0.8) else '⚠️'} **Stage Diameter Ratio**: Your first-to-second stage diameter ratio is {first_stage.get("diameter", 1.2) / second_stage.get("diameter", 0.8):.1f}, which is {'appropriate' if first_stage.get("diameter", 1.2) >= second_stage.get("diameter", 0.8) else 'unusual and may cause aerodynamic issues'}.

{'✅' if nose_cone.get("shape", "conical") in ["conical", "ogive", "elliptical"] else '⚠️'} **Nose Cone**: Your {nose_cone.get("shape", "conical")} nose cone shape is {' a standard aerodynamic profile' if nose_cone.get("shape", "conical") in ["conical", "ogive", "elliptical"] else 'not a recognized standard shape'}.

## Material Assessment
- **First Stage Material**: {first_stage.get("material", "aluminum-2024")} {'has good properties for rocket applications' if first_stage.get("material", "aluminum-2024") in ["aluminum-2024", "aluminum-7075", "carbon-fiber", "titanium-6al4v"] else 'is not a standard aerospace material'}
- **Second Stage Material**: {second_stage.get("material", "aluminum-7075")} {'has good properties for rocket applications' if second_stage.get("material", "aluminum-7075") in ["aluminum-2024", "aluminum-7075", "carbon-fiber", "titanium-6al4v"] else 'is not a standard aerospace material'}

## Overall Performance
Your rocket design has an estimated maximum altitude of {1000 * (aspect_ratio / 8):.1f} meters and maximum velocity of {100 * (aspect_ratio / 10):.1f} m/s based on its geometry and material selection.

## Steam Rocket Specific Recommendations
- Ensure your pressure vessel can handle 0.5-1.0 MPa safely
- Optimal wall thickness should be approximately {first_diameter * 1000 * 0.003:.1f}mm for your {first_diameter:.1f}m diameter
- Use pressure relief valve
- Consider double-walled construction for insulation
- Ensure wall thickness increases at joints and stress points
"""
        return analysis


# Create a singleton instance
ai_service = AIService()
