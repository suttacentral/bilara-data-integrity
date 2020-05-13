from pathlib import Path

import attr

from .base import BaseAggregate


@attr.s(frozen=True)
class VinayaAggregate(BaseAggregate):
    part_pth = Path("vinaya")
