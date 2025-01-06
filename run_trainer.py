import os
import signal
import subprocess
import time

from config import Config

class RunTrainer:

    def __init__(self):
        self.running = False
        self.process = None
        pass

    def run(self, config: Config, finetrainers_path: str, log_file: str):

        assert finetrainers_path, "Path to finetrainers is required"
        assert config.get('data_root'), "Data root required"
        assert config.get('pretrained_model_name_or_path'), "pretrained_model_name_or_path required"

        # Model arguments
        model_cmd = f"--model_name {config.get('model_name')} \
        --pretrained_model_name_or_path {config.get('pretrained_model_name_or_path')} \
        --text_encoder_dtype {config.get('text_encoder_dtype')} \
        --text_encoder_2_dtype {config.get('text_encoder_2_dtype')} \
        --text_encoder_3_dtype {config.get('text_encoder_3_dtype')} \
        --vae_dtype {config.get('vae_dtype')} "
        
        if config.get('layerwise_upcasting_modules') != 'none':
            model_cmd += f"--layerwise_upcasting_modules {config.get('layerwise_upcasting_modules')} \
            --layerwise_upcasting_storage_dtype {config.get('layerwise_upcasting_storage_dtype')} \
            --layerwise_upcasting_granularity {config.get('layerwise_upcasting_granularity')} "

        # Dataset arguments
        dataset_cmd = f"--data_root {config.get('data_root')} \
        --video_column {config.get('video_column')} \
        --caption_column {config.get('caption_column')} \
        --id_token {config.get('id_token')} \
        --video_resolution_buckets {config.get('video_resolution_buckets')} \
        --caption_dropout_p {config.get('caption_dropout_p')} \
        --caption_dropout_technique {config.get('caption_dropout_technique')} \
        {'--precompute_conditions' if config.get('precompute_conditions') else ''} "

        # Dataloader arguments
        dataloader_cmd = f"--dataloader_num_workers {config.get('dataloader_num_workers')}"

        # Diffusion arguments TODO: replace later
        diffusion_cmd = f"{config.get('diffusion_options')}"

        # Training arguments
        training_cmd = f"--training_type {config.get('training_type')} \
        --seed {config.get('seed')} \
        --batch_size {config.get('batch_size')} \
        --train_steps {config.get('train_steps')} \
        --rank {config.get('rank')} \
        --lora_alpha {config.get('lora_alpha')} \
        --target_modules {config.get('target_modules')} \
        --gradient_accumulation_steps {config.get('gradient_accumulation_steps')} \
        {'--gradient_checkpointing' if config.get('gradient_checkpointing') else ''} \
        --checkpointing_steps {config.get('checkpointing_steps')} \
        --checkpointing_limit {config.get('checkpointing_limit')} \
        {'--enable_slicing' if config.get('enable_slicing') else ''} \
        {'--enable_tiling' if config.get('enable_tiling') else ''}"

        # Optimizer arguments
        optimizer_cmd = f"--optimizer {config.get('optimizer')} \
        --lr {config.get('lr')} \
        --lr_scheduler {config.get('lr_scheduler')} \
        --lr_warmup_steps {config.get('lr_warmup_steps')} \
        --lr_num_cycles {config.get('lr_num_cycles')} \
        --beta1 {config.get('beta1')} \
        --beta2 {config.get('beta2')} \
        --weight_decay {config.get('weight_decay')} \
        --epsilon {config.get('epsilon')} \
        --max_grad_norm {config.get('max_grad_norm')} \
        {'--use_8bit_bnb' if config.get('use_8bit_bnb') else ''}"

        # Validation arguments
        validation_cmd = f"--validation_prompts \"{config.get('validation_prompts')}\" \
        --num_validation_videos {config.get('num_validation_videos')} \
        --validation_steps {config.get('validation_steps')}"

        # Miscellaneous arguments
        miscellaneous_cmd = f"--tracker_name {config.get('tracker_name')} \
        --output_dir {config.get('output_dir')} \
        --nccl_timeout {config.get('nccl_timeout')} \
        --report_to {config.get('report_to')}"

        cmd = f"accelerate launch --config_file {finetrainers_path}/accelerate_configs/{config.get('accelerate_config')} --gpu_ids {config.get('gpu_ids')} {finetrainers_path}/train.py \
        {model_cmd} \
        {dataset_cmd} \
        {dataloader_cmd} \
        {diffusion_cmd} \
        {training_cmd} \
        {optimizer_cmd} \
        {validation_cmd} \
        {miscellaneous_cmd}"

        print(cmd)
        self.running = True
        with open(log_file, "w") as output_file:
            self.process = subprocess.Popen(cmd, shell=True, stdout=output_file, stderr=output_file, text=True)
            self.process.communicate()
            return self.process
            
        return "Unknown result"
    
    def stop(self):
        try:
            self.running = False
            if self.process:
                self.process.terminate()
                time.sleep(3)
                if self.process.poll() is None:
                    self.process.kill()
        except Exception as e:
            return f"Error stopping training: {e}"
        finally:
            self.process.wait()
        return "Training forcibly stopped"