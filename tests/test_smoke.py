"""
SIH-26227 Smoke Tests — import and basic sanity checks.
Run: pytest tests/test_smoke.py -v
"""

import sys
from pathlib import Path

PROJECT_DIR = Path(__file__).resolve().parent.parent
if str(PROJECT_DIR) not in sys.path:
    sys.path.insert(0, str(PROJECT_DIR))


def test_project_code_import():
    import project_code  # noqa: F401


def test_model_import():
    from project_code.models.siamese_resnet18 import SiameseResNet18UNet
    model = SiameseResNet18UNet(pretrained=False, attention_type="cbam")
    assert model is not None


def test_changeformer_import():
    from project_code.models.lightweight_changeformer import LightweightChangeFormer
    model = LightweightChangeFormer()
    assert model is not None


def test_false_alarm_imports():
    from project_code.false_alarm.registration import RegistrationValidator
    from project_code.false_alarm.quality_mask import QualityMaskFilter
    from project_code.false_alarm.spectral_check import SpectralConsistencyChecker
    from project_code.false_alarm.postprocess import MorphologicalPostProcessor
    assert RegistrationValidator() is not None
    assert QualityMaskFilter() is not None
    assert SpectralConsistencyChecker() is not None
    assert MorphologicalPostProcessor() is not None


def test_retrieval_imports():
    from project_code.retrieval.remoteclip_encoder import RemoteCLIPEncoder
    from project_code.retrieval.qdrant_indexer import QdrantLocalIndexer
    enc = RemoteCLIPEncoder()
    idx = QdrantLocalIndexer()
    assert enc is not None
    assert idx is not None


def test_temporal_imports():
    from project_code.temporal.change_timeline import ChangeTimelineBuilder, EarliestChangeDetector
    assert ChangeTimelineBuilder() is not None
    assert EarliestChangeDetector is not None


def test_provenance_import():
    from project_code.provenance.audit_logger import ProvenanceAuditLogger
    logger = ProvenanceAuditLogger()
    assert logger is not None


def test_config_paths():
    from project_code.config import PROJECT_ROOT, EXPERIMENTS_DIR, DATASETS_DIR
    assert PROJECT_ROOT.exists(), f"PROJECT_ROOT {PROJECT_ROOT} does not exist"


def test_model_forward_pass():
    """Verify one forward pass on synthetic data (CPU)."""
    import torch
    from project_code.models.siamese_resnet18 import SiameseResNet18UNet

    model = SiameseResNet18UNet(pretrained=False, attention_type="cbam")
    model.eval()
    t1 = torch.zeros(1, 3, 256, 256)
    t2 = torch.zeros(1, 3, 256, 256)
    with torch.no_grad():
        out = model(t1, t2)
    assert "change_logits" in out
    assert out["change_logits"].shape == (1, 1, 256, 256)
