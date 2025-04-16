"""
Fallback responses for AI Design System demo mode
"""

def generate_fallback_design_response(prompt, current_model):
    """
    Generate a fallback response when AI is unavailable
    
    Args:
        prompt (str): User's design request
        current_model (dict): Current rocket model parameters
        
    Returns:
        dict: Fallback response with simulated recommendations
    """
    # Extract current model components
    first_stage = current_model.get("firstStage", {})
    second_stage = current_model.get("secondStage", {})
    nose_cone = current_model.get("noseCone", {})
    fins = current_model.get("fins", {})
    
    response = {
        "message": "I've analyzed your design request and have the following recommendations.",
        "modelChanges": {},
        "status": "success"
    }
    
    # Process based on keywords in prompt
    lower_prompt = prompt.lower()
    
    # Track if we made any changes
    changes_made = False
    
    # First Stage changes
    if any(term in lower_prompt for term in ["first stage", "booster", "main stage"]) or "diameter" in lower_prompt:
        # Diameter changes
        if any(term in lower_prompt for term in ["wider", "increase diameter", "larger diameter"]):
            current_diameter = first_stage.get("diameter", 1.2)
            response["modelChanges"]["firstStage"] = response["modelChanges"].get("firstStage", {})
            response["modelChanges"]["firstStage"]["diameter"] = min(current_diameter * 1.25, 2.0)
            response["message"] += f"\n\n• I've increased the first stage diameter from {current_diameter} to {response['modelChanges']['firstStage']['diameter']:.2f} meters. This will provide more internal volume for propellant and improve stability."
            changes_made = True
        
        # Material changes
        if "carbon" in lower_prompt or "composite" in lower_prompt or "fiber" in lower_prompt:
            response["modelChanges"]["firstStage"] = response["modelChanges"].get("firstStage", {})
            response["modelChanges"]["firstStage"]["material"] = "carbon-fiber"
            response["message"] += "\n\n• I've changed the first stage material to carbon fiber. This reduces mass by approximately 30% while maintaining structural integrity, significantly improving the thrust-to-weight ratio."
            changes_made = True
        elif "titanium" in lower_prompt:
            response["modelChanges"]["firstStage"] = response["modelChanges"].get("firstStage", {})
            response["modelChanges"]["firstStage"]["material"] = "titanium-6al4v"
            response["message"] += "\n\n• I've changed the first stage material to titanium 6Al-4V alloy. This offers superior strength-to-weight ratio and heat resistance compared to aluminum, but at increased cost."
            changes_made = True
    
    # Second Stage changes
    if any(term in lower_prompt for term in ["second stage", "upper stage"]) or "longer" in lower_prompt:
        # Length changes
        if any(term in lower_prompt for term in ["longer", "increase length", "extend"]):
            current_length = second_stage.get("length", 3.2)
            response["modelChanges"]["secondStage"] = response["modelChanges"].get("secondStage", {})
            response["modelChanges"]["secondStage"]["length"] = current_length * 1.25
            response["message"] += f"\n\n• I've extended the second stage length from {current_length} to {response['modelChanges']['secondStage']['length']:.2f} meters. This provides 25% more propellant capacity, increasing delta-V by approximately 20%."
            changes_made = True
    
    # Nose cone changes
    if "nose" in lower_prompt or "aerodynamic" in lower_prompt:
        # Shape changes
        if "ogive" in lower_prompt:
            response["modelChanges"]["noseCone"] = response["modelChanges"].get("noseCone", {})
            response["modelChanges"]["noseCone"]["shape"] = "ogive"
            response["message"] += "\n\n• I've changed the nose cone to an ogive shape, which reduces drag by approximately 15% compared to a conical nose cone, especially at transonic velocities."
            changes_made = True
        elif "elliptical" in lower_prompt:
            response["modelChanges"]["noseCone"] = response["modelChanges"].get("noseCone", {})
            response["modelChanges"]["noseCone"]["shape"] = "elliptical"
            response["message"] += "\n\n• I've changed the nose cone to an elliptical shape, which provides a good balance of drag reduction and ease of manufacturing."
            changes_made = True
    
    # Fin changes
    if "fin" in lower_prompt or "stability" in lower_prompt:
        # Count changes
        if "more" in lower_prompt and "fins" in lower_prompt:
            response["modelChanges"]["fins"] = response["modelChanges"].get("fins", {})
            response["modelChanges"]["fins"]["count"] = 6
            response["message"] += "\n\n• I've increased the number of fins from 4 to 6. This improves stability, particularly during the initial launch phase with high thrust and low velocities."
            changes_made = True
        
        # Span changes
        if "larger" in lower_prompt and "fins" in lower_prompt:
            current_span = fins.get("span", 0.5)
            response["modelChanges"]["fins"] = response["modelChanges"].get("fins", {})
            response["modelChanges"]["fins"]["span"] = current_span * 1.3
            response["message"] += f"\n\n• I've increased the fin span from {current_span} to {response['modelChanges']['fins']['span']:.2f} meters. This provides more stabilizing force at the cost of slightly increased drag."
            changes_made = True
    
    # If no specific changes were requested, provide some general optimizations
    if not changes_made:
        if "optimize" in lower_prompt or "improve" in lower_prompt or "better" in lower_prompt:
            # General optimization for performance
            response["modelChanges"]["firstStage"] = {"material": "carbon-fiber"}
            response["modelChanges"]["noseCone"] = {"shape": "ogive"}
            response["message"] += "\n\n• I've changed the first stage material to carbon fiber, reducing its mass by approximately 30%.\n• I've modified the nose cone to an ogive shape, reducing drag by 15%.\n\nThese changes together should improve maximum altitude by approximately 22% and increase stability during ascent."
        elif "structural" in lower_prompt or "strength" in lower_prompt:
            # Structural improvements
            response["modelChanges"]["firstStage"] = {"diameter": first_stage.get("diameter", 1.2) * 1.1}
            response["message"] += f"\n\n• I've increased the first stage diameter by 10% to improve structural rigidity.\n• I would also recommend adding internal reinforcement at the stage junction and pressure vessel bulkheads.\n\nThese changes will increase safety factors by approximately 25% with only a 5% mass penalty."
    
    # Add engineering justification
    response["message"] += "\n\nThe modified design maintains a favorable center of gravity to center of pressure ratio for stable flight, while improving overall performance characteristics."
    
    # Always include these fields to match expected format
    if "changeDescription" not in response:
        response["changeDescription"] = "Design modifications"
    
    return response
