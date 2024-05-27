
# FLOW SHIPPING COMPANY

Project Requirements:
1- Get the list of available carriers.
2- Get the list of orders that are waiting to be shipped
3- Assign an available carrier to ship an unshipped order
4- Mark an order as shipped
5- Get the list of orders assigned to a given carrier

## DATABASE DIAGRAM
Acces database diagram at - https://dbdiagram.io/d/Order_Carrier-6651d2e1f84ecd1d221ed44b (works best in Google chrome)

![Order_Carrier(1)](https://github.com/smit-arora/astro/assets/170908724/9c5ce7a6-626c-49fa-9651-d4f9d4b3c2ec)

Tables and their utilization:

Table merchant - Base table for storing merchant data

Table merchandise - Base table for storing merchandise data

Table merchant_merchandise - Mapping table that maps each merchandise to the merchant table

Table orders - Table for tracking orders; contains merchant_id, status(1-Placed,2-Assigned,3-Shipped), carrier_id (if assigned), order created at, order shipped at

Table order_detail - Details of order, maps orders table to this table, contains merchandise id and quantity to be shipped

Table carrier - Base table for storing carrier Data - name, max orders a carrier can send per day, max merchandise per order, cost per order

Table carrier_availaibility - Check the carrier availability, contains carrier id and number of orders assigned per day. It will not contain any data for a carrier if no order is assigned to be shipped 



## Import Database- 
This branch is for working on the project using SqlAlchemy ORM.

To initialize the project, you have to first create the database, this file will simply create the database flow_shipping_orm

```mysql < initialize/flow_shipping.sql```

If you want to import the data then that can be done by 

```mysql < initialize/flow_shipping_data.sql```

Next Create DB user that will be accessing the database

```
CREATE USER 'flow_shipping'@'%' IDENTIFIED BY 'PAss123';
GRANT ALL PRIVILEGES ON flow_shipping_orm.* TO 'flow_shipping'@'%';
```



## Usage
After Starting the project, use following CURL commands to access


1- Get the list of available carriers.

```
curl --header "Content-Type: application/json" \
  --request GET \
  http://localhost:5000/carriers/availaible
```

2- Get the list of orders that are waiting to be shipped

```
curl --header "Content-Type: application/json" \
  --request GET \
  http://localhost:5000/orders/waitingshipping
```

3- Assign an available carrier to ship an unshipped order
```
curl --header "Content-Type: application/json" \
  --request POST \
  --data '{"order_id":2, "carrier_id":2}' \
  http://localhost:5000/order/assign
```

4- Mark an order as shipped
```
curl --header "Content-Type: application/json" \
  --request POST \
  --data '{"order_id":2, "shipped_date":"2024-05-26 01:08:16"}' \
  http://localhost:5000/orders/markshipped
```

5- Get the list of orders assigned to a given carrier
```
  curl --header "Content-Type: application/json" \
  --request GET \
  --data '{"carrier_id":1}' \
  http://localhost:5000/carriers/orderlist
```
