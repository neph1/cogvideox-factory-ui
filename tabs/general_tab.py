
import gradio as gr
from typing import OrderedDict

from tabs.tab import Tab

properties = OrderedDict()

class GeneralTab(Tab):

    def __init__(self, title, config_file_path, allow_load=False):
        super().__init__(title, config_file_path, allow_load)
        with self.settings_column:
            self.groups['Other'] = gr.Accordion('Other')
    
        try:
            with self.settings_column:
                inputs = self.update_form()
                self.components = OrderedDict(inputs)
                children = []
                for child in self.settings_column.children:
                    if isinstance(child, gr.Accordion):
                        for sub_child in child.children:
                            properties[sub_child.children[0].label] = sub_child.children[0]
                            children.append(sub_child.children[0])

        except Exception as e:
            gr.Error(f"Error loading config file: {e}")
            
        with gr.Row(equal_height=False):
            self.add_buttons()

    def get_properties(self) -> OrderedDict:
        return properties