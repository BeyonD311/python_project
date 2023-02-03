from .super import SuperRepository, NotFoundError
from app.database import PositionModel
from typing import Iterator


class PositionRepository(SuperRepository):
    base_model = PositionModel

    def get_all(self) -> Iterator[PositionModel]:
        return super().get_all()
    def get_by_id(self, id: int) -> PositionModel:
        return super().get_by_id(id)


__all__ = ('PositionRepository')