
import datetime
import os
import gradio as gr
from typing import OrderedDict
from config import Config

from run_trainer import RunTrainer
from tabs import general_tab
from tabs.tab import Tab
from trainer_config_validator import TrainerValidator

properties = OrderedDict()

class TrainingTab(Tab):

    def __init__(self, title, config_file_path, allow_load=False):
        super().__init__(title, config_file_path, allow_load)
        self.trainer = RunTrainer()

        try:
            self.config_categories = self.load_config('config/config_categories.yaml')
        except Exception as e:
            gr.Error(f"Error loading config categories file: {e}")

        with self.settings_column:
            for category in self.config_categories.keys():
                self.groups[category] = gr.Accordion(category)
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

        self.output_box = gr.Textbox(value="", label="Output")
        with gr.Row(equal_height=True):
            run_button = gr.Button("Start Training", key='run_trainer')
            stop_button = gr.Button("Stop", key='stop_trainer')

        log_output = gr.File(label="Log File", interactive=False)
        run_button.click(self.run_trainer, 
                        inputs=[*properties.values()],
                        outputs=[self.output_box, log_output]
                        )
        
        stop_button.click(self.stop_trainer, outputs=[self.output_box])

    def get_properties(self) -> OrderedDict:
        return properties
    
    def run_trainer(self, *args):
        time = datetime.datetime.now()
        properties_values = list(args)
        keys_list = list(properties.keys())
        
        config = Config()
        for index in range(len(properties_values)):
            key = keys_list[index]
            properties[key].value = properties_values[index]
            config.set(key, properties_values[index])
        config.set('path_to_finetrainers', general_tab.properties['path_to_finetrainers'].value)

        config_validator = TrainerValidator(config)
        try:
            config_validator.validate()
        except Exception as e:
            return str(e), None

        output_path = os.path.join(properties['output_dir'].value, "config")
        os.makedirs(output_path, exist_ok=True)
        self.save_edits(os.path.join(output_path, "config_{}.yaml".format(time)), *properties_values)

        log_file = os.path.join(output_path, "log_{}.txt".format(time))

        result = self.trainer.run(config, config.get('path_to_finetrainers'), log_file)
        self.trainer.running = False
        if isinstance(result, str):
            return result, log_file
        if result.returncode == 0:
            return "Training finished. Please see the log file for more details.", log_file
        return "Training failed. Please see the log file for more details.", log_file
    
    def stop_trainer(self):
        self.trainer.stop()