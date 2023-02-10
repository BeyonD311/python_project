from .super import SuperRepository, NotFoundError
from app.database.models import SkillsModel

class SkillsRepository(SuperRepository):
    base_model = SkillsModel
    def find_skill(self, text: str):
        with self.session_factory() as session:
            return session.query(self.base_model).filter(self.base_model.name.like(f"%{text}%")).all()
    def add_skill(self, text: str):
        with self.session_factory() as session:
            skill = SkillsModel(name = text.lower())
            session.add(skill)
            session.commit()
            session.flush()
            return skill
    def add(self, arg):
        pass
    def update(self):
        pass


__all__ = ('GroupsRepository')