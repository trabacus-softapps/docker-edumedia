-- 				Script for EDUMEDIA 
-- ************************************************************************************************************************************

DROP LANGUAGE IF EXISTS plpgsql cascade;
CREATE LANGUAGE plpgsql;


-- ************************************************************************************************************************************
--                                                       Function to genrate customer number
--*************************************************************************************************************************************

DROP FUNCTION if EXISTS "GenCust_Fun"();

CREATE OR REPLACE FUNCTION "GenCust_Fun"()
  RETURNS trigger AS
$BODY$DECLARE
   CUSTNum VARCHAR(30);
   
BEGIN
  IF tg_op = 'INSERT' THEN
  
     CUSTNum :='EDU';
 IF (SELECT count(ref) FROM res_partner 
	 WHERE ref like CUSTNum || '%'
	 GROUP BY id 
	 ORDER BY id desc limit 1) > 0 THEN
     
	     SELECT CUSTNum || trim(to_char(to_number(substr(ref,4,5),'99999') + 1,'00000')) into CUSTNum 
	     FROM res_partner 
	     WHERE ref like CUSTNum || '%'
	     ORDER BY to_number(substr(ref,4,5),'99999') desc limit 1;
     ELSE
	 CUSTNum := CUSTNum || '00001';
     END IF;	     
     
   
     UPDATE res_partner set ref = CUSTNum WHERE id = new.id;
     
  END IF;  
  RETURN new;
END
$BODY$
  LANGUAGE plpgsql VOLATILE
  COST 100;

-- **************************************************************************************************************************
--                                    Trigger for function GenCust_fun()
-- ***************************************************************************************************************************

DROP TRIGGER if exists "GenCust_Trg" ON res_partner;

CREATE TRIGGER "GenCust_Trg"
  AFTER INSERT
  ON res_partner
  FOR EACH ROW
  EXECUTE PROCEDURE "GenCust_Fun"();

 -- **************************************************************************************************************************
--                                    Delete standard purcahse order sequence
-- ***************************************************************************************************************************
DELETE FROM ir_sequence  WHERE name = 'Purchase Order';

  -- ************************************************************************************************************************************
--                                                       Function to genrate Purchase Order number
--*************************************************************************************************************************************

      CREATE OR REPLACE FUNCTION "GenPONum_Fun"()
  RETURNS trigger AS
$BODY$DECLARE
   PONum VARCHAR(30); 
   CY integer;
   CM Integer;  
   FinYr VARCHAR(30);    
   
BEGIN
  IF tg_op = 'INSERT' THEN
  
     PONum :='PO';
     SELECT to_char(now(),'YY') into CY;  	
     SELECT to_char(now(),'MM') into CM;   
     
     IF CM > 3 THEN
	FinYr :=  '/' || CY || '-' || (CY + 1); 
     ELSE
	FinYr := '/' || (CY - 1) || '-' || CY; 
     END IF;   

     IF (SELECT count(name) FROM purchase_order 
	 WHERE name like PONum || '%' || FinYr
	 GROUP BY id
	 ORDER BY id desc limit 1) > 0 THEN
     
	     SELECT PONum || trim(to_char(to_number(substr(name,3,5),'99999') + 1,'00000')) || FinYr into PONum 
	     FROM purchase_order 
	     WHERE name like PONum || '%' || FinYr
	     ORDER BY to_number(substr(name,3,5),'99999') desc limit 1 ;
     ELSE
	 PONum := PONum || '00001' || FinYr;
     END IF;	     
     
   
     UPDATE purchase_order set name = PONum WHERE id = new.id;
     
  END IF;  
  RETURN new;
END
$BODY$
  LANGUAGE 'plpgsql' VOLATILE
  COST 100;
  
-- **************************************************************************************************************************
--                                    Trigger for function GenPONUM_fun()
-- ***************************************************************************************************************************
DROP TRIGGER if exists "GenPONum_Trg" ON purchase_order;


CREATE TRIGGER "GenPONum_Trg"
  AFTER INSERT
  ON purchase_order
  FOR EACH ROW
  EXECUTE PROCEDURE "GenPONum_Fun"();

-- ************************************************************************************************************************************
--                                                       Function to genrate Subscription number
--*************************************************************************************************************************************

CREATE OR REPLACE FUNCTION "GenSub_Fun"()
RETURNS trigger AS
$BODY$DECLARE
   SubNum VARCHAR(30);    
   
BEGIN
  IF tg_op = 'INSERT' THEN
  
     SubNum :='MEN/';    

     IF (SELECT count(sub_no) FROM ed_subscription 
	 WHERE sub_no like SubNum || '%'
	 GROUP BY id
	 ORDER BY id desc limit 1) > 0 THEN
     
	     SELECT SubNum || trim(to_char(to_number(substr(sub_no,5,5),'99999') + 1,'00000')) into SubNum 
	     FROM ed_subscription 
	     WHERE sub_no like SubNum || '%'
	     ORDER BY to_number(substr(sub_no,5,5),'99999') desc limit 1 ;
     ELSE
	 SubNum := SubNum || '00001';
     END IF;	     
     
   
     UPDATE ed_subscription set sub_no = SubNum WHERE id = new.id;
     
  END IF;  
  RETURN new;
END
$BODY$
  LANGUAGE 'plpgsql' VOLATILE
  COST 100;
  
-- **************************************************************************************************************************
--                                    Trigger for function GenSub_Fun()
-- ***************************************************************************************************************************
DROP TRIGGER if exists "GenSubNum_Trg" ON ed_subscription;


CREATE TRIGGER "GenSubNum_Trg"
  AFTER INSERT
  ON ed_subscription
  FOR EACH ROW
  EXECUTE PROCEDURE "GenSub_Fun"();

-- ************************************************************************************************************************************
--                                                       VIEWS: Coordinator details
-- ************************************************************************************************************************************* 
DROP VIEW IF EXISTS vw_res_partner_address; 
CREATE OR REPLACE VIEW vw_res_partner_address AS
select pa.id
      , pa.name
      , pa.mobile
      , pa.email
      , pa.ed_desig_id
      , 3 as sale_id
from res_partner_address pa
where pa.id in (select address_id from address_sale_rel where sale_id = 3);

-- ************************************************************************************************************************************
--                                                       VIEWS: Partner to print labels
-- ************************************************************************************************************************************* 
DROP VIEW IF EXISTS vw_res_partner; 

CREATE OR REPLACE VIEW vw_res_partner AS
select r.id,
       r.id as partner_id,
       1 as stock_id
from res_partner r 
where r.id in (select partner_id 
	from part_comp_rel 
	where comp_id = 1) 
order by r.id;

-- ************************************************************************************************************************************
--                                                       VIEWS: Subscriber to print labels
-- ************************************************************************************************************************************* 
DROP VIEW IF EXISTS vw_ed_subscription; 

CREATE OR REPLACE VIEW vw_ed_subscription AS
select s.id,
       s.id as subscrib_id,
       1 as monthly_id
from ed_subscription s 
where s.id in (select subs_id 
	from monthly_subs_rel 
	where monthly_id = 1) 
order by s.id;

-- ************************************************************************************************************************************
--                                                       VIEWS: Advertisers to print labels
-- ************************************************************************************************************************************* 
DROP VIEW IF EXISTS vw_ed_advertisers; 

CREATE OR REPLACE VIEW vw_ed_advertisers AS
select ad.id,
       ad.id as advertiser_id,
       1 as monthly_id
from ed_advertisers_details ad 
where ad.id in (select adver_id 
	from monthly_adver_rel 
	where monthly_id = 1) 
order by ad.id;

-- ************************************************************************************************************************************
--                                                       VIEWS: Director to print labels
-- ************************************************************************************************************************************* 
DROP VIEW IF EXISTS vw_ed_director; 

CREATE OR REPLACE VIEW vw_ed_director AS
select dd.id,
       dd.id as director_id,
       1 as monthly_id
from ed_director_details dd 
where dd.id in (select director_id 
	from monthly_direc_rel 
	where monthly_id = 1) 
order by dd.id;


-- ************************************************************************************************************************************
--                                                       VIEWS: CLass details
-- *************************************************************************************************************************************
CREATE OR REPLACE VIEW vw_ed_class_details AS
                            select cl.id
                                  , cl.ed_class    
                                  , cl.ed_sec
                                  , cl.ed_students
                                  , cl.ed_boys
                                  , case when cl.ed_class = 6 then sum(cl.ed_girls)
						    else 0 end as girls
			          , case when cl.ed_class = 7 then sum(cl.ed_boys)
						    else 0 end as boys
                                  , cl.ed_girls
                                  , 53  as sale_id
                            from ed_class_details cl
                            where cl.id in (select cls_id from class_sale_rel 
                                        where sale_id = 53)
                             group by cl.id,cl.ed_class ,cl.ed_sec, cl.ed_students, cl.ed_boys, cl.ed_girls;

-- **************************************************************************************************************************
--                                    Views for mailing list report
-- ***************************************************************************************************************************
DROP VIEW IF EXISTS ed_vw_mailing_list;

CREATE OR REPLACE VIEW ed_vw_mailing_list AS
  SELECT 1 as id
      ,  1 as category_id
      ,  1 as country_id
      ,  1 as state_id
      ,  1 as ed_city_id;


-- ************************************************************************************************************************************
--                                                       Function to genrate mailing list
-- *************************************************************************************************************************************

drop type if exists ed_mail_list cascade;

create type ed_mail_list as (id int,  
	  partner_id int,
	  address_id int,
	  category text);
	  

CREATE OR REPLACE FUNCTION ed_mail_func(categ integer, country integer, state integer, city integer)
  RETURNS SETOF ed_mail_list AS
$BODY$
DECLARE
   r ed_mail_list%rowtype;
   sqlstr text;
   tmpstr text;
   s2 varchar(100):=''; 
   

BEGIN
    
    DROP SEQUENCE if exists mail_seq;
    CREATE TEMP sequence mail_seq;
    
    DROP SEQUENCE if exists tmp_seq;
    CREATE TEMP sequence tmp_seq;
    

    DROP TABLE if exists tmp_mail_list;
    CREATE TEMP TABLE tmp_mail_list
	( id int,  
	  partner_id int,
	  address_id int,
	  category text
	  
	 )
     ON COMMIT DROP;

    DROP TABLE if exists tmp_table;
    CREATE TEMP TABLE tmp_table
	( id int,  
	  partner_id int,
	  address_id int,
	  category text
	  
	 )
     ON COMMIT DROP;

   if categ > 0 then
        select ' AND car.category_id =' || categ into s2 ; 
    end if;  

    if country > 0 then
       select  s2 ||' AND a.country_id = ' ||country into s2;
    end if;

    if state > 0 then
       select s2 || ' AND a.state_id =' || state into s2;
    end if;
    
    if city > 0 then
       select s2 || ' AND a.ed_city_id ='|| city into s2;
    end if; 

   
        
    
   sqlstr := 'INSERT INTO tmp_mail_list(id, partner_id, address_id, category)
    ( SELECT nextval(''mail_seq'') as id
	     , x.partner_id 
	     , x.address_id 
	     , x.category
	        
	FROM
		(       select  a.id 
		      , p.id as partner_id
		      , a.id as address_id 
		      , ca.name as category
		from res_partner p 
		inner join res_partner_category_rel car on car.partner_id=p.id
		inner join res_partner_category ca on ca.id = car.category_id
		inner join res_partner_address a on a.partner_id = p.id
		WHERE a.ed_desig_id = (select id from ed_designation where lower(name) = ''principal'')
		'|| s2 ||' 
		
		

	)x 
    )';

    execute sqlstr;
   
    INSERT INTO tmp_table(id, partner_id, address_id, category)
    (   SELECT nextval('tmp_seq') as id
              , data.partner_id
              , data.address_id
              , data.category
        FROM
        (  select distinct a.partner_id
		 , a.address_id
		 , array_to_string(array(select distinct category from tmp_mail_list where partner_id = a.partner_id ),'/') as category
	    from tmp_mail_list a
	)data
    );
    
    for r in SELECT * FROM tmp_table loop
	return next r;          
    end loop;
    
    return;  
END 

$BODY$
  LANGUAGE 'plpgsql' VOLATILE
  COST 100;



-- **************************************************************************************************************************
--                                    Views to fetch mailing list lines
--***************************************************************************************************************************
DROP VIEW IF EXISTS ed_vw_mailing_list_ln;

CREATE OR REPLACE VIEW ed_vw_mailing_list_ln AS                                   
select  q.id 
      , q.partner_id  
      , q.address_id 
      , q.category 
      , 1 as main 
from (select * from ed_mail_func(0,101,53,0))q;

-- **************************************************************************************************************************
--                                    Views to fetch training list 
-- ***************************************************************************************************************************
DROP VIEW IF EXISTS ed_vw_training_list;
CREATE OR REPLACE VIEW ed_vw_training_list AS
  SELECT 1 as id
      ,  1 as category_id
      ,  '2012-01-01' as sch_date
      ,  1 as user_id
      ,  'no' as ed_complt;

drop type if exists ed_training_list cascade;
create type ed_training_list as (id int,  
	  sale_id int,
	  partner_id int,
	  tname varchar(300),
	  schdate date,
	  userid int,
	  ed_stat varchar(300),
	  ed_complt varchar(16),
	  complt_on date,	  
	  category text);
	  
	  
CREATE OR REPLACE FUNCTION ed_training_func(categ integer, schdate varchar(50), userid integer, cmplt varchar(50))
  RETURNS SETOF ed_training_list AS
$BODY$
DECLARE
   r ed_training_list%rowtype;
   sqlstr text;
   tmpstr text;
   s1 varchar(100):='';
   s2 varchar(100):=''; 
   

BEGIN
    
    DROP SEQUENCE if exists train_seq;
    CREATE TEMP sequence train_seq;
    
    DROP SEQUENCE if exists tmp_seq;
    CREATE TEMP sequence tmp_seq;
    

    DROP TABLE if exists tmp_training_list;
    CREATE TEMP TABLE tmp_training_list
	( id int,  
	  sale_id int,
	  partner_id int,
          tname varchar(300),
          sch_date date,
	  user_id int,
	  ed_stat varchar(300),
	  ed_complt varchar(16),
	  complt_on date,	  
	  category text)
	  
	 
     ON COMMIT DROP;

    DROP TABLE if exists tmp_table;
    CREATE TEMP TABLE tmp_table
	( id int,  
	  sale_id int,
	  partner_id int,
	  tname varchar(300),
	  sch_date date,
	  user_id int,
	  ed_stat varchar(300),
	  ed_complt varchar(16),	  
	  complt_on date,
	  category text)
	  
     ON COMMIT DROP;

   if categ > 0 then
        select ' AND car.category_id =' || categ into s2 ; 
    end if;  

    if length(schdate) > 1 then
      
       select  s2 ||' AND t.sch_date =  '''|| to_date(schdate,'yyyy-mm-dd') ||'''' into s2;
    end if;

    if userid > 0 then
       select s2 || ' AND t.user_id =' || userid into s2;
    end if;
    
    if length(cmplt) > 1 then
       select s2 || ' AND t.ed_complt ='''|| cmplt ||''''into s2;
    end if; 

    if length(s2) > 1 then 
       select 'where '|| substr(s2,5,length(s2)) into s1;
    end if; 
        
    
   sqlstr := 'INSERT INTO tmp_training_list(id, sale_id,partner_id, tname, sch_date, user_id, ed_stat, ed_complt,complt_on, category)
    ( SELECT nextval(''train_seq'') as id
	     , x.sale_id
	     , x.partner_id 
	     , x.tname 
	     , x.sch_date
	     , x.user_id
	     , x.ed_stat
	     , x.ed_complt
	     , x.complt_on
	     , x.category	        
	FROM
		(       select   t.id
			       , so.id as sale_id
			       , p.id as partner_id
			       , t.name as tname
			       , t.sch_date 
			       , t.user_id 
			       , t.ed_stat
			       , t.ed_complt
			       , t.complt_date as complt_on
			       , ca.name as category
			       , 1 as main 
				from sale_order so
				inner join ed_training_grid t on t.sale_id = so.id
				inner join res_partner p on p.id = so.partner_id
				inner join res_partner_category_rel car on car.partner_id = so.partner_id 
				inner join res_partner_category ca on ca.id = car.category_id 
				'|| s1 ||' 
		
		

	)x 
    )';

    execute sqlstr;
   
    INSERT INTO tmp_table(id, sale_id, partner_id, tname, sch_date, user_id, ed_stat, ed_complt,complt_on,category)
    ( SELECT nextval('train_seq') as id
	     , data.sale_id
	     , data.partner_id 
	     , data.tname 
	     , data.sch_date
	     , data.user_id
	     , data.ed_stat
	     , data.ed_complt
	     , data.complt_on
	     , data.category
        FROM
        (  select distinct a.sale_id
                 , a.partner_id
		 , a.tname 
		 , a.sch_date
		 , a.user_id 
		 , a.ed_stat
		 , a.ed_complt
		 , a.complt_on		
		 , array_to_string(array(select distinct category from tmp_training_list where sale_id = a.sale_id ),'/') as category
	    from tmp_training_list a
	)data
    );
    
    for r in SELECT * FROM tmp_table loop
	return next r;          
    end loop;
    
    return;  
END 

$BODY$
  LANGUAGE 'plpgsql' VOLATILE
  COST 100;      

-- **************************************************************************************************************************
--                                    Views to fetch training list 
--***************************************************************************************************************************
DROP VIEW IF EXISTS ed_vw_training_list_ln;

CREATE OR REPLACE VIEW ed_vw_training_list_ln AS                                   
select   t.id
   , t.sale_id
   , t.partner_id
   , t.tname as name
   , t.schdate as sch_date
   , t.userid as user_id 
   , t.ed_stat
   , t.ed_complt
   , t.complt_on
   , t.category
   , 1 as main 
from 
( select * from ed_training_func(1,'2012-01-01',1 ,'no'))t; 

--***************************************************************************************************************************
--                                    Views to Payment List
--***************************************************************************************************************************
DROP VIEW IF EXISTS ed_vw_payment_list;

CREATE OR REPLACE VIEW ed_vw_payment_list AS
SELECT 1 as id
      , 1 as category_id
      , '2012-03-14' AS nxt_payment_date ;

drop type if exists ed_payment_list cascade;
create type ed_payment_list as (id int,  
	  sale_id int,
	  partner_id int,
	  pay_amt float,
	  category text);

	  
CREATE OR REPLACE FUNCTION ed_payment_func(categ integer,nxtdate varchar(50))
  RETURNS SETOF ed_payment_list AS
$BODY$
DECLARE
   r ed_payment_list%rowtype;
   sqlstr text;
   tmpstr text;
   s1 varchar(100):='';
  
   

BEGIN
    
    DROP SEQUENCE if exists pay_seq;
    CREATE TEMP sequence pay_seq;
    
    DROP SEQUENCE if exists tmp_seq;
    CREATE TEMP sequence tmp_seq;
    

    DROP TABLE if exists tmp_payment_list;
    CREATE TEMP TABLE tmp_payment_list
	( id int,  
	  sale_id int,
	  partner_id int,
	  pay_amt float,
	  category text)
	  
	 
     ON COMMIT DROP;

    DROP TABLE if exists tmp_table;
    CREATE TEMP TABLE tmp_table
	( id int,  
	  sale_id int,
	  partner_id int,
	  pay_amt float,
	  category text)
	  
     ON COMMIT DROP;

   if categ > 0 then
        select ' AND car.category_id =' || categ into s1 ; 
    end if;  

   if length(nxtdate) > 1 then
      
       select  s1 ||' AND so.nxt_payment_date =  '''|| to_date(nxtdate,'yyyy-mm-dd') ||'''' into s1;
    end if;
    
   sqlstr := 'INSERT INTO tmp_payment_list(id, sale_id,partner_id, pay_amt,category)
    ( SELECT nextval(''pay_seq'') as id
	     , x.sale_id
	     , x.partner_id 
	     , x.payamt
	     , x.category	        
	FROM
		(       select   so.id as sale_id
			       , p.id as partner_id
			       , sum(pa.ed_amt) as payamt
			       , ca.name as category 
			from sale_order so
			inner join ed_payment pa on pa.sale_id = so.id
			inner join res_partner_category_rel car on car.partner_id=so.partner_id
			inner join res_partner_category ca on ca.id = car.category_id
			inner join res_partner p on p.id = so.partner_id
			where so.amount_total  > (SELECT sum(pa.ed_amt) from ed_payment pa where pa.sale_id = so.id limit 1)
		        '|| s1 ||' 
			group by so.id,p.id,category 
		)x 
    )';

    execute sqlstr;
   
    INSERT INTO tmp_table(id, sale_id,partner_id,  pay_amt,  category)
    ( SELECT nextval('tmp_seq') as id
	     , data.sale_id
	     , data.partner_id 
	     , data.pay_amt
	     , data.category
        FROM
        (  select distinct a.sale_id
                 , a.partner_id
		 , a.pay_amt
	         , array_to_string(array(select distinct category from tmp_payment_list where sale_id = a.sale_id ),'/') as category
	    from tmp_payment_list a
	)data
    );
    
    for r in SELECT * FROM tmp_table loop
	return next r;          
    end loop;
    
    return;  
END 

$BODY$
  LANGUAGE 'plpgsql' VOLATILE
  COST 100;



--***************************************************************************************************************************
--                                    Views to Payment List lines
--***************************************************************************************************************************
DROP VIEW IF EXISTS ed_vw_payment_list_ln;
            
CREATE OR REPLACE VIEW ed_vw_payment_list_ln AS                                   
select  q.id 
      , q.sale_id 
      , q.partner_id
      , q.pay_amt as ed_amt
      , q.category as category
      , 1 as main 
from (select * from ed_payment_func(1,'2012-03-14'))q;

--***************************************************************************************************************************
--                                    views to create class 
--***************************************************************************************************************************

CREATE OR REPLACE VIEW ed_vw_module AS 
 SELECT a.id
      , a.id as name
 FROM
 (	select unnest(array[1, 2, 3, 4, 5, 6, 7, 8]) as id
 )a;

-- **************************************************************************************************************************
--                                    Views to fetch sessions list 
-- ***************************************************************************************************************************

DROP VIEW IF EXISTS ed_vw_sessions_list;
CREATE OR REPLACE VIEW ed_vw_sessions_list AS
                                SELECT 1 as id
                                      ,1 as category_id;
                                      
drop type if exists ed_session_list cascade;
create type ed_session_list as (id int,
          ed_school varchar(200),  
	  sale_id int,
	  module1 int,
	  module2 int,
	  module3 int,
	  module4 int,
	  module5 int,
	  module6 int,
	  module7 int,
	  module8 int,
	  parents int,
	  teachers int,
	  category text);
	 


	  
CREATE OR REPLACE FUNCTION ed_session_func(categ integer,clslist integer[])
  RETURNS SETOF ed_session_list AS
$BODY$
DECLARE
   r ed_session_list%rowtype;
   sqlstr text;
   tmpstr text;
   s1 varchar(100):='';
   s2 varchar(500):='';
   x record;
   

BEGIN
    
    DROP SEQUENCE if exists ses_seq;
    CREATE TEMP sequence ses_seq;
    
    DROP SEQUENCE if exists tmp_seq;
    CREATE TEMP sequence tmp_seq;
    

    DROP TABLE if exists tmp_session_list;
    CREATE TEMP TABLE tmp_session_list
	( id int,
          ed_school varchar(200),  
	  sale_id int,
	  module1 int,
	  module2 int,
	  module3 int,
	  module4 int,
	  module5 int,
	  module6 int,
	  module7 int,
	  module8 int,
	  parents int,
	  teachers int,
	  category text)
	  
	 
     ON COMMIT DROP;

    DROP TABLE if exists tmp_table;
    CREATE TEMP TABLE tmp_table
	( id int,
          ed_school varchar(200),  
	  sale_id int,
	  module1 int,
	  module2 int,
	  module3 int,
	  module4 int,
	  module5 int,
	  module6 int,
	  module7 int,
	  module8 int,
	  parents int,
	  teachers int,
	  category text)
	  
     ON COMMIT DROP;

   if categ > 0 then
        select ' AND rcr.category_id =' || categ into s1 ; 
    end if;


    for x in (select * from (select unnest(clslist) as cl)a)  loop
       select ' or q.module'||x.cl||'> 0'||s2 into s2; 
     end loop;

     if length(s2) > 1 then 
       select 'having '|| substr(s2,5,length(s2)) into s2;
    end if;       
     
  
   sqlstr := 'INSERT INTO tmp_session_list(id, ed_school,sale_id,module1,module2,module3,module4,module5,module6,module7,module8,parents,teachers,category)
    ( select nextval(''ses_seq'') as id
            ,x.school
            ,x.sale_id
            ,x.module1
            ,x.module2
            ,x.module3
            ,x.module4
            ,x.module5
            ,x.module6
            ,x.module7
            ,x.module8
            ,y.parent_sesns
            ,y.teach_sesns
            ,x.name
	 from
	 (
		  select q.school
		       , q.sale_id  
		       , q.module1
		       , q.module2
		       , q.module3
		       , q.module4
		       , q.module5
		       , q.module6
		       , q.module7
		       , q.module8
		       , q.name
		  from
		  (	      select a.school
				     , a.sale_id  
				     , sum(module1) as module1
				     , sum(module2) as module2
				     , sum(module3) as module3
				     , sum(module4) as module4
				     , sum(module5) as module5
				     , sum(module6) as module6
				     , sum(module7) as module7
				     , sum(module8) as module8
				     , a.name
				from
				(
					select s.ed_school as school
					     , s.sale_id 
					     , rc.name 
					     , case when sc.ed_class = 1 then sum(sn.name)
						    else null end as module1

					     , case when sc.ed_class = 2 then sum(sn.name)
						    else null end as module2

					     , case when sc.ed_class = 3 then sum(sn.name)
						    else null end as module3

					     , case when sc.ed_class = 4 then sum(sn.name)
						    else null end as module4
						    
					     , case when sc.ed_class = 5 then sum(sn.name)
						    else null end as module5

					     , case when sc.ed_class = 6 then sum(sn.name)
						    else null end as module6

					     , case when sc.ed_class = 7 then sum(sn.name)
						    else null end as module7

					     , case when sc.ed_class = 8 then sum(sn.name)
						    else null end as module8 
					from ed_sessions s
					inner join ed_class_sessions sc on sc.sesion_id = s.id
					inner join ed_type_session st on st.id = sc.type
					inner join no_of_sessions sn on sn.id = sc.ed_no_seion
					inner join sale_order so on so.id = s.sale_id
					inner join res_partner_category_rel rcr on rcr.partner_id = so.partner_id
					inner join res_partner_category rc on rc.id=rcr.category_id
					where st.name = ''MODULE'' '||s1||'
					group by sale_id, s.ed_school, sc.ed_class,rc.name
				)a	
				group by a.school, a.sale_id,a.name
					
			)q
			group by q.school,q.sale_id,q.name,q.module1,q.module2,q.module3,q.module4,q.module5,q.module6,q.module7,q.module8
			'||s2||'
		)x
		LEFT OUTER JOIN 
		(	
				select p.sale_id
				      , sum(parent_ses) as parent_sesns
				      , sum(teach_ses) as teach_sesns
				from
				(	select s.ed_school as school
					     , s.sale_id 
					     , case when st.name = ''TEACHERS SESSION'' then sum(sn.name)
						    else null end as teach_ses
					     , case when st.name = ''PARENTS SESSION'' then sum(sn.name)
						    else null end as parent_ses
					from ed_sessions s
					inner join ed_class_sessions sc on sc.sesion_id = s.id
					inner join ed_type_session st on st.id = sc.type
					inner join no_of_sessions sn on sn.id = sc.ed_no_seion
					where st.name in (''TEACHERS SESSION'', ''PARENTS SESSION'') 
					group by school, sale_id, ed_so, st.name
				)p
				group by p.sale_id
		)y on x.sale_id = y.sale_id)';

    execute sqlstr;

    INSERT INTO tmp_table(id, ed_school,sale_id,module1,module2,module3,module4,module5,module6,module7,module8,parents,teachers,category)
    ( SELECT nextval('tmp_seq') as id
	     , data.ed_school
	     , data.sale_id
	     , data.module1
	     , data.module2
	     , data.module3
	     , data.module4
	     , data.module5
	     , data.module6
	     , data.module7
	     , data.module8
	     , data.parents
	     , data.teachers
	     , data.category
	FROM
	(  select distinct a.ed_school
		     , a.sale_id
		     , a.module1
		     , a.module2
		     , a.module3
		     , a.module4
		     , a.module5
		     , a.module6
		     , a.module7
		     , a.module8
		     , a.parents
		     , a.teachers			     	
		     , array_to_string(array(select distinct category from tmp_session_list where sale_id = a.sale_id ),'/') as category
	    from tmp_session_list a
	)data
    ); 
		    
    for r in SELECT * FROM tmp_table loop
	return next r;          
    end loop;
    
    
    return;  
END 

$BODY$
  LANGUAGE plpgsql VOLATILE
  COST 100;
  
-- **************************************************************************************************************************
--                                    Views to fetch sessions list lines
-- ***************************************************************************************************************************
DROP VIEW IF EXISTS ed_vw_sessions_list_ln;

CREATE OR REPLACE VIEW ed_vw_sessions_list_ln AS                                   
                                select  q.id
                                      , q.ed_school
                                      , q.sale_id 
                                      , q.module1
                                      , q.module2
                                      , q.module3
                                      , q.module4
                                      , q.module5
                                      , q.module6
                                      , q.module7
                                      , q.module8
                                      , q.parents
                                      , q.teachers
                                      , q.category
                                      , 1 as main 
                                from (select * from ed_session_func(1, array[1,2]))q;

-- **************************************************************************************************************************
--                                    Views to fetch Time Table List
-- ***************************************************************************************************************************

DROP VIEW IF EXISTS ed_vw_time_table_list;

CREATE OR REPLACE VIEW ed_vw_time_table_list AS  
                       select  1    as id
                             , 1    as account_id
                             , 'm1' as name
                             , 1 as city_id
                             ,'activity' as ed_type;

-- **************************************************************************************************************************
--                                    Views to fetch Time Table List Lines
-- ***************************************************************************************************************************

DROP VIEW IF EXISTS ed_vw_time_table_list_ln;

CREATE OR REPLACE VIEW ed_vw_time_table_list_ln AS                                      
                                     select tl.id as id
                                           ,t.id as table_id
                                           ,tl.id as table_ln_id
                                           ,am.id as month_id
                                           ,1 as main
                                     from time_table t 
                                     inner join account_fiscalyear a on t.account_id = a.id 
                                     inner join ed_auto_month am on am.table_id = t.id 
                                     inner join time_table_lines tl on tl.month_id = am.id
                                     where tl.ed_type ='activity' and t.account_id = 3 and t.city_id = 210 and am.name = 'm1'
                                     order by am.name,tl.day_id ASC ;   

-- **************************************************************************************************************************
--                                    Views to fetch Activity Session List
-- ***************************************************************************************************************************
drop VIEW IF EXISTS ed_vw_monthly_sessions;

CREATE OR REPLACE VIEW ed_vw_monthly_sessions AS
		       SELECT   1 as id
		              , 2 as partner_id
		              ,'02-01-2012' AS date1
		              ,'04-14-2012' as date2
			      ,'activity' AS ed_type;

-- **************************************************************************************************************************
--                                    Views to fetch Activity Session List Lines
-- ***************************************************************************************************************************
drop VIEW IF EXISTS ed_vw_monthly_sessions_ln;

CREATE OR REPLACE VIEW ed_vw_monthly_sessions_ln AS 
 SELECT act.id
      , act.id AS session_id
      , array_to_string(ARRAY( SELECT DISTINCT emu.name 
			       FROM ed_activity_session eas 
			       JOIN method_sessions_rel ms ON ms.method_id = eas.id
			       JOIN ed_method_used emu ON emu.id = ms.session_id
			       WHERE eas.id = act.id), ','::text) AS other_actv
      ,(select name from res_partner_address where partner_id = 11492 and type = 'default') as cont_name
      ,(select id from ed_sponsors 
	where ed_skills = 'activity' 
	and scity_id = (select ed_city_id 
			from res_partner_address 
			where partner_id = 1273 order by id limit 1)) as sponser_id  
      , 1 AS main
 FROM ed_activity_session act	
 WHERE act.ed_type::text = 'akshaya'::text 
 AND act.partner_id = 11492 
 AND act.ed_date >= '2012-01-23'::date AND act.ed_date <= '2012-11-23'::date
 ORDER BY act.ed_date asc;   
-- **************************************************************************************************************************
--                                    Views to fetch Topics List
-- ***************************************************************************************************************************
drop VIEW IF EXISTS ed_vw_topic_list;
CREATE OR REPLACE  VIEW ed_vw_topic_list AS
       SELECT   1 as id
	      ,'2011-01-01' AS start_date
	      ,'2012-04-31' as end_date;

drop type if exists ed_topic_list cascade;
create type ed_topic_list as (id int,
          tot_sessions int,
          tot_sessions1 int,
          school_id int,
	  ed_class int,
	  status varchar(50),
	  topic text
	  );

CREATE OR REPLACE FUNCTION func_topic(start_dt date, end_dt date, classlst integer[])
  RETURNS SETOF ed_topic_list AS
$BODY$
DECLARE
   r ed_topic_list%rowtype;
   start_date timestamp;
   end_date timestamp; 
   rec record; 
   i record; 
   sqlstr text;
   strn text = E', ';

BEGIN

    start_date := to_char((start_dt || ' 00:00:00')::timestamp, 'yyyy-mm-dd hh24:mi:ss');    
    end_date := to_char((end_dt   || ' 23:59:59')::timestamp, 'yyyy-mm-dd hh24:mi:ss');      
         
    DROP SEQUENCE if exists topic_seq;
    CREATE TEMP sequence topic_seq; 
    
    DROP TABLE if exists tmp_topic;
    CREATE TEMP TABLE tmp_topic
	( id int,  
	  tot_sessions int,
	  tot_sessions1 int,
          school_id int,
	  ed_class int,
	  status varchar(50),
	  topic text
	)
     ON COMMIT DROP;
    
    DROP TABLE if exists tmp_session;
    CREATE TEMP TABLE tmp_session
	( id int,  
	  partner_id int,
	  ed_class int,
	  ed_date date,
	  content_id int,
          topic_id int,
	  sess_count int, 
	  status varchar(50)
	)
     ON COMMIT DROP;

     insert into tmp_session(id, partner_id, ed_class, ed_date, content_id, topic_id, sess_count, status)
     (   select ss.id
	      , ss.partner_id
	      , ss.ed_class
	      , ss.ed_date
	      , ss.content_id
	      , ss.topic_id
	      , ss.sess_count
	      , lower(es.name) as status
	 from ed_activity_session ss
	 inner join ed_status es on es.id = ss.status_id
	 inner join ed_topic et on et.id = ss.topic_id
	 where lower(es.name) = 'completed'
	 and ss.ed_type = 'akshaya' and ss.sess_count > 0
	 and ss.ed_date between start_date and end_date  
	 and ss.ed_class in (select unnest(classlst)) 
     );
	      
    FOR i in (select unnest(classlst) as cls) LOOP
	insert into tmp_topic(id, school_id, ed_class, status)
	(   select nextval('topic_seq') as id
	        , a.partner_id as school_id 
	        , i.cls as ed_class
	        , b.status
	    from 
	    (   select distinct ts.partner_id
	        from tmp_session ts 
	        where ts.ed_class = i.cls
	    )a 
	    cross join 
	    (   select unnest(array['completed','in progress']) as status
	    )b 
	);
    END LOOP;
     

      -- To update Completed Records
    for rec in (select * from tmp_topic t where t.status = 'completed' order by t.id) loop
	update tmp_topic
	       set topic = (select array_to_string
				  (array( select distinct et.name 
					  from tmp_session ts
					  inner join ed_topic et on et.id = ts.topic_id
					  where ts.partner_id = rec.school_id 
					  and ts.ed_class = rec.ed_class
					  and ts.status = 'completed'
					  
			  ),strn)) 

	 ,tot_sessions = (  select sum(ts.sess_count)
			    from tmp_session ts
			    where ts.partner_id = rec.school_id 
			    and ts.ed_class in (5,6,7)
			    and ts.status = 'completed'
			  ) 
	 ,tot_sessions1 = (  select sum(ts.sess_count)
			    from tmp_session ts
			    where ts.partner_id = rec.school_id 
			    and ts.ed_class in (8,9,10)
			    and ts.status = 'completed'
			  ) 
			   
	where id = rec.id; 
    end loop; 
 
        
      -- To update Other Records
    for rec in (select * from tmp_topic t where t.status = 'in progress' order by t.id) loop
	update tmp_topic 
	       set topic = ( select case when a.nxt_topic is null 
				    then (select t.name from ed_topic t
					  inner join ed_content c on c.id = t.content_id
					  where c.seq > a.content_seq 
					  and t.ed_class = a.ed_class 
					  order by c.seq, t.seq limit 1) 
				    else
					a.nxt_topic end
			     from
			     (	    select c.seq as content_seq
					  , ts.ed_class
					  , (select name from ed_topic t where t.seq > et.seq 
						and t.content_id = et.content_id and t.ed_class = ts.ed_class 
						order by content_id, t.seq limit 1) as nxt_topic
				    from tmp_session ts  
				    inner join ed_topic et on et.id = ts.topic_id
				    inner join ed_content c on c.id = et.content_id 
				    where ts.partner_id = rec.school_id 
				    and ts.ed_class = rec.ed_class
				    and ts.status = 'completed' 
				    order by ts.ed_date desc limit 1 
			    ) a
			   )  
			   
	 ,tot_sessions = (  select sum(ts.sess_count)
			    from tmp_session ts
			    where ts.partner_id = rec.school_id 
			    and ts.ed_class in (5,6,7)
			    and ts.status = 'completed'
			  ) 
	 ,tot_sessions1 = (  select sum(ts.sess_count)
			    from tmp_session ts
			    where ts.partner_id = rec.school_id 
			    and ts.ed_class in (8,9,10)
			    and ts.status = 'completed'
			  ) 
			   
	where id = rec.id; 
    end loop; 

        
    for r in SELECT * FROM tmp_topic loop
	return next r;          
    end loop;
    
    return;  
END 

$BODY$
  LANGUAGE 'plpgsql' VOLATILE
  COST 100;

-- **************************************************************************************************************************
--                                    Views to fetch Topics List Lines
-- ***************************************************************************************************************************  
drop VIEW IF EXISTS ed_vw_topic_list_ln;
CREATE OR REPLACE VIEW ed_vw_topic_list_ln AS
 SELECT q.id
       ,q.tot_sessions
       ,q.tot_sessions1
       ,q.school_id as partner_id
       ,q.ed_class
       ,q.status
       ,q.topic
       ,1 as main
 FROM (select * from func_topic('2011-01-01', '2012-01-01',array[5]) order by ed_class ASC )q;   

-- **************************************************************************************************************************
--                                    views to fetch career list
-- ***************************************************************************************************************************  

drop VIEW IF EXISTS vw_ed_career;
CREATE OR REPLACE VIEW vw_ed_career AS
                                select 1 as id
                                      ,18 as department_id;

drop type if exists ed_career_list cascade;
create type ed_career_list as ( id int
                               ,employee_id int
			       ,contract_id int
			       ,date_of_join varchar(15)
			       ,ac_conform_due_date varchar(15)
			       ,leave_date varchar(15)
			       ,date_start varchar(15)
			       ,date_end varchar(15)       
          );

CREATE OR REPLACE FUNCTION ed_career_func(dep_id integer)
  RETURNS SETOF ed_career_list AS
$BODY$
DECLARE
   r ed_career_list%rowtype;
   sqlstr text;
   s1 varchar(100):='';  

BEGIN

    if dep_id > 0 then
        select ' where  emp.department_id =' || dep_id into s1 ; 
    end if;
    
    DROP SEQUENCE if exists career_seq;
    CREATE TEMP sequence career_seq;

    DROP TABLE if exists tmp_career_list;
    CREATE TEMP TABLE tmp_career_list
	( id int,  
	  employee_id int,
	  contract_id int,
	  date_of_join varchar(15)
	  ,ac_conform_due_date varchar(15)
	  ,leave_date varchar(15)
	  ,date_start varchar(15)
	  ,date_end varchar(15))  
	 
     ON COMMIT DROP;
    
   sqlstr := 'INSERT INTO tmp_career_list(id, employee_id,contract_id,date_of_join,ac_conform_due_date,leave_date,date_start,date_end)
    ( SELECT nextval(''career_seq'') as id
	     , x.employee_id
	     , x.contract_id
	     , x.date_of_join
	     , x.ac_conform_due_date
	     , x.leave_date 	     
	     , x.date_start
	     , x.date_end
	FROM
		( 
		select emp.id as employee_id
		      ,crt.id as contract_id 
		      ,to_char(emp.date_of_join,''dd/mm/yyyy'' )AS date_of_join
		      ,to_char(emp.ac_conform_due_date,''dd/mm/yyyy'' )AS ac_conform_due_date
		      ,to_char(emp.leave_date,''dd/mm/yyyy'' )AS leave_date
		      ,to_char(crt.date_start,''dd/mm/yyyy'' )AS date_start
		      ,to_char(crt.date_end,''dd/mm/yyyy'' )AS date_end
		       from hr_employee emp left outer join hr_contract crt on crt.employee_id = emp.id 
		'||s1||')x
    )';

    execute sqlstr;
    
    for r in SELECT * FROM tmp_career_list loop
	return next r;          
    end loop;
    
    return;  
END 

$BODY$
  LANGUAGE 'plpgsql' VOLATILE
  COST 100;

-- **************************************************************************************************************************
--                                    views fetch to career lines
-- ***************************************************************************************************************************  

DROP VIEW IF EXISTS vw_ed_career_lines;
CREATE OR REPLACE VIEW vw_ed_career_lines AS
select 1 as id
      ,q.employee_id
      ,q.contract_id
      ,q.date_of_join
      ,q.ac_conform_due_date
      ,q.leave_date
      ,q.date_start
      ,q.date_end
	from (select * from ed_career_func(18))q;


-- **************************************************************************************************************************
--                                    VIEW: Allocation Report
-- *************************************************************************************************************************** 

DROP VIEW IF EXISTS vw_ed_allocation;
CREATE OR REPLACE VIEW vw_ed_allocation AS
   select 1 as id; 

-- **************************************************************************************************************************
--                                    FUNCTION: Allocation Report
-- *************************************************************************************************************************** 

drop type if exists ed_dept cascade;
create type ed_dept as
( id int,
  department_id int,
  job_id int,
  name text 
);


CREATE OR REPLACE FUNCTION ed_allocation()
  RETURNS SETOF ed_dept AS
$BODY$
DECLARE
   ro ed_dept%rowtype; 
   rec record;
   strn text = E'\n';
   
BEGIN	  
     
    DROP SEQUENCE if exists dpt_sq;
    CREATE TEMP sequence dpt_sq;    
     
    DROP TABLE if exists tmp_allocation;
    CREATE TEMP TABLE tmp_allocation
		( id int,
		  department_id int,
		  job_id int,
		  name text 
		 )
    on commit drop; 
   
   insert into tmp_allocation(id, department_id, job_id)
   ( 	select nextval('dpt_sq')
	      , d.id as department_id 
	      , j.id as job_id
        from hr_department d 
	cross join hr_job j 
   );

   for rec in select * from tmp_allocation loop
       update tmp_allocation 
         set name = (   
			select array_to_string(array(
			    select al.employee || ' - ' || al.allocation || '%' 
			    from
			    ( select a.allocation
				   , r.name as employee
			      from ed_hr_allocation a
			      inner join hr_employee e on e.id = a.hr_emp_id
			      inner join resource_resource r on r.id = e.resource_id
			      where a.department_id = rec.department_id
			      and (select c.job_id from hr_contract c where c.employee_id = e.id order by date_start desc limit 1) = rec.job_id
			  
			   )al  
			),strn)
		    )
	 where id = rec.id;
   end loop;
    
   for ro in  select * from tmp_allocation loop
	return next ro;          
   end loop;
 return;  
END 

$BODY$
  LANGUAGE 'plpgsql' VOLATILE
  COST 100;

-- **************************************************************************************************************************
--                                    VIEW: Allocation Report [lines]
-- *************************************************************************************************************************** 

DROP VIEW IF EXISTS vw_ed_allocation_lines;
CREATE OR REPLACE VIEW vw_ed_allocation_lines AS
    select t.id
          , t.department_id
          , t.job_id
          , t.name
          ,1 as main
    from 
    ( select * from ed_allocation())t;


-- =========================================================================================
-- 		VIEW: Stock Detail Report
-- ========================================================================================= 
DROP VIEW if exists ed_view_stock_rpt1;

CREATE OR REPLACE VIEW ed_view_stock_rpt1 AS
SELECT 1 as id 
     , 1 as name
     , '2011-06-27' as start_dt
     , '2011-06-27' as end_dt;

-- =========================================================================================
-- 		TABLE: Stock Detail Report
-- ========================================================================================= 
DROP TABLE if exists tmp_stock_detail cascade;

CREATE TABLE tmp_stock_detail
( id integer,
  uid integer,
  stk_id integer,
  stk_dt date,
  seq integer,
  product_id integer,
  detail varchar(150),
  reference varchar(300),
  opening numeric(16,2),
  arrival numeric(16,2),
  issue numeric(16,2),  
  closing numeric(16,2)  
);

-- =========================================================================================
-- 		FUNCTION: Stock Detail Report
-- ========================================================================================= 

CREATE OR REPLACE FUNCTION ed_stock_detail(userid integer, component_id integer[], start_date date, end_date date)
  RETURNS void AS
$BODY$
DECLARE
	open_bal numeric(16,2);
	close_bal numeric(16,2);
	i integer;
	rec record;
	component record;
	st_date timestamp;
	ed_date timestamp;
BEGIN
    
    DROP SEQUENCE if exists tmp_sd_seq;
    CREATE TEMP sequence tmp_sd_seq;

    DROP SEQUENCE if exists tseq;
    CREATE TEMP sequence tseq;

    DELETE FROM tmp_stock_detail WHERE uid = userid;

    st_date := to_char((start_date|| ' 00:00:00')::timestamp, 'yyyy-mm-dd hh24:mi:ss');
    ed_date := to_char((end_date  || ' 23:59:59')::timestamp, 'yyyy-mm-dd hh24:mi:ss');

   FOR component IN (select id from product_product where id in (select unnest(component_id)) order by id) LOOP
	    INSERT INTO tmp_stock_detail(id, uid, seq, stk_dt, opening, arrival, issue, closing, product_id)
	    ( SELECT nextval('tmp_sd_seq') as id
		    , userid
		    , nextval('tseq') as seq
		    , start_date
		    , y.incoming_qty - x.outgoing_qty as opening
		    , 0
		    , 0 
		    , (y.incoming_qty - x.outgoing_qty) as closing
		    , x.product_id
		FROM 
		(	SELECT p.id as product_id
			     , CASE WHEN a.outgoing_qty IS NULL THEN 0 ELSE a.outgoing_qty END 
			FROM
			( 
				 SELECT sum(sm.product_qty) as outgoing_qty
				      , sm.product_id 
				 FROM stock_move sm 
				 INNER JOIN stock_location sl ON sm.location_id = sl.id 		 		 
				 WHERE upper(sl.name)='STOCK' AND sm.state='done' 
				 AND sm.location_id != sm.location_dest_id
				 AND sm.date < st_date AND sm.product_id = component.id
				 GROUP BY sm.product_id
			) a
			RIGHT OUTER JOIN product_product p ON p.id = a.product_id 
			LEFT OUTER JOIN product_template pt ON p.product_tmpl_id = pt.id
			LEFT OUTER JOIN product_category pc ON pt.categ_id = pc.id 
			WHERE p.id = component.id
		) x
		 INNER JOIN
		(	SELECT p.id  as product_id
			     , CASE WHEN a.incoming_qty IS NULL THEN 0 ELSE a.incoming_qty END 
			FROM
			( 
				 SELECT sum(sm.product_qty) as incoming_qty
				      , sm.product_id 
				 FROM stock_move sm 
				 INNER JOIN stock_location sl ON sm.location_dest_id = sl.id  
				 WHERE upper(sl.name)='STOCK' AND sm.state='done' 
				 AND sm.location_id != sm.location_dest_id
				 AND sm.date < st_date AND sm.product_id = component.id
				 GROUP BY sm.product_id 
			) a
			RIGHT OUTER JOIN product_product p ON p.id = a.product_id 		
			LEFT OUTER JOIN product_template pt ON p.product_tmpl_id = pt.id
			LEFT OUTER JOIN product_category pc ON pt.categ_id = pc.id 
			WHERE p.id = component.id
		) y 
		ON x.product_id = y.product_id
	    ); 

	    select opening into open_bal from tmp_stock_detail where uid = userid and product_id = component.id ;

	    INSERT INTO tmp_stock_detail(id, uid, stk_dt, detail, reference, arrival, opening, issue, closing, stk_id, product_id)
	    ( SELECT nextval('tmp_sd_seq') as id 
		    , userid
		    , x.date
		    , x.detail 
		    , x.reference 
		    , CASE WHEN x.incoming_qty IS NULL THEN 0 ELSE x.incoming_qty END as arrival
		    , 0
		    , 0
		    , 0
		    , x.stk_id
		    , x.product_id
		FROM 
		(	
			 SELECT sm.product_id 
			      , sm.date as date
			      , product_qty as incoming_qty
			      , case when sp.type = 'out' then (select p.name from res_partner p 
				     inner join res_partner_address a on a.partner_id = p.id  where a.id = sp.address_id) 
				     else (case when sm.origin is null then sm.name else sm.origin end) end as detail
			      , sp.name as reference
			      , sm.id as stk_id
			 FROM stock_move sm 
			 INNER JOIN stock_location sl ON sm.location_dest_id = sl.id  
			 LEFT JOIN stock_picking sp ON sp.id = sm.picking_id
			 WHERE upper(sl.name)='STOCK' AND sm.state='done'
			 AND sm.location_id != sm.location_dest_id 
			 AND sm.date BETWEEN st_date AND ed_date
			 AND sm.product_id = component.id  
		  
		)x	
		ORDER BY x.product_id,x.date
	    );

	    INSERT INTO tmp_stock_detail(id, uid, stk_dt, detail, reference, issue, opening, arrival, closing, stk_id, product_id)
	    ( SELECT nextval('tmp_sd_seq') as id 
		    , userid
		    , x.date
		    , x.detail 
		    , x.reference
		    , CASE WHEN x.outgoing_qty IS NULL THEN 0 ELSE x.outgoing_qty END as issue 
		    , 0
		    , 0
		    , 0
		    , x.stk_id
		    , x.product_id
		FROM 
		(	 
			 SELECT sm.product_id 
			      , sm.date as date
			      , product_qty as outgoing_qty
			      , case when sp.type = 'out' then (select p.name from res_partner p 
				     inner join res_partner_address a on a.partner_id = p.id  where a.id = sp.address_id) 
				     else (case when sm.origin is null then sm.name else sm.origin end) end as detail
			      , sp.name as reference
			      , sm.id as stk_id
			 FROM stock_move sm 
			 INNER JOIN stock_location sl ON sm.location_id = sl.id 
			 LEFT JOIN stock_picking sp ON sp.id = sm.picking_id	 		 
			 WHERE upper(sl.name)='STOCK' AND sm.state='done' 
			 AND sm.location_id != sm.location_dest_id
			 AND sm.date BETWEEN st_date AND ed_date
			 AND sm.product_id = component.id 
			  
		)x
		ORDER BY x.product_id,x.date
	    );    

	      FOR rec IN (select * from tmp_stock_detail where uid = userid and product_id = component.id order by product_id) LOOP
	       IF rec.id != 1 THEN
		   close_bal = (open_bal+ rec.arrival) - rec.issue;
		   
		   update tmp_stock_detail set opening = open_bal
					 , closing = close_bal 				 
					 , seq = nextval('tseq') where id = rec.id;
					 
		   open_bal = close_bal;
		   
	       END IF;
	    
	    END LOOP;

  END LOOP;

END 

$BODY$
  LANGUAGE plpgsql VOLATILE
  COST 100;
-- =========================================================================================
-- 		VIEW: Stock Detail Report lines
-- ========================================================================================= 
DROP VIEW if exists ed_view_stock_rpt_lines;

CREATE OR REPLACE VIEW ed_view_stock_rpt_lines AS
 SELECT t.id
      , t.stk_dt
      , t.seq 
      , t.product_id
      , t.detail
      , t.reference
      , t.opening 
      , t.arrival
      , t.issue 
      , t.closing
      , 1 as main
  FROM tmp_stock_detail t
  WHERE t.uid = 1
  AND t.id not in (select id from tmp_stock_detail 
		   where (opening = 0 and arrival = 0 
                   and issue = 0 and closing = 0));

-- =========================================================================================
-- 		VIEW: Appraisal Score
-- ========================================================================================= 
DROP VIEW if exists ed_vw_appraisal_score;

CREATE OR REPLACE VIEW ed_vw_appraisal_score AS
	  select 1 as id
		,1 as resource_id;

-- =========================================================================================
-- 		VIEW: Appraisal Score Lines
-- ========================================================================================= 
DROP VIEW if exists ed_vw_appraisal_score_ln;

CREATE OR REPLACE VIEW ed_vw_appraisal_score_ln AS
          select   eo.id
	          ,eo.id as summary_id 
	          ,1 as main
          from ed_appraisal ea 
          inner join ed_app_overall eo on eo.appraisal_id = ea.id
          where ea.resource_id = 1 
          order by eo.id;

-- =========================================================================================
-- 		VIEW: ERP Implementation
-- ========================================================================================= 
DROP VIEW if exists ed_vw_erp_implemantation;
CREATE OR REPLACE VIEW ed_vw_erp_implemantation AS
                                select 1 as id
                                      ,'2012-01-01' as start_dt
                                      ,'2013-01-01' as end_dt
                                      ,1 as city_id
                                      ,1 as user_id;

-- =========================================================================================
-- 		VIEW: ERP Implementation Lines
-- ========================================================================================= 
DROP VIEW if exists ed_vw_erp_implemantation_ln;
CREATE OR REPLACE VIEW ed_vw_erp_implemantation_ln AS                                     	
select   so.id
	,so.id as sale_id
	,so.name as so_name
	,(select sp.id from product_category pc
	               inner join product_template pt on pt.categ_id = pc.id 
	               inner join stock_move sm on sm.product_id = pt.id
	               inner join stock_picking sp on sp.id = sm.picking_id
	               where sp.sale_id = so.id and sp.state = 'done'
		       and pc.name ='HDD'limit 1) as cdd_id
	,(select sp.id from product_category pc
	            inner join product_template pt on pt.categ_id = pc.id 
	            inner join stock_move sm on sm.product_id = pt.id
	            inner join stock_picking sp on sp.id = sm.picking_id
	            where sp.sale_id = so.id  and sp.state = 'done'
		    and pc.name='Products (SC)' limit 1) as workbk_id 
	,case when (select count(id) from sale_order where partner_id = so.partner_id and state != 'draft') > 1 then 'Existing' else 'New' end as scl_exist
	,(select sum(ed_students)from ed_class_details where sale_id = so.id) as tot_stu
	,(select sum(price_unit) from sale_order_line where order_id = so.id and lower(name)!= 'license') as price_unit
	,1 as main
from sale_order so
inner join res_partner_address rpa on rpa.id = so.partner_order_id
where so.date_order between '2013-01-01' and '2013-05-17'
and so.state not in ('draft','cancel')
--and rpa.id =116
--and so.user_id = 1
order by so.id;
