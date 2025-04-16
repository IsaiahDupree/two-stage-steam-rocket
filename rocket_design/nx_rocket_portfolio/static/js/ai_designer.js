/**
 * AI-Assisted Rocket Design Interface
 * This module handles the interactive design process with AI assistance
 */

// Global variables
let currentModel = {
    name: "Two-Stage Steam Rocket",
    version: "v1.0",
    firstStage: {
        diameter: 1.2,  // meters
        length: 7.2,    // meters
        material: "aluminum-2024"
    },
    secondStage: {
        diameter: 0.8,  // meters
        length: 3.2,    // meters
        material: "aluminum-7075"
    },
    noseCone: {
        shape: "conical",
        length: 1.0,    // meters
    },
    fins: {
        count: 4,
        shape: "trapezoidal",
        span: 0.5       // meters
    }
};

let modelHistory = [
    {
        version: "v1.0",
        date: "2025-04-13",
        description: "Initial design",
        model: JSON.parse(JSON.stringify(currentModel))  // Deep copy
    }
];

let scene, camera, renderer, rocketModel;
let processingRequest = false;

// Initialize the interface
document.addEventListener('DOMContentLoaded', function() {
    initializeChat();
    initializeModelViewer();
    initializeEventListeners();
    loadModelParameters();
});

// Initialize chat interface
function initializeChat() {
    const chatMessages = document.getElementById('chat-messages');
    const promptInput = document.getElementById('prompt-input');
    const sendButton = document.getElementById('send-prompt');
    const clearButton = document.getElementById('clear-chat');
    
    // Send button click handler
    sendButton.addEventListener('click', function() {
        sendPromptToAI();
    });
    
    // Enter key press handler
    promptInput.addEventListener('keydown', function(e) {
        if (e.key === 'Enter' && !e.shiftKey) {
            e.preventDefault();
            sendPromptToAI();
        }
    });
    
    // Clear chat history
    clearButton.addEventListener('click', function() {
        while (chatMessages.children.length > 1) {
            chatMessages.removeChild(chatMessages.lastChild);
        }
    });
}

// Submit message to AI assistant
async function submitMessage() {
    if (processingRequest) return;
    
    const messageInput = document.getElementById('prompt-input');
    const message = messageInput.value.trim();
    
    if (message === '') return;
    
    // Clear input
    messageInput.value = '';
    
    // Add user message to chat
    addMessageToChat('user', message);
    
    // Show processing modal
    showProcessingModal();
    processingRequest = true;
    
    // Prepare request data
    const requestData = {
        prompt: message,
        currentModel: currentModel
    };
    
    try {
        console.log('Sending request:', requestData);
        
        const response = await fetch('/api/ai-design', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(requestData)
        });

        // Check if response is ok
        if (!response.ok) {
            throw new Error(`HTTP error! Status: ${response.status}`);
        }

        const responseText = await response.text();
        console.log('Raw response:', responseText);
        
        let data;
        try {
            data = JSON.parse(responseText);
            console.log('Parsed data:', data);
        } catch (parseError) {
            console.error('JSON parse error:', parseError);
            throw new Error('Invalid JSON response');
        }
        
        // Check if data has expected format
        if (!data.message) {
            console.error('Response missing message field:', data);
            throw new Error('Invalid response format');
        }
        
        // Process AI response
        processAIResponse(data);
        
        // Check for visualizations in the response
        if (data.visualizations) {
            displayDesignVisualizations(data.visualizations);
        }
    } catch (error) {
        console.error('Error:', error);
        addMessageToChat('assistant', 'I encountered an error processing your request: ' + error.message);
    } finally {
        processingRequest = false;
        hideProcessingModal();
    }
}

// Process AI response and update model if needed
function processAIResponse(response) {
    console.log('Processing response:', response);
    
    // Add AI response message to chat
    if (typeof response.message === 'string') {
        addMessageToChat('assistant', response.message);
    } else {
        console.error('Response message is not a string:', response.message);
        addMessageToChat('assistant', 'Received an invalid response format. Please try again.');
        return;
    }
    
    // If model changes were requested
    if (response.modelChanges) {
        console.log('Applying model changes:', response.modelChanges);
        
        // Create a new version
        const newVersion = `v${(modelHistory.length + 1).toFixed(1)}`;
        
        // Update the current model with changes
        applyModelChanges(response.modelChanges);
        
        // Add to history
        const historyEntry = {
            version: newVersion,
            date: new Date().toISOString().split('T')[0],
            description: response.changeDescription || "AI-generated update",
            model: JSON.parse(JSON.stringify(currentModel))  // Deep copy
        };
        
        modelHistory.push(historyEntry);
        updateVersionHistory();
        
        // Update the 3D visualization
        updateRocketModel();
        
        // Update parameters in UI
        loadModelParameters();
    }
}

// Add a message to the chat interface
function addMessageToChat(sender, content) {
    const chatMessages = document.getElementById('chat-messages');
    const messageDiv = document.createElement('div');
    messageDiv.className = `message ${sender}`;
    
    const contentDiv = document.createElement('div');
    contentDiv.className = 'message-content';
    
    // Split content into paragraphs
    const paragraphs = content.split('\n').filter(p => p.trim());
    paragraphs.forEach(paragraph => {
        const p = document.createElement('p');
        p.textContent = paragraph;
        contentDiv.appendChild(p);
    });
    
    messageDiv.appendChild(contentDiv);
    chatMessages.appendChild(messageDiv);
    
    // Scroll to bottom
    chatMessages.scrollTop = chatMessages.scrollHeight;
    
    return messageDiv;
}

// Show processing modal with custom message
function showProcessingModal(message = 'Processing your request...') {
    const processingModal = document.getElementById('processing-modal');
    const messageElement = document.getElementById('processing-message');
    if (messageElement) {
        messageElement.textContent = message;
    }
    processingModal.style.display = 'flex';
}

// Update processing modal message
function updateProcessingMessage(message) {
    const messageElement = document.getElementById('processing-message');
    if (messageElement) {
        messageElement.textContent = message;
    }
}

// Hide processing modal
function hideProcessingModal() {
    const processingModal = document.getElementById('processing-modal');
    processingModal.style.display = 'none';
}

// Analyze the current design for performance
async function analyzeCurrentDesign() {
    addMessageToChat('assistant', 'Analyzing current design...');
    
    // Show processing modal
    showProcessingModal('Generating comprehensive design analysis...');
    
    // Prepare request data
    const requestData = {
        model: currentModel
    };
    
    try {
        const response = await fetch('/api/analyze-design', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(requestData)
        });

        const data = await response.json();
        
        // Display analysis results
        addMessageToChat('assistant', data.analysis || 'Analysis complete. No significant issues found.');
    } catch (error) {
        console.error('Error:', error);
        addMessageToChat('assistant', 'I encountered an error analyzing your design. Please try again.');
    } finally {
        hideProcessingModal();
    }
}

// Optimize the current design with AI
async function optimizeDesign(goal = null) {
    if (!goal) {
        // If no goal provided, ask the user what they want to optimize for
        const goalInput = prompt(
            'What would you like to optimize for?\n\nExamples:\n- Maximize altitude\n- Minimize mass\n- Optimize for speed\n- Improve structural integrity',
            'Optimize overall performance'
        );
        
        if (!goalInput) return; // User canceled
        goal = goalInput;
    }
    
    addMessageToChat('assistant', `Starting optimization for: ${goal}`);
    showProcessingModal('Starting AI-powered design optimization...');
    
    try {
        const currentModel = getCurrentModel();
        
        // Start the optimization process
        const response = await fetch('/api/optimize-design', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                model: currentModel,
                goal: goal
            })
        });

        const data = await response.json();
        
        if (data.status === 'success') {
            const runId = data.run_id;
            addMessageToChat('assistant', `Starting design optimization for: ${goal}. This may take a moment.`);
            
            // Poll for optimization status
            pollOptimizationStatus(runId);
        } else {
            hideProcessingModal();
            addMessageToChat('assistant', `Error starting optimization: ${data.message}`);
        }
    } catch (error) {
        console.error('Error optimizing design:', error);
        hideProcessingModal();
        addMessageToChat('assistant', 'Failed to start design optimization. Please try again.');
    }
}

// Poll for optimization status
async function pollOptimizationStatus(runId, attempts = 0) {
    try {
        if (attempts > 30) { // Limit polling attempts (15 minutes at 30 second intervals)
            hideProcessingModal();
            addMessageToChat('assistant', 'Optimization is taking longer than expected. Please check back later.');
            return;
        }
        
        // Update loading message
        updateProcessingMessage(`Optimization in progress... (${attempts+1}/30)`);
        
        const response = await fetch(`/api/optimization-status/${runId}`, {
            method: 'GET',
            headers: {
                'Content-Type': 'application/json',
            }
        });

        const data = await response.json();
        
        if (data.status === 'success') {
            const optimizationStatus = data.optimization_status;
            
            if (optimizationStatus.status === 'completed') {
                // Optimization complete
                hideProcessingModal();
                displayOptimizationResults(optimizationStatus);
            } else if (optimizationStatus.status === 'error') {
                // Error occurred
                hideProcessingModal();
                addMessageToChat('assistant', `Optimization error: ${optimizationStatus.message}`);
            } else {
                // Still in progress, poll again after delay
                setTimeout(() => pollOptimizationStatus(runId, attempts + 1), 30000);
            }
        } else {
            hideProcessingModal();
            addMessageToChat('assistant', `Error checking optimization status: ${data.message}`);
        }
    } catch (error) {
        console.error('Error polling optimization status:', error);
        hideProcessingModal();
        addMessageToChat('assistant', 'Failed to check optimization status. Please try again.');
    }
}

// Display optimization results
function displayOptimizationResults(optimizationData) {
    // Create message content
    let messageContent = `**Optimization Results: ${optimizationData.goal}**\n\n`;
    
    // Add summary
    messageContent += `${optimizationData.summary}\n\n`;
    
    // Add best design details
    if (optimizationData.best_designs && optimizationData.best_designs.length > 0) {
        const bestDesign = optimizationData.best_designs[optimizationData.best_designs.length - 1];
        messageContent += `**Best Design (Generation ${bestDesign.generation})**\n`;
        messageContent += `- Fitness Score: ${bestDesign.fitness.toFixed(2)}\n`;
        
        // Add design changes
        messageContent += `\n**Key Design Changes:**\n`;
        for (const [key, value] of Object.entries(bestDesign.key_changes)) {
            messageContent += `- ${key}: ${value}\n`;
        }
        
        // Add apply button to chat message
        messageContent += `\n\n[Apply Optimized Design]`;
        
        // Store the optimized model for later use
        window.optimizedModel = bestDesign.model;
    }
    
    // Display the optimization results in the chat
    const messageElement = addMessageToChat('assistant', messageContent);
    
    // Add event listener to the apply button
    if (window.optimizedModel) {
        const applyButton = messageElement.querySelector('a');
        if (applyButton) {
            applyButton.addEventListener('click', (e) => {
                e.preventDefault();
                applyOptimizedModel(window.optimizedModel);
            });
        }
    }
    
    // Display visualization if available
    if (optimizationData.visualizations) {
        displayDesignVisualizations(optimizationData.visualizations);
    }
}

// Apply the optimized model
function applyOptimizedModel(optimizedModel) {
    if (!optimizedModel) return;
    
    // Make sure we have the current model as a starting point
    const currentModelData = getCurrentModel();
    
    // Update the current model with the optimized values
    for (const section in optimizedModel) {
        if (currentModelData[section] && typeof optimizedModel[section] === 'object') {
            // Update section properties
            Object.assign(currentModelData[section], optimizedModel[section]);
        } else {
            // Set property directly
            currentModelData[section] = optimizedModel[section];
        }
    }
    
    // Update the UI with the new model values
    updateUIControls(currentModelData);
    
    // Update the 3D model
    updateRocketModel();
    
    // Notify the user
    addMessageToChat('system', 'Optimized design has been applied!');
}

// Initialize the 3D model viewer
function initializeModelViewer() {
    const container = document.getElementById('rocket-model-display');
    
    // Create scene
    scene = new THREE.Scene();
    scene.background = new THREE.Color(0xf0f0f0);
    
    // Create camera
    camera = new THREE.PerspectiveCamera(45, container.clientWidth / container.clientHeight, 0.1, 1000);
    camera.position.set(0, 0, 20);
    
    // Add lighting
    const ambientLight = new THREE.AmbientLight(0xffffff, 0.5);
    scene.add(ambientLight);
    
    const directionalLight = new THREE.DirectionalLight(0xffffff, 0.8);
    directionalLight.position.set(1, 1, 1);
    scene.add(directionalLight);
    
    // Create renderer
    renderer = new THREE.WebGLRenderer({ antialias: true });
    renderer.setSize(container.clientWidth, container.clientHeight);
    
    // Clear container and add renderer
    container.innerHTML = '';
    container.appendChild(renderer.domElement);
    
    // Initial model creation
    createRocketModel();
    
    // Animation loop
    animate();
    
    // Handle window resize
    window.addEventListener('resize', function() {
        camera.aspect = container.clientWidth / container.clientHeight;
        camera.updateProjectionMatrix();
        renderer.setSize(container.clientWidth, container.clientHeight);
    });
}

// Create 3D rocket model based on parameters
function createRocketModel() {
    // Remove existing model if any
    if (rocketModel) {
        scene.remove(rocketModel);
    }
    
    // Create a new group for the rocket
    rocketModel = new THREE.Group();
    
    // First stage
    const firstStageGeometry = new THREE.CylinderGeometry(
        currentModel.firstStage.diameter / 2, 
        currentModel.firstStage.diameter / 2, 
        currentModel.firstStage.length, 
        32
    );
    const firstStageMaterial = new THREE.MeshStandardMaterial({ color: 0xcccccc });
    const firstStage = new THREE.Mesh(firstStageGeometry, firstStageMaterial);
    firstStage.position.y = -currentModel.firstStage.length / 2;
    rocketModel.add(firstStage);
    
    // Second stage
    const secondStageGeometry = new THREE.CylinderGeometry(
        currentModel.secondStage.diameter / 2, 
        currentModel.firstStage.diameter / 2, 
        currentModel.secondStage.length, 
        32
    );
    const secondStageMaterial = new THREE.MeshStandardMaterial({ color: 0xdddddd });
    const secondStage = new THREE.Mesh(secondStageGeometry, secondStageMaterial);
    secondStage.position.y = currentModel.secondStage.length / 2;
    rocketModel.add(secondStage);
    
    // Nose cone
    let noseConeGeometry;
    if (currentModel.noseCone.shape === 'conical') {
        noseConeGeometry = new THREE.ConeGeometry(
            currentModel.secondStage.diameter / 2, 
            currentModel.noseCone.length, 
            32
        );
    } else if (currentModel.noseCone.shape === 'ogive') {
        // Simplified ogive using lathe
        const points = [];
        const segments = 10;
        for (let i = 0; i <= segments; i++) {
            const t = i / segments;
            const x = (1 - t) * (currentModel.secondStage.diameter / 2);
            // Ogive curve approximation
            const y = currentModel.noseCone.length * t;
            points.push(new THREE.Vector2(x, y));
        }
        noseConeGeometry = new THREE.LatheGeometry(points, 32);
    } else {
        // Elliptical
        const points = [];
        const segments = 10;
        for (let i = 0; i <= segments; i++) {
            const t = i / segments;
            // Elliptical profile
            const x = (currentModel.secondStage.diameter / 2) * Math.sqrt(1 - t*t);
            const y = currentModel.noseCone.length * t;
            points.push(new THREE.Vector2(x, y));
        }
        noseConeGeometry = new THREE.LatheGeometry(points, 32);
    }
    
    const noseConeMaterial = new THREE.MeshStandardMaterial({ color: 0xff3333 });
    const noseCone = new THREE.Mesh(noseConeGeometry, noseConeMaterial);
    noseCone.position.y = currentModel.secondStage.length + currentModel.noseCone.length / 2;
    rocketModel.add(noseCone);
    
    // Add fins if defined
    if (currentModel.fins && currentModel.fins.count > 0) {
        const finShape = new THREE.Shape();
        const finHeight = currentModel.firstStage.diameter / 2;
        const finLength = currentModel.firstStage.length / 4;
        
        finShape.moveTo(0, 0);
        
        if (currentModel.fins.shape === 'trapezoidal') {
            finShape.lineTo(finLength * 0.7, finHeight);
            finShape.lineTo(finLength, finHeight);
            finShape.lineTo(finLength, 0);
        } else if (currentModel.fins.shape === 'triangular') {
            finShape.lineTo(finLength, finHeight);
            finShape.lineTo(finLength, 0);
        } else {
            // Default rectangular
            finShape.lineTo(0, finHeight);
            finShape.lineTo(finLength, finHeight);
            finShape.lineTo(finLength, 0);
        }
        
        const finGeometry = new THREE.ExtrudeGeometry(finShape, {
            depth: 0.05,
            bevelEnabled: false
        });
        
        const finMaterial = new THREE.MeshStandardMaterial({ color: 0x333333 });
        
        // Add multiple fins
        for (let i = 0; i < currentModel.fins.count; i++) {
            const fin = new THREE.Mesh(finGeometry, finMaterial);
            fin.rotation.y = (i * Math.PI * 2) / currentModel.fins.count;
            fin.position.y = -currentModel.firstStage.length * 0.8;
            rocketModel.add(fin);
        }
    }
    
    // Position the rocket model in the scene
    rocketModel.rotation.x = Math.PI; // Flip to stand upright
    scene.add(rocketModel);
    
    // Reset camera position
    camera.position.set(0, 0, Math.max(20, 
        (currentModel.firstStage.length + currentModel.secondStage.length + currentModel.noseCone.length) * 2));
}

// Update the rocket model with current parameters
function updateRocketModel() {
    createRocketModel();
}

// Animation loop for 3D viewer
function animate() {
    requestAnimationFrame(animate);
    
    if (rocketModel) {
        rocketModel.rotation.z += 0.005;
    }
    
    renderer.render(scene, camera);
}
