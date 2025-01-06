import os
import re

class TrainerValidator:

    def __init__(self, config):
        self.config = config

    def validate(self):
        required_settings = [
            'path_to_finetrainers',
            'accelerate_config',
            'batch_size',
            'beta1',
            'beta2',
            'caption_column',
            'caption_dropout_p',
            'checkpointing_limit',
            'checkpointing_steps',
            'data_root',
            'dataloader_num_workers',
            'epsilon',
            'gpu_ids',
            'gradient_accumulation_steps',
            'id_token',
            'lora_alpha',
            'lr',
            'lr_num_cycles',
            'lr_scheduler',
            'lr_warmup_steps',
            'max_grad_norm',
            'model_name',
            'nccl_timeout',
            'optimizer',
            'pretrained_model_name_or_path',
            'rank',
            'seed',
            'target_modules',
            'train_steps',
            'training_type',
            'validation_steps',
            'video_column',
            'video_resolution_buckets',
            'weight_decay'
        ]

        for setting in required_settings:
            if not self.config.get(setting) and self.config.get(setting) != 0:
                raise ValueError(f"{setting} is required")
            
        self.validate_finetrainers_path()
        self.validate_data_root()
        self.validate_caption_column()
        self.validate_video_column()
        self.validate_video_resolution_buckets()

    def validate_finetrainers_path(self):
        train_script_path = os.path.join(self.config.get('path_to_finetrainers'), 'train.py')
        if not os.path.isfile(train_script_path):
            raise ValueError(f"train.py does not exist at {self.config.get('path_to_finetrainers')}")

    def validate_caption_column(self):
        data_root = self.config.get('data_root')
        caption_column = self.config.get('caption_column')
        if data_root and caption_column:
            file_path = os.path.join(data_root, caption_column)
            if not os.path.isfile(file_path):
                raise ValueError(f"File {caption_column} does not exist at {data_root}")

    def validate_data_root(self):
        data_root = self.config.get('data_root')
        if data_root and not os.path.isdir(data_root):
            raise ValueError(f"data_root path {data_root} does not exist")

    def validate_video_column(self):
        data_root = self.config.get('data_root')
        video_column = self.config.get('video_column')
        if data_root and video_column:
            file_path = os.path.join(data_root, video_column)
            if not os.path.isfile(file_path):
                raise ValueError(f"File {video_column} does not exist at {data_root}")

    def validate_video_resolution_buckets(self):
        buckets = self.config.get('video_resolution_buckets')
        split_buckets =  buckets.split(' ')
        for bucket in split_buckets:
            if not isinstance(bucket, str) or not re.match(r'^\d+x\d+x\d+$', bucket):
                raise ValueError(f"Each bucket must have the format '<frames>x<height>x<width>', but got {bucket}")