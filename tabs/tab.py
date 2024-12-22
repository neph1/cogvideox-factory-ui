from abc import ABC
from typing import OrderedDict
import gradio as gr
import yaml
import editor_factory

class Tab(ABC):

    def __init__(self, title, config_file_path, allow_load=False):
        self.title = title
        self.allow_load = allow_load
        gr.Markdown(title)
    
        self.status = gr.Markdown()
        self.config_inputs = gr.Column("Settings")
        self.save_status = gr.Markdown()
        # try:
        #     self.config = self.load_config(config_file_path)
        #     with self.config_inputs:
        #         self.components = OrderedDict(self.update_form(self.config))
        #     print("config_inputs", self.config_inputs.children)
        # except Exception as e:
        #     gr.Error(f"Error loading config file: {e}")
        self.config_file_box = gr.Textbox(value=config_file_path, label="Config file")

        try:
            self.config = self.load_config(config_file_path)
        except Exception as e:
            gr.Error(f"Error loading config file: {e}")

    def load_config(self, file_path):
        with open(file_path, "r") as file:
            return yaml.safe_load(file)

    def save_config(self, file_path):
        with open(file_path, "w") as file:
            yaml.dump(self.config, file, default_flow_style=False)

    def save_edits(self,*args):
        args_list = list(args)
        config_file = args_list[0]
        properties_values = args_list[1:]
        properties = self.get_properties()
        keys_list = list(properties.keys())
        try:

            for key in keys_list:
                if key not in self.config.keys():
                    continue
                index = keys_list.index(key)
                value = properties_values[index]
                self.config[key] = value if value else False
            self.save_config(config_file)
            return f"Config saved successfully: {self.config} to {config_file}", config_file
        except Exception as e:
            return f"Error saving config: {e}", ""

    def add_buttons(self):
        """Add Save and Load buttons for the tab."""
        if self.allow_load:
            config_file = gr.File(label="Upload Config File")
        save_button = gr.Button("Save Config")
        
        save_button.click(
            self.save_edits,
            inputs=[self.config_file_box, *self.get_properties().values()],
            outputs=[self.save_status, self.config_file_box]
        )

        if self.allow_load:
            load_button = gr.Button("Load Config")
            load_button.click(
                self.render_editor, 
                inputs=[config_file, self.config_file_box, *self.get_properties().values()], 
                outputs=[self.save_status, self.config_file_box, *self.get_properties().values()]
            )

    def update_form(self, config):
        inputs = dict()
        for key, value in config.items():
            if isinstance(value, bool):
                inputs[key] = (gr.Checkbox(value=value, label=key))
            elif isinstance(value, str):
                inputs[key] = (gr.Textbox(value=value, label=key, interactive=True))
            elif isinstance(value, list):
                inputs[key] = (gr.Dropdown(value=value[0], label=key, choices=value))
            else:
                inputs[key] = (gr.Textbox(value=str(value), label=key))
            
        return inputs
    
    def get_properties(self) -> OrderedDict:
        pass
    
    def render_editor(self, *args):
        args_list = list(args)
        config_file = args_list[0]
        config_file_box = args_list[1]
        properties_values = args_list[2:]
        try:
            with open(config_file, "r") as file:
                new_config = yaml.safe_load(file)
            props_list = list(self.get_properties().keys())
            for key, value in new_config.items():
                
                index = props_list.index(key)
                key = props_list[index]
                
                properties_values[index] = value
                #properties[key].value = value
            return ["Config loaded. Edit below:", config_file_box, *properties_values]
        except Exception as e:
            return [f"Error loading config: {e}", config_file_box, *properties_values]