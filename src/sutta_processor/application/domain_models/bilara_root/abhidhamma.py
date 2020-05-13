from pathlib import Path

import attr

from .base import BaseAggregate


@attr.s(frozen=True)
class AbhidhammaAggregate(BaseAggregate):
    part_pth: Path = Path("abhidhamma")
