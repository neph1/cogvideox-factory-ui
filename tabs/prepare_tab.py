

import datetime
import os
import sys
import gradio as gr

from typing import OrderedDict
from config import Config
from runner import RunPrepareDataset
from tabs import general_tab
from tabs.tab import Tab

properties = OrderedDict()

class PrepareDatasetTab(Tab):

    def __init__(self, title, config_file_path, allow_load=False):
        super().__init__(title, config_file_path, allow_load)

        try:
            with self.settings_column:
                self.components = OrderedDict(self.update_form())
                for i in range(len(self.settings_column.children)):
                    keys = list(self.components.keys())
                    properties[keys[i]] = self.settings_column.children[i]
                    
        except Exception as e:
            gr.Error(f"Error loading config file: {e}")
            
        with gr.Row(equal_height=False):
            self.add_buttons()

        self.output_box = gr.Textbox(value="", label="Output")

        run_button = gr.Button("Prepare dataset", key='prepare_dataset')
        run_button.click(self.run_prepare_data, 
                        inputs=[*properties.values()],
                        outputs=[self.output_box]
                        )

    def get_properties(self) -> OrderedDict:
        return properties
    
    def run_prepare_data(self, *args):
        time = datetime.datetime.now()
        properties_values = list(args)
        keys_list = list(properties.keys())
        
        config  = Config()
        for index in range(len(properties_values)):
            key = keys_list[index]
            properties[key].value = properties_values[index]
            config.set(key, properties_values[index])
        output_path = os.path.join(properties['output_dir'].value, "config")
        os.makedirs(output_path, exist_ok=True)

        self.save_edits(os.path.join(output_path, "config_{}.yaml".format(time)), *properties_values)
        result = RunPrepareDataset().run(config, general_tab.properties['path_to_cogvideox_factory'].value)
        if result.returncode == 0:
            return "Prepate dataset: Dataset prepared successfully"
        else:
            return "Prepate dataset: Dataset preparation failed"