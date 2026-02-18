
import logging
from nemo.collections.asr.models.hybrid_rnnt_ctc_bpe_models import EncDecHybridRNNTCTCBPEModel

print("Finding class with _setup_monolingual_tokenizer...")

target_cls = None
for cls in EncDecHybridRNNTCTCBPEModel.mro():
    if '_setup_monolingual_tokenizer' in cls.__dict__:
        target_cls = cls
        print(f"Found method in: {cls.__name__}")
        break

if target_cls:
    print("Patching...")
    original_method = target_cls._setup_monolingual_tokenizer
    
    def wrapped_setup(self, tokenizer_cfg):
        print(f"Patch invoked! Config keys: {tokenizer_cfg.keys()}")
        if 'dir' not in tokenizer_cfg:
            print("Injecting missing 'dir' key...")
            tokenizer_cfg['dir'] = None
        return original_method(self, tokenizer_cfg)
    
    target_cls._setup_monolingual_tokenizer = wrapped_setup
    print("Patch applied.")
else:
    print("Could not find method to patch.")

print("Test complete.")
