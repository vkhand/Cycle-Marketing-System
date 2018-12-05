import mysql.connector

con = mysql.connector.connect(user='root', password='vikash1234', host='localhost', database='cycledatabase')
c = con.cursor()
def create_table():

    c.execute('create table if not exists customer(user_id varchar(20), password varchar(30), name varchar(50), ph_no varchar(20), constraint pk_cus primary key(user_id))')
    c.execute('create table if not exists category(cat_id varchar(10), cat_name varchar(15),constraint pk_cat primary key(cat_id))')
    c.execute('create table if not exists stock(cycle_name varchar(50),cat_id varchar(10),cost_price integer, sell_price integer, cycle_image varchar(100),quantity integer, description text, constraint pk_stock primary key(cycle_name),constraint fk_stock foreign key(cat_id) references category(cat_id) on delete cascade)')
    c.execute('create table if not exists access(user_id varchar(20), cycle_name varchar(50), constraint pk_acc primary key(user_id,cycle_name), constraint fk1_acc foreign key(user_id) references customer(user_id) on delete cascade,constraint fk2_acc foreign key(cycle_name) references stock(cycle_name) on delete cascade)')
    c.execute('create table if not exists enquiry(enq_id varchar(100), user_id varchar(20), cycle_name varchar(50), cat_id varchar(10),enq_date date, constraint pk_enq primary key(enq_id,user_id,cycle_name,cat_id), constraint fk1_enq foreign key(user_id) references customer(user_id) on delete cascade,constraint fk2_enq foreign key(cycle_name) references stock(cycle_name) on delete cascade,constraint fk3_enq foreign key(cat_id) references category(cat_id) on delete cascade)')
    c.execute('create table if not exists suppliers(s_id varchar(20), s_name varchar(50),s_city varchar(30),ph_no varchar(20),email varchar(50), constraint pk_sup primary key(s_id))')
    c.execute('create table if not exists supplies(s_id varchar(20), cycle_name varchar(50), constraint pk_s primary key(s_id,cycle_name),constraint fk1_s foreign key(s_id) references suppliers(s_id) on delete cascade,constraint fk2_s foreign key(cycle_name) references stock(cycle_name) on delete cascade)')
    c.execute('create trigger calculate_sp before insert on stock for each row begin set new.sell_price = new.cost_price*1.18*1.2 ; end')
    c.execute('create trigger calculate_sp_update before update on stock for each row begin set new.sell_price = new.cost_price*1.18*1.2 ; end')
    c.execute('create  procedure `add_supplies`(in s_id varchar(20), in cycle_name varchar(50)) begin insert into supplies(s_id,cycle_name) values(s_id, cycle_name); end')
    c.execute('create  procedure `update_supplies`(in s_id varchar(20), in cycle_name varchar(50)) begin update supplies s set s.s_id = s_id where s.cycle_name = cycle_name; end')

create_table()
