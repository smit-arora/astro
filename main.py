
from flask import Flask, jsonify, request 
from sqlalchemy import create_engine,text
from sqlalchemy.orm import sessionmaker, relationship
from sqlalchemy.schema import Index
from sqlalchemy import Column, Integer,BigInteger, String, DateTime, Numeric, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
import datetime
import json

Base = declarative_base()

class Merchant(Base):
    __tablename__ = "merchant"
    id = Column(BigInteger, primary_key=True)
    name = Column(String(255))

class Merchandise(Base):
    __tablename__ = "merchandise"
    id = Column(BigInteger, primary_key=True)
    name = Column(String(255))
    created_at= Column(DateTime)

class Merchant_Merchandise(Base):
    __tablename__ = "merchant_merchandise"
    id = Column(Integer, primary_key=True)
    merchant_id = Column(BigInteger, ForeignKey ("merchant.id"))
    merchandise_id= Column(BigInteger, ForeignKey ("merchandise.id"))

class Carrier(Base):
    __tablename__ = "carrier"
    id = Column(BigInteger, primary_key=True)
    name = Column(String(255))
    max_order_per_day =Column(Integer)
    max_merch_per_order=Column(Integer)
    cost_per_order=Column(Numeric(10,2))

class Carrier_Availability(Base):
    __tablename__ = "carrier_availability"
    id = Column(BigInteger, primary_key=True)
    carrier_id = Column(BigInteger, ForeignKey ("carrier.id"))
    no_of_orders_assigned = Column(Integer)
    order_assign_date = Column(DateTime)
    carrier_relationship = relationship("Carrier")
    
class Orders (Base):
    __tablename__ = "orders"
    id = Column(BigInteger, primary_key=True)
    merchant_id = Column(BigInteger, ForeignKey ("merchant.id"))
    status = Column(Integer)
    carrier_id = Column(BigInteger, ForeignKey ("carrier.id"))
    order_created_at = Column(DateTime)
    order_shipped_at = Column(DateTime)


Index(None, Orders.status, Orders.carrier_id)

class Order_detail (Base):
    __tablename__ = "order_detail"
    id = Column(BigInteger, primary_key=True)
    order_id = Column(BigInteger, ForeignKey ("orders.id"))
    merchandise_id = Column(BigInteger, ForeignKey ("merchandise.id"))
    quantity = Column(Integer)

def db_connect():
    connection_string = "mysql+mysqlconnector://flow_shipping:PAss123@localhost:3306/flow_shipping_orm"
    engine = create_engine(connection_string, echo=True)
    Base.metadata.create_all(engine)
    Session = sessionmaker(bind=engine)
    session = Session()
    
    return session

app = Flask(__name__) 

@app.route('/orders/waitingshipping', methods=['GET'])
def get_waiting_shipping():

    session=db_connect()
    orders=session.query(Orders).filter(Orders.status==2).filter(Orders.carrier_id!=None).filter(Orders.order_shipped_at!=None)
    result_list=[]



    for order in orders:
        result_list.append('{"order_id":'+str(order.id)+',"merchant_id":'+str(order.merchant_id)+',"order_created_date":"'+str(order.order_created_at)+'"}')
    return str(result_list).replace("'","")

 
@app.route('/orders/markshipped', methods = ['POST'])   
def mark_order_shipped():
    order_id = request.json['order_id']
    try:
        shipped_date = '"'+request.json['shipped_date']+'"'
    except KeyError:
        shipped_date='NOW()'
    session=db_connect()
    order=session.query(Orders).get(order_id)
    
    if(order.carrier_id != None):
        order.status=3
        order.shipped_date=shipped_date
        session.commit()
        return 'ORDER MARKED AS SHIPPED'
    else:
        return "No Carrier Assigned, can't mark as shipped"

@app.route('/carriers/orderlist', methods = ['GET'])   
def list_orders_carrier():
    carrier_id = request.json['carrier_id']
    
    session=db_connect()
    orders=session.query(Orders).filter(Orders.status==2).filter(Orders.carrier_id==carrier_id)
    result_list=[]
    if orders is not None:
        for item in orders:
                    result_list.append('{"order_id":'+str(item.id)+'}')
        return str(result_list).replace("'","")
    else:
        return "No orders assigned"

@app.route('/order/assign', methods = ['POST'])   
def mark_assign_order():
    order_id = request.json['order_id']
    carrier_id = request.json['carrier_id']
    session=db_connect()
    # rder=session.query(Orders).get(order_id)
    order=session.query(Orders).get(order_id)
    if(order.status != 1):
        return "This order is marked as shipped or assigned to another carrier"
    else:
        order_detail=session.query(Order_detail).filter(Order_detail.order_id==order.id)
        carrier=session.query(Carrier).get(carrier_id)
        for order_item in order_detail:
            if(order_item.quantity>carrier.max_merch_per_order):
                return "Can't assign this order to the carrier, no of merchandise is more than the carrier can carry"
            else:
                list_carrier=list_availiable_carrier()
                data = json.loads(list_carrier)
                print(data)
                if not any(dic["carrier_id"] == carrier_id for dic in data):
                    proceed_flag=0
                    return "This carrier cant carry any more orders"
                print("check")
                order=session.query(Orders).get(order_id)
                order.status=2
                order.carrier_id=carrier_id
                session.commit()
                return 'ORDER MARKED AS SHIPPED'          



@app.route('/carriers/availaible', methods = ['GET'])   
def list_availiable_carrier():
    
    session=db_connect()
    result_list=[]
    result = session.execute(text('SELECT C.id,C.name,(C.max_order_per_day-IFNULL(CA.no_of_orders_assigned,0)) as order_remaining FROM carrier C left join carrier_availability CA on C.id=CA.carrier_id  WHERE C.max_order_per_day>IFNULL(CA.no_of_orders_assigned,0) AND (order_assign_date=DATE(NOW()) OR order_assign_date is null) '))
    print(result.rowcount)
    if (result.rowcount ==0):
        return("No carriers Availaible")
    else:
        for i in result:
            result_list.append('{"carrier_id":'+str(i.id)+',"carrier_name":"'+i.name+'","order_remaining":'+str(i.order_remaining)+'}')
        return str(result_list).replace("'","")
        



if __name__ == '__main__': 
    print("HI")
   
    db_connect()
    app.run(debug = True) 
    