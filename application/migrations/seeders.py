from flask_seeder import Seeder, faker, generator
import models

class ProductsSeeder(Seeder):

    def create(self, model:models.Products):
        pass
    #     models.
#
#     id = Column(Integer, primary_key=True, name='id')
#     uuid = Column(String(60), nullable=False, name='uuid')
#     sku = Column(Integer, nullable=False, name='sku')
#     name = Column(String(255), nullable=False, name='name')
#     description = Column(TEXT, nullable=False, name='description')
#     supplier_id = Column(Integer, nullable=False, name='supplier_id')
#     created_at = Column(TIMESTAMP, nullable=True, server_default=text('CURRENT_TIMESTAMP'),
#                         name='created_at')
#     updated_at = Column(TIMESTAMP, nullable=True, name='updated_at')
#     deleted_at = Column(TIMESTAMP, nullable=True, name='deleted_at')
#     active = Column(Integer, default=1, name='active')
#
#
# REFERENCES['products'] = ProductsModel
#
#
# def create(db: SQLAlchemy):
#     class Products(db.Model, ProductsModel):
#         pass
#
#     MODELS['products'] = Products

def seed(model_name):
    if model_name in models.MODELS.keys():
        model_class = models.MODELS[model_name]

