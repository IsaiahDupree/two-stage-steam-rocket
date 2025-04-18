#!/usr/bin/env python
"""
Drone Nose Cone GUI
A simple graphical interface for adjusting nose cone parameters and generating models.
"""

import os
import sys
import json
import subprocess
import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import threading
import time

# Define the default parameters
DEFAULT_PARAMS = {
    "inner_diameter": 67.0,  # mm
    "outer_diameter": 78.0,  # mm
    "base_ring_depth": 13.0,  # mm
    "cone_angle": 52.0,      # degrees
    "use_lightweighting": True,
    "shell_thickness": 1.2,  # mm
    "internal_ribs": True,
    "rib_count": 6           # number of ribs
}

CONFIG_FILE = os.path.join(os.path.dirname(__file__), "parameters.json")

class NoseConeDesignerApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Drone Nose Cone Designer")
        self.root.geometry("800x700")
        self.root.resizable(True, True)
        
        # Set up the parameter values
        self.params = self.read_parameters()
        
        # Create the main frame
        self.create_widgets()
        
        # Status variables
        self.status_var = tk.StringVar(value="Ready")
        self.progress_var = tk.DoubleVar(value=0)
        
        # Set up the layout
        self.setup_layout()
    
    def read_parameters(self):
        """Read parameters from the config file if it exists, otherwise use defaults"""
        if os.path.exists(CONFIG_FILE):
            try:
                with open(CONFIG_FILE, 'r') as f:
                    return json.load(f)
            except Exception as e:
                print(f"Error reading config: {e}")
                return DEFAULT_PARAMS.copy()
        return DEFAULT_PARAMS.copy()
    
    def save_parameters(self):
        """Save parameters to the config file"""
        try:
            with open(CONFIG_FILE, 'w') as f:
                json.dump(self.params, f, indent=2)
            self.status_var.set(f"Parameters saved to {CONFIG_FILE}")
        except Exception as e:
            self.status_var.set(f"Error saving parameters: {e}")
    
    def create_widgets(self):
        """Create all the GUI widgets"""
        # Create a notebook (tabs)
        self.notebook = ttk.Notebook(self.root)
        
        # Tab 1 - Parameters
        self.tab_params = ttk.Frame(self.notebook)
        self.notebook.add(self.tab_params, text="Parameters")
        
        # Tab 2 - Advanced
        self.tab_advanced = ttk.Frame(self.notebook)
        self.notebook.add(self.tab_advanced, text="Advanced")
        
        # Tab 3 - Output
        self.tab_output = ttk.Frame(self.notebook)
        self.notebook.add(self.tab_output, text="Output")
        
        # Tab 4 - Help
        self.tab_help = ttk.Frame(self.notebook)
        self.notebook.add(self.tab_help, text="Help")
        
        # Create parameter widgets on Tab 1
        self.create_parameter_widgets()
        
        # Create advanced widgets on Tab 2
        self.create_advanced_widgets()
        
        # Create output widgets on Tab 3
        self.create_output_widgets()
        
        # Create help widgets on Tab 4
        self.create_help_widgets()
        
        # Create status bar
        self.status_frame = ttk.Frame(self.root)
        ttk.Label(self.status_frame, textvariable=self.status_var).pack(side=tk.LEFT, padx=5)
        self.progress_bar = ttk.Progressbar(self.status_frame, variable=self.progress_var, 
                                           length=200, mode='determinate')
        self.progress_bar.pack(side=tk.RIGHT, padx=5)
    
    def setup_layout(self):
        """Set up the layout of the widgets"""
        self.notebook.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        self.status_frame.pack(fill=tk.X, side=tk.BOTTOM, padx=10, pady=5)
    
    def create_parameter_widgets(self):
        """Create widgets for the Parameters tab"""
        # Create a frame for the parameters
        params_frame = ttk.LabelFrame(self.tab_params, text="Nose Cone Parameters")
        params_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Basic parameters
        row = 0
        
        # Helper function for creating parameter rows
        def add_param_row(label_text, param_name, min_val, max_val, default_val, step=0.1, row_num=None):
            nonlocal row
            if row_num is not None:
                row = row_num
            
            ttk.Label(params_frame, text=label_text).grid(row=row, column=0, sticky=tk.W, padx=5, pady=2)
            
            # Create a variable to store the value
            var = tk.DoubleVar(value=self.params.get(param_name, default_val))
            scale = ttk.Scale(params_frame, from_=min_val, to=max_val, variable=var,
                             orient=tk.HORIZONTAL, length=300)
            scale.grid(row=row, column=1, sticky=tk.W, padx=5, pady=2)
            
            # Entry for direct value input
            entry = ttk.Entry(params_frame, textvariable=var, width=8)
            entry.grid(row=row, column=2, padx=5, pady=2)
            
            # Add a unit label
            ttk.Label(params_frame, text="mm" if "diameter" in param_name or "depth" in param_name 
                                      else "°" if param_name == "cone_angle" else "").grid(
                row=row, column=3, sticky=tk.W, padx=2, pady=2)
            
            # Store the variable for later access
            setattr(self, f"{param_name}_var", var)
            
            row += 1
            return var
        
        # Add parameter rows
        add_param_row("Inner Diameter:", "inner_diameter", 10, 200, 67.0)
        add_param_row("Outer Diameter:", "outer_diameter", 20, 250, 78.0)
        add_param_row("Base Ring Depth:", "base_ring_depth", 1, 50, 13.0)
        add_param_row("Cone Angle:", "cone_angle", 10, 85, 52.0)
        add_param_row("Shell Thickness:", "shell_thickness", 0.5, 5, 1.2)
        
        # Add checkbox for lightweighting
        row += 1
        self.use_lightweighting_var = tk.BooleanVar(value=self.params.get("use_lightweighting", True))
        ttk.Checkbutton(params_frame, text="Use Lightweighting", variable=self.use_lightweighting_var).grid(
            row=row, column=0, columnspan=2, sticky=tk.W, padx=5, pady=5)
        
        # Add checkbox for internal ribs
        row += 1
        self.internal_ribs_var = tk.BooleanVar(value=self.params.get("internal_ribs", True))
        ttk.Checkbutton(params_frame, text="Use Internal Ribs", variable=self.internal_ribs_var).grid(
            row=row, column=0, columnspan=2, sticky=tk.W, padx=5, pady=5)
        
        # Add rib count
        row += 1
        ttk.Label(params_frame, text="Number of Ribs:").grid(row=row, column=0, sticky=tk.W, padx=5, pady=2)
        self.rib_count_var = tk.IntVar(value=self.params.get("rib_count", 6))
        rib_spinner = ttk.Spinbox(params_frame, from_=3, to=12, textvariable=self.rib_count_var, width=5)
        rib_spinner.grid(row=row, column=1, sticky=tk.W, padx=5, pady=2)
        
        # Add buttons at the bottom
        button_frame = ttk.Frame(self.tab_params)
        button_frame.pack(fill=tk.X, side=tk.BOTTOM, padx=10, pady=10)
        
        ttk.Button(button_frame, text="Apply Changes", command=self.apply_changes).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="Reset to Default", command=self.reset_parameters).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="Generate Models", command=self.generate_models).pack(side=tk.RIGHT, padx=5)
        
    def create_advanced_widgets(self):
        """Create widgets for the Advanced tab"""
        # Create a frame for advanced options
        adv_frame = ttk.LabelFrame(self.tab_advanced, text="Advanced Settings")
        adv_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Tip rounding control
        ttk.Label(adv_frame, text="Tip Rounding Factor:").grid(row=0, column=0, sticky=tk.W, padx=5, pady=2)
        self.tip_factor_var = tk.DoubleVar(value=0.5)  # Default factor is 0.5 of outer radius
        tip_scale = ttk.Scale(adv_frame, from_=0.1, to=1.0, variable=self.tip_factor_var,
                             orient=tk.HORIZONTAL, length=300)
        tip_scale.grid(row=0, column=1, sticky=tk.W, padx=5, pady=2)
        ttk.Entry(adv_frame, textvariable=self.tip_factor_var, width=8).grid(row=0, column=2, padx=5, pady=2)
        
        # Wall thinning options
        ttk.Label(adv_frame, text="Wall Thinning Factor:").grid(row=1, column=0, sticky=tk.W, padx=5, pady=2)
        self.wall_thinning_var = tk.DoubleVar(value=1.0)  # Default is no thinning
        wall_scale = ttk.Scale(adv_frame, from_=0.5, to=1.0, variable=self.wall_thinning_var,
                              orient=tk.HORIZONTAL, length=300)
        wall_scale.grid(row=1, column=1, sticky=tk.W, padx=5, pady=2)
        ttk.Entry(adv_frame, textvariable=self.wall_thinning_var, width=8).grid(row=1, column=2, padx=5, pady=2)
        
        # Additional design variations
        variations_frame = ttk.LabelFrame(self.tab_advanced, text="Design Variations")
        variations_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        self.design_var = tk.StringVar(value="standard")
        ttk.Radiobutton(variations_frame, text="Standard Rounded Tip", 
                       variable=self.design_var, value="standard").pack(anchor=tk.W, padx=5, pady=2)
        ttk.Radiobutton(variations_frame, text="Ogive (Parabolic) Profile", 
                       variable=self.design_var, value="ogive").pack(anchor=tk.W, padx=5, pady=2)
        ttk.Radiobutton(variations_frame, text="Elliptical Profile", 
                       variable=self.design_var, value="elliptical").pack(anchor=tk.W, padx=5, pady=2)
        ttk.Radiobutton(variations_frame, text="Von Kármán Profile (Low Drag)", 
                       variable=self.design_var, value="karman").pack(anchor=tk.W, padx=5, pady=2)
        
        # Export options
        export_frame = ttk.LabelFrame(self.tab_advanced, text="Export Options")
        export_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        ttk.Label(export_frame, text="File Formats:").grid(row=0, column=0, sticky=tk.W, padx=5, pady=2)
        
        self.export_stl_var = tk.BooleanVar(value=True)
        ttk.Checkbutton(export_frame, text="STL", variable=self.export_stl_var).grid(
            row=0, column=1, sticky=tk.W, padx=5, pady=2)
        
        self.export_obj_var = tk.BooleanVar(value=False)
        ttk.Checkbutton(export_frame, text="OBJ", variable=self.export_obj_var).grid(
            row=0, column=2, sticky=tk.W, padx=5, pady=2)
        
        self.export_step_var = tk.BooleanVar(value=False)
        ttk.Checkbutton(export_frame, text="STEP", variable=self.export_step_var).grid(
            row=0, column=3, sticky=tk.W, padx=5, pady=2)
        
        ttk.Label(export_frame, text="Resolution:").grid(row=1, column=0, sticky=tk.W, padx=5, pady=2)
        self.resolution_var = tk.StringVar(value="medium")
        resolution_combo = ttk.Combobox(export_frame, textvariable=self.resolution_var, 
                                      values=["low", "medium", "high", "ultra"], width=10)
        resolution_combo.grid(row=1, column=1, columnspan=2, sticky=tk.W, padx=5, pady=2)
        
    def create_output_widgets(self):
        """Create widgets for the Output tab"""
        # Create a frame for the output view
        output_frame = ttk.Frame(self.tab_output)
        output_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Create a text widget for output
        self.output_text = tk.Text(output_frame, wrap=tk.WORD, height=15)
        self.output_text.pack(fill=tk.BOTH, expand=True, side=tk.TOP)
        
        # Add scrollbar
        scrollbar = ttk.Scrollbar(self.output_text, command=self.output_text.yview)
        scrollbar.pack(fill=tk.Y, side=tk.RIGHT)
        self.output_text.config(yscrollcommand=scrollbar.set)
        
        # Add buttons for output actions
        button_frame = ttk.Frame(output_frame)
        button_frame.pack(fill=tk.X, side=tk.BOTTOM, padx=5, pady=5)
        
        ttk.Button(button_frame, text="View Report", command=self.view_report).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="Run Validation", command=self.run_validation).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="Open Output Folder", command=self.open_output_folder).pack(side=tk.RIGHT, padx=5)
        ttk.Button(button_frame, text="Clear Output", command=self.clear_output).pack(side=tk.RIGHT, padx=5)
        
        # Add an image preview frame
        preview_frame = ttk.LabelFrame(output_frame, text="Preview")
        preview_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        self.preview_label = ttk.Label(preview_frame, text="No preview available")
        self.preview_label.pack(fill=tk.BOTH, expand=True)
        
    def create_help_widgets(self):
        """Create widgets for the Help tab"""
        help_frame = ttk.Frame(self.tab_help)
        help_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Help text
        help_text = """
        # Drone Nose Cone Designer
        
        This application helps you design and generate 3D models for drone nose cones.
        
        ## Parameters Tab
        - **Inner Diameter**: The inside diameter of the nose cone (where it fits into the fuselage)
        - **Outer Diameter**: The outside diameter of the nose cone base
        - **Base Ring Depth**: How deep the nose cone inserts into the fuselage
        - **Cone Angle**: The angle of the cone sides (from vertical)
        - **Shell Thickness**: Wall thickness for hollow parts
        - **Lightweighting**: Makes the model hollow to reduce weight
        - **Internal Ribs**: Adds support structures inside the hollow cone
        
        ## Advanced Tab
        - **Tip Rounding**: Controls how rounded the tip of the cone is
        - **Wall Thinning**: Gradually reduces wall thickness toward the tip
        - **Design Variations**: Different nose cone profiles for various aerodynamic properties
        - **Export Options**: Choose file formats and resolution for export
        
        ## Output Tab
        - View validation reports and model output
        - Access the output files
        
        ## Getting Started
        1. Adjust parameters to match your requirements
        2. Click "Apply Changes" to update the model
        3. Click "Generate Models" to create 3D files
        4. Check the Output tab to see the results
        
        For more information, visit the project's GitHub repository.
        """
        
        # Create a text widget for help content
        help_text_widget = tk.Text(help_frame, wrap=tk.WORD)
        help_text_widget.pack(fill=tk.BOTH, expand=True)
        help_text_widget.insert(tk.END, help_text)
        help_text_widget.config(state=tk.DISABLED)  # Make it read-only
        
        # Add scrollbar
        scrollbar = ttk.Scrollbar(help_text_widget, command=help_text_widget.yview)
        scrollbar.pack(fill=tk.Y, side=tk.RIGHT)
        help_text_widget.config(yscrollcommand=scrollbar.set)
    
    def apply_changes(self):
        """Apply parameter changes to the model"""
        # Update parameters from the UI
        self.params["inner_diameter"] = self.inner_diameter_var.get()
        self.params["outer_diameter"] = self.outer_diameter_var.get()
        self.params["base_ring_depth"] = self.base_ring_depth_var.get()
        self.params["cone_angle"] = self.cone_angle_var.get()
        self.params["use_lightweighting"] = self.use_lightweighting_var.get()
        self.params["shell_thickness"] = self.shell_thickness_var.get()
        self.params["internal_ribs"] = self.internal_ribs_var.get()
        self.params["rib_count"] = self.rib_count_var.get()
        
        # Validate parameters
        valid, message = self.validate_parameters()
        if not valid:
            messagebox.showerror("Parameter Error", message)
            return
        
        # Save parameters
        self.save_parameters()
        
        # Run the parameter update script
        self.run_script("adjust_parameters.py")
        
        # Update status
        self.status_var.set("Parameters applied successfully")
    
    def reset_parameters(self):
        """Reset parameters to default values"""
        if messagebox.askyesno("Reset Parameters", "Reset all parameters to default values?"):
            # Reset the parameters
            self.params = DEFAULT_PARAMS.copy()
            
            # Update the UI controls
            self.inner_diameter_var.set(self.params["inner_diameter"])
            self.outer_diameter_var.set(self.params["outer_diameter"])
            self.base_ring_depth_var.set(self.params["base_ring_depth"])
            self.cone_angle_var.set(self.params["cone_angle"])
            self.use_lightweighting_var.set(self.params["use_lightweighting"])
            self.shell_thickness_var.set(self.params["shell_thickness"])
            self.internal_ribs_var.set(self.params["internal_ribs"])
            self.rib_count_var.set(self.params["rib_count"])
            
            # Save parameters
            self.save_parameters()
            
            # Run the parameter update script
            self.run_script("adjust_parameters.py", ["--reset"])
            
            # Update status
            self.status_var.set("Parameters reset to defaults")
    
    def generate_models(self):
        """Generate 3D models with current parameters"""
        # Apply changes first
        self.apply_changes()
        
        # Use threading to keep the UI responsive
        self.status_var.set("Generating models...")
        self.progress_var.set(0)
        
        # Create a thread to run the generation
        threading.Thread(target=self._run_generation).start()
    
    def _run_generation(self):
        """Run model generation in a separate thread"""
        try:
            # Update progress
            self.root.after(100, lambda: self.progress_var.set(10))
            
            # Run the validation script
            self.root.after(200, lambda: self.status_var.set("Running validation..."))
            result = self.run_script("validate_design.py", capture_output=True)
            self.root.after(300, lambda: self.progress_var.set(30))
            
            if result and result.returncode == 0:
                # Add the output to the text widget
                self.root.after(0, lambda: self.update_output_text(result.stdout))
            
            # Run the visualization script
            self.root.after(400, lambda: self.status_var.set("Generating visualization..."))
            self.run_script("visualize_design.py")
            self.root.after(500, lambda: self.progress_var.set(60))
            
            # Run the generator script
            self.root.after(600, lambda: self.status_var.set("Generating OpenSCAD files..."))
            self.run_script("nose_cone_generator.py")
            self.root.after(700, lambda: self.progress_var.set(90))
            
            # Update UI when complete
            self.root.after(800, lambda: self.progress_var.set(100))
            self.root.after(900, lambda: self.status_var.set("Models generated successfully"))
            
            # Try to load a preview image
            self.root.after(1000, self.load_preview)
            
        except Exception as e:
            self.root.after(0, lambda: self.status_var.set(f"Error: {e}"))
    
    def run_validation(self):
        """Run the validation script and display the results"""
        self.status_var.set("Running validation...")
        
        # Create a thread to run the validation
        threading.Thread(target=self._run_validation).start()
    
    def _run_validation(self):
        """Run validation in a separate thread"""
        try:
            # Run the validation script
            result = self.run_script("validate_design.py", capture_output=True)
            
            if result and result.returncode == 0:
                # Add the output to the text widget
                self.root.after(0, lambda: self.update_output_text(result.stdout))
                self.root.after(100, lambda: self.status_var.set("Validation complete"))
            else:
                self.root.after(0, lambda: self.status_var.set("Validation failed"))
        except Exception as e:
            self.root.after(0, lambda: self.status_var.set(f"Error: {e}"))
    
    def view_report(self):
        """View the validation report"""
        # Just run validation as it displays the report
        self.run_validation()
    
    def open_output_folder(self):
        """Open the output folder in explorer"""
        output_dir = os.path.join(os.path.dirname(__file__), "output")
        if not os.path.exists(output_dir):
            os.makedirs(output_dir)
        
        # Open folder in explorer
        if sys.platform == 'win32':
            os.startfile(output_dir)
        elif sys.platform == 'darwin':  # macOS
            subprocess.run(['open', output_dir])
        else:  # Linux
            subprocess.run(['xdg-open', output_dir])
    
    def clear_output(self):
        """Clear the output text"""
        self.output_text.delete(1.0, tk.END)
    
    def update_output_text(self, text):
        """Update the output text widget"""
        self.output_text.delete(1.0, tk.END)
        self.output_text.insert(tk.END, text)
    
    def load_preview(self):
        """Load a preview image if available"""
        # Check for diagram image
        image_path = os.path.join(os.path.dirname(__file__), "output", "nose_cone_diagram.png")
        
        if os.path.exists(image_path):
            try:
                from PIL import Image, ImageTk
                
                # Load the image
                img = Image.open(image_path)
                
                # Resize to fit in the preview area
                width, height = img.size
                max_width = 400
                max_height = 300
                
                if width > max_width or height > max_height:
                    ratio = min(max_width / width, max_height / height)
                    new_width = int(width * ratio)
                    new_height = int(height * ratio)
                    img = img.resize((new_width, new_height), Image.LANCZOS)
                
                # Convert to PhotoImage and display
                photo = ImageTk.PhotoImage(img)
                self.preview_label.config(image=photo)
                self.preview_label.image = photo  # Keep a reference
            
            except Exception as e:
                self.preview_label.config(text=f"Error loading preview: {e}")
        else:
            self.preview_label.config(text="No preview image available.\nGenerate models to create previews.")
    
    def run_script(self, script_name, args=None, capture_output=False):
        """Run a Python script"""
        if args is None:
            args = []
        
        script_path = os.path.join(os.path.dirname(__file__), script_name)
        
        if not os.path.exists(script_path):
            self.status_var.set(f"Script not found: {script_path}")
            return None
        
        try:
            if capture_output:
                result = subprocess.run([sys.executable, script_path] + args, 
                                      capture_output=True, text=True)
                return result
            else:
                subprocess.run([sys.executable, script_path] + args)
                return True
        except Exception as e:
            self.status_var.set(f"Error running script: {e}")
            return None
    
    def validate_parameters(self):
        """Validate parameter values"""
        inner_diameter = self.params["inner_diameter"]
        outer_diameter = self.params["outer_diameter"]
        base_ring_depth = self.params["base_ring_depth"]
        cone_angle = self.params["cone_angle"]
        
        # Basic validation
        if inner_diameter <= 0:
            return False, "Inner diameter must be positive"
        if outer_diameter <= 0:
            return False, "Outer diameter must be positive"
        if base_ring_depth <= 0:
            return False, "Base ring depth must be positive"
        if cone_angle <= 0 or cone_angle >= 90:
            return False, "Cone angle must be between 0 and 90 degrees"
        
        # Relationship validation
        if outer_diameter <= inner_diameter:
            return False, "Outer diameter must be larger than inner diameter"
        
        # More advanced validation could be added here
        
        return True, "Parameters valid"

def main():
    root = tk.Tk()
    app = NoseConeDesignerApp(root)
    root.mainloop()

if __name__ == "__main__":
    main()
