from pathlib import Path

import attr

from .base import BaseAggregate


@attr.s(frozen=True)
class SuttaAggregate(BaseAggregate):
    part_pth: Path = Path("sutta")
