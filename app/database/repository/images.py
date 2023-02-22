from .super import SuperRepository
from app.database import ImagesModel

class ImagesRepository(SuperRepository):

    base_model = ImagesModel

    def add(self, path: str):
        
        with self.session_factory() as session:
            image = session.query(self.base_model).filter(ImagesModel.path == path).first()
            if image is None:
                image = ImagesModel(
                    path=path
                )
                session.add(image)
                session.commit()

    def update(self):
        pass