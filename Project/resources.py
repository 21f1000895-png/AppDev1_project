from flask_restful import Api, Resource, reqparse
from models import *

api = Api()

parser = reqparse.RequestParser()
parser.add_argument('section_name')
parser.add_argument('product_name')
parser.add_argument('product_unit')
parser.add_argument('product_price')
parser.add_argument('product_quantity')
parser.add_argument('product_section_id')

class Api_sections(Resource):
    def get(self):
        s1 = Section.query.all()
        all_section = {}
        i=1
        for sect in s1:
            this_sect={}
            this_sect["Section_id"]=sect.section_id
            this_sect["Section_name"]=sect.section_name
            all_section[f'item_{i}'] = this_sect
            i+=1
        return all_section

    
    def post(self):
        args = parser.parse_args()
        new_section = Section(section_name = args["section_name"])
        db.session.add(new_section)
        db.session.commit()
        return{
            "message": "resource added successfully"
        }, 201
    
    def put(self, sec_id):
        args = parser.parse_args()
        old_section = Section.query.get(sec_id)
        old_section.section_name = args["section_name"]
        db.session.commit()
        return{
            "message": "resource updated successfully"
        }

    def delete(self,sec_id):
        del_section = Section.query.get(sec_id)
        db.session.delete(del_section)
        db.session.commit()
        return{
            "message": "resource deleted successfully"
        }
#------------------------------------------Api_resource_class_for_products--------------------------------------------
class Api_products(Resource):
    def get(self):
        p1 = Product.query.all()
        all_products = {}
        i=1
        for item in p1:
            this_item={}
            this_item['Product_id'] = item.product_id
            this_item['Product_section_id']= item.sect
            this_item['Product_name']= item.product_name
            this_item['Product_unit']= item.product_unit
            this_item['Product_price']= item.product_price
            this_item['Product_Quantity']= item.product_quantity
            all_products[f'item_{i}']=this_item
            i+=1
        return all_products
    
    def post(self):
        args = parser.parse_args()
        new_product = Product(product_name = args["product_name"],product_unit = args["product_unit"],
                              product_price = args["product_price"],product_quantity = args["product_quantity"],
                              sect = args["product_section_id"])
        print(new_product)
        db.session.add(new_product)
        db.session.commit()
        return{
            "message": "resource added successfully"
        }, 201
    
    def put(self, prod_id):
        args = parser.parse_args()
        old_product = Product.query.get(prod_id)
        old_product.product_name = args["product_name"]
        db.session.commit()
        return{
            "message": "resource updated successfully"
        }
    
    def delete(self,prod_id):
        del_product = Product.query.get(prod_id)
        db.session.delete(del_product)
        db.session.commit()
        return{
            "message": "resource deleted successfully"
        }

    
    
api.add_resource(Api_sections, "/api/all_section","/api/add_section", "/api/update_section/<int:sec_id>", "/api/delete_section/<int:sec_id>")
api.add_resource(Api_products, "/api/all_product", "/api/add_product", "/api/update_product_name/<int:prod_id>", "/api/delete_product/<int:prod_id>")