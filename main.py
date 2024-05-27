
from flask import Flask, jsonify, request 
from sqlalchemy import create_engine
from sqlalchemy import text
import json

def db_connect():
    connection_string = "mysql+mysqlconnector://flow_shipping:PAss123@localhost:3306/flow_shipping"
    engine = create_engine(connection_string, echo=True)
    print("=========")
    print(type(engine))
    with engine.connect() as con:
        query=text('SELECT * FROM merchant')
        rs = con.execute(query)

        for row in rs:
            print(row)
    return engine
  
# creating a Flask app 
app = Flask(__name__) 
  
# on the terminal type: curl http://127.0.0.1:5000/ 
# returns hello world when we use GET. 
# returns the data that we send when we use POST. 
@app.route('/', methods = ['GET', 'POST']) 
def home(): 
    if(request.method == 'GET'): 
        db_connect()
        data = "hello world"
        return jsonify({'data': data}) 
  

@app.route('/orders/markshipped', methods = ['POST'])   
def mark_order_shipped():
    order_id = request.json['order_id']
    try:
        shipped_date = '"'+request.json['shipped_date']+'"'
    except KeyError:
        shipped_date='NOW()'
    engine=db_connect()
    with engine.connect() as con:
        check_query=text('SELECT carrier_id FROM orders where id='+str(order_id))
        rs = con.execute(check_query)
        result=rs.first()[0]
        
        if(result!=None):
            update_query=text('UPDATE orders SET status=3, order_shipped_at='+str(shipped_date)+' WHERE id='+str(order_id))
            con.execute(update_query)
            con.commit()
        else:
            return "No Carrier Assigned, can't mark as shipped"
    return 'ORDER MARKED AS SHIPPED'


@app.route('/orders/waitingshipping', methods=['GET'])
def get_waiting_shipping():

    engine=db_connect()
    with engine.connect() as con:
        check_query=text('SELECT id,merchant_id,order_created_at FROM orders where status=2 AND carrier_id is not null and order_shipped_at is null')
        rs = con.execute(check_query)
        con.commit()
        result=rs.fetchall()
        if(len(result)==0):
            return "No Orders are waiting to be shipped"
        else:
            result_list=[]
            for item in result:
                result_list.append('{"order_id":'+str(item[0])+',"merchant_id":'+str(item[1])+',"order_created_date":"'+str(item[2].strftime("%d-%m-%Y %H:%M:%S"))+'"}')
            print(result_list)
            return str(result_list).replace("'","")

@app.route('/carriers/orderlist', methods = ['GET'])   
def list_orders_carrier():
    carrier_id = request.json['carrier_id']
    
    engine=db_connect()
    with engine.connect() as con:
        list_query=text('SELECT id FROM orders where status=2 and carrier_id='+str(carrier_id))
        rs = con.execute(list_query)
        con.commit()
        result=rs.fetchall()
        print(result)
        if(len(result)==0):
            return "No orders assigned"
        else:
            result_list=[]
            for item in result:
                result_list.append('{"order_id":'+str(item[0])+'}')
            print(result_list)
            return str(result_list).replace("'","")


@app.route('/carriers/availaible', methods = ['GET'])   
def list_availiable_carrier():
    
    engine=db_connect()
    with engine.connect() as con:
        carrier_query=text('SELECT C.id,C.name,(C.max_order_per_day-IFNULL(CA.no_of_orders_assigned,0)) as order_remaining FROM carrier C left join carrier_availability CA on C.id=CA.carrier_id  AND (order_assign_date=DATE(NOW()) OR order_assign_date is null) WHERE (C.max_order_per_day>IFNULL(CA.no_of_orders_assigned,0));')
        rs = con.execute(carrier_query)
        con.commit()
        result=rs.fetchall()
        print(result)
        if(len(result)==0):
            return "No orders assigned"
        else:
            result_list=[]
            for item in result:
                result_list.append('{"carrier_id":'+str(item[0])+',"carrier_name":"'+str(item[1])+'","order_remaining":'+str(item[2])+'}')
            print(result_list)
            return str(result_list).replace("'","")

@app.route('/order/assign', methods = ['POST'])   
def mark_assign_order():
    order_id = request.json['order_id']
    carrier_id = request.json['carrier_id']
    engine=db_connect()
    with engine.connect() as con:
        
        quantity_query=text('SELECT status FROM orders where id='+str(order_id))
        rs = con.execute(quantity_query)
        result=rs.first()[0]
        
        if(result!=1):
            return "This order is marked as shipped or assigned to another carrier"
            
        else:
            quantity_query=text('SELECT quantity FROM order_detail where order_id='+str(order_id))
            rs = con.execute(quantity_query)
            result1=rs.first()[0]
            max_merch_query=text('SELECT max_merch_per_order FROM carrier where id='+str(carrier_id))
            rs1 = con.execute(max_merch_query)
            result2=rs1.first()[0]
            if(result1>result2):
                return "Can't assign this order to the carrier, no of merchandise is more than the carrier can carry"
            else:
                proceed_flag=1
                list_carrier=list_availiable_carrier()
                data = json.loads(list_carrier)
                print(data)
                if not any(dic["carrier_id"] == carrier_id for dic in data):
                    proceed_flag=0
                    return "This carrier cant carry any more orders"
                if(len(result)==0):
                    query=text('INSERT INTO carrier_availability (carrier_id,no_of_orders_assigned,order_assign_date)VALUES ('+str(carrier_id)+',1,NOW())')
                else:
                    query=text('UPDATE orders SET status=2, carrier_id='+str(carrier_id)+' WHERE id='+str(order_id))
                con.execute(update_query)
                update_query_2=text('UPDATE carrier_availability SET no_of_orders_assigned=no_of_orders_assigned+1 WHERE DATE(order_assign_date)=DATE(NOW()) AND carrier_id='+str(carrier_id))
                con.execute(update_query_2)
                con.commit()
                
                
                 
            return "SUCCESS"         

# driver function 
if __name__ == '__main__': 
  
    app.run(debug = True) 
