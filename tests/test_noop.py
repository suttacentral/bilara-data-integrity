from sutta_processor.application.use_cases import noop
from sutta_processor.shared.config import SRC_ROOT, Config


def test_run_noop():
    cfg = Config.from_yaml(f_pth=SRC_ROOT / ".." / "example_config.yaml")
    noop(cfg=cfg)
