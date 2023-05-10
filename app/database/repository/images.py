from .super import SuperRepository
from app.database import ImagesModel

class ImagesRepository(SuperRepository):

    base_model = ImagesModel

    def add(self, path: str) -> ImagesModel:
        with self.session_factory() as session:
            image = ImagesModel(
                    path=path
                )
            session.add(image)
            session.commit()
            return image
    def update(self):
        pass
