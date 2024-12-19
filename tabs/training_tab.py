
import os
import gradio as gr
from typing import OrderedDict
from config import Config, global_config

import yaml
from runner import RunCogVideoX
from tabs import general_tab
from tabs.tab import Tab

properties = OrderedDict()

class TrainingTab(Tab):

    def __init__(self, title, config_file_path, allow_load=False):
        super().__init__(title, config_file_path, allow_load)

        try:
            with self.config_inputs:
                self.components = OrderedDict(self.update_form(self.config))
                for i in range(len(self.config_inputs.children)):
                    keys = list(self.components.keys())
                    properties[keys[i]] = self.config_inputs.children[i]
                    
        except Exception as e:
            gr.Error(f"Error loading config file: {e}")
            
        with gr.Row(equal_height=False):
            self.add_buttons()

        self.output_box = gr.Textbox(value="", label="Output")
        run_button = gr.Button("Run Training", key='run_cogvideox')
        run_button.click(self.run_cogvideox, 
                        inputs=[*properties.values()],
                        outputs=[self.output_box]
                        )

    def get_properties(self) -> OrderedDict:
        return properties
    
    def run_cogvideox(self, *args):
        properties_values = list(args)
        keys_list = list(properties.keys())
        general_properties = general_tab.properties
        
        config  = Config()
        for index in range(len(properties_values)):
            key = keys_list[index]
            properties[key].value = properties_values[index]
            config.set(key, properties_values[index])
        output_path = os.path.join(properties['output_dir'].value, "config")
        os.makedirs(output_path, exist_ok=True)
        result = RunCogVideoX().run_cogvideox(config, general_tab.properties['path_to_cogvideox_factory'].value)
        if result.returncode == 0:
            return "Run Training: Training completed successfully"
        else:
            return "Run Training: Training failed"
    