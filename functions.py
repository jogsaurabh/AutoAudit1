#from email import message
import sqlite3
import pandas as pd
import streamlit as st
from datetime import datetime
import numpy as np


def create_user(Name,user,password,designation):
    try:
        sqliteConnection = sqlite3.connect('autoaudit.db')
        cursor = sqliteConnection.cursor()
        #st.info("Done1")
        #add DS name in table
        sqlite_insert_with_param = """INSERT INTO Users
                          (Name,user,password,designation) 
                          VALUES (?,?,?,?);"""
        data_tuple = (Name,user,password,designation)
        #st.info("Done2")
        cursor.execute(sqlite_insert_with_param, data_tuple)
        sqliteConnection.commit()
        
        cursor.close()
        message_verify=("User Created...")
    except sqlite3.Error as error:
        message_verify=("Error while creating New User", error)
    finally:
        if sqliteConnection:
            sqliteConnection.close()
            #message=("The SQLite connection is closed")
            
    return message_verify

def get_audit_by_com(comp_name,audit):
    try:
        sqliteConnection = sqlite3.connect('autoaudit.db')
        cursor = sqliteConnection.cursor()
        query=f"SELECT id from Audit where Company_name='{comp_name}' AND Audit_Name ='{audit}'"
        sql_query=pd.read_sql_query(query,sqliteConnection)
        auditid = pd.DataFrame(sql_query)
        cursor.close()
    except sqlite3.Error as error:
        auditid=("Error while getting user name", error)
        st.write(auditid)
    finally:
        if sqliteConnection:
            sqliteConnection.close()
            #message=("The SQLite connection is closed")
        
    return auditid
    
    
def check_login(username,password,comp_name,role,audit) :
    try:
        sqliteConnection = sqlite3.connect('autoaudit.db')
        cursor = sqliteConnection.cursor()
        cursor.execute(f"SELECT password from Users where user='{username}'")
        passworddb=cursor.fetchone()
        #print(passworddb[0])
        cursor.close()
        sqliteConnection.close()
        #st.write(passworddb[0])
        if passworddb:
            if passworddb[0]==password:
                st.session_state['loggedIn'] = True
                st.session_state['User']=username
                st.session_state['Company']=comp_name
                st.session_state['Role']=role
                st.session_state['Audit']=audit
                auditid=get_audit_by_com(comp_name,audit)
                audit_id=auditid['id'].values[0]
                st.session_state['AuditID']=audit_id
                #st.success(st.session_state['AuditID'])
                return True
            else:
                st.session_state['loggedIn'] = False
                st.error("Invalid password")
                return False
        else:
            st.session_state['loggedIn'] = False
            st.error("Invalid user name ")
            return False
            
    except sqlite3.Error as error:
        if sqliteConnection:
            sqliteConnection.close()
        st.error(error)
        return False
        
    finally:
        if sqliteConnection:
            sqliteConnection.close()
            #message=("The SQLite connection is closed")
        
def create_company(comp_name, com_address,com_email,com_mobile,com_person):
    try:
        sqliteConnection = sqlite3.connect('autoaudit.db')
        cursor = sqliteConnection.cursor()
        #st.info("Done1")
        #add DS name in table
        sqlite_insert_with_param = """INSERT INTO Company
                          (Name,Address,email,mobile,contact_person) 
                          VALUES (?,?,?,?,?);"""
        data_tuple = (comp_name, com_address,com_email,com_mobile,com_person)
        #st.info("Done2")
        cursor.execute(sqlite_insert_with_param, data_tuple)
        sqliteConnection.commit()
        cursor.close()
        st.info("created...")
        message_verify=("Company Created...")
    except sqlite3.Error as error:
        message_verify=("Error while creating New Company", error)
        st.info(error)
        st.info(comp_name)
    finally:
        if sqliteConnection:
            sqliteConnection.close()
            #message=("The SQLite connection is closed")
            
    return message_verify
    
def add_datato_ds(df,table_name,comp_name):
    try:
        #ds=table_name
        table_name= f"{comp_name}_{st.session_state['AuditID']}_{table_name}"
        sqliteConnection = sqlite3.connect('autoaudit.db')
        cursor = sqliteConnection.cursor()
        df.to_sql(table_name,sqliteConnection,if_exists='append', index=False)
        message=("Data Set Appended Successfully")
        sqliteConnection.commit()
        cursor.close()
        
    except sqlite3.Error as error:
        message=("Error while Appending Data Set ", error)
    except ValueError:
        message=(error)
        st.error("Values Mismatch...Data Set NOT Appended ")
    finally:
        if sqliteConnection:
            sqliteConnection.close()
            #message=("The SQLite connection is closed")
            
    return message

def assign_user_rights(user,company_name,role):
    try:
        sqliteConnection = sqlite3.connect('autoaudit.db')
        cursor = sqliteConnection.cursor()
        #st.info("Done1")
        #add DS name in table
        sqlite_insert_with_param = """INSERT INTO Users_Rights
                          (user,company_name,role) 
                          VALUES (?,?,?);"""
        data_tuple = (user,company_name,role)
        #st.info("Done2")
        cursor.execute(sqlite_insert_with_param, data_tuple)
        sqliteConnection.commit()
        cursor.close()
        st.info("User Rights Assigned...")
        message_verify=("User Rights Assigned...")
    except sqlite3.Error as error:
        message_verify=("Error while creating New Company", error)
        st.info(error)
        st.info(company_name)
    finally:
        if sqliteConnection:
            sqliteConnection.close()
            #message=("The SQLite connection is closed")
            
    return message_verify

def create_dataset(df,table_name,comp_name,person_responsible):
    try:
        ds=table_name
        currentime=datetime.now()
        table_name= f"{comp_name}_{st.session_state['AuditID']}_{table_name}"
        sqliteConnection = sqlite3.connect('autoaudit.db')
        cursor = sqliteConnection.cursor()
        df.to_sql(table_name,sqliteConnection,if_exists='fail', index=True)
        message=("Data Set created Successfully")
        sqliteConnection.commit()
        cursor.close()
        #add DS name in table
        cursor = sqliteConnection.cursor()
        sqlite_insert_with_param = """INSERT INTO DSName
                          (DS,company_name,person_responsible,created_by,cretaed_on,Audit_Name,Audit_id) 
                          VALUES (?,?,?,?,?,?,?);"""
        data_tuple = (ds,comp_name,person_responsible,st.session_state['User'],currentime,st.session_state['Audit'],int(st.session_state['AuditID']))
        cursor.execute(sqlite_insert_with_param,data_tuple)
        sqliteConnection.commit()
        cursor.close()
        message=("Data Set Added Successfully")
        # Alter table to add  audit status
        cursor = sqliteConnection.cursor()
        cursor.execute(f"ALTER TABLE '{table_name}' ADD Status TEXT NOT NULL DEFAULT 'Unaudited'")
        sqliteConnection.commit()
        cursor.close()
        # Alter table to add  audit Sampled?
        cursor = sqliteConnection.cursor()
        cursor.execute(f"ALTER TABLE '{table_name}' ADD Sampled TEXT NOT NULL DEFAULT 'Yes'")
        sqliteConnection.commit()
        cursor.close()
    except sqlite3.Error as error:
        message=("Error while creating Data Set to sqlite", error)
    except ValueError:
        message=("DS Name aready exist...You can create new Dataset with Other Name")
        st.error("DS Name aready exist...You can create new Dataset with Other Name")
    finally:
        if sqliteConnection:
            sqliteConnection.close()
            #message=("The SQLite connection is closed")
            
    return message

def add_verification_criteria (Criteria,DsName,comp_name):
    
    try:
        sqliteConnection = sqlite3.connect('autoaudit.db')
        cursor = sqliteConnection.cursor()
        #st.info("Done1")
        #add DS name in table
        currentime=datetime.now()
        sqlite_insert_with_param = """INSERT INTO DSCriteria
                          (Verification_Criteria,DSName,CompanyName,created_by,created_on,Audit_Name,Audit_id) 
                          VALUES (?,?,?,?,?,?,?);"""
        data_tuple = (Criteria,DsName,comp_name,st.session_state['User'],currentime,st.session_state['Audit'],int(st.session_state['AuditID']))
        #st.info("Done2")
        cursor.execute(sqlite_insert_with_param, data_tuple)
        sqliteConnection.commit()
        #st.info("Done3")
        #query=f"SELECT Verification_Criteria from DSCriteria where DsName='{DsName}' AND CompanyName='{comp_name}'"
        #st.write(query)
        #sql_query=pd.read_sql_query(query,sqliteConnection)
        df = "Added Successfully.."
        cursor.close()
        message_verify=(df)
    except sqlite3.Error as error:
        message_verify=("Error while creating Data Set Criteria", error)
    finally:
        if sqliteConnection:
            sqliteConnection.close()
            #message=("The SQLite connection is closed")
            
    return message_verify

def get_dsname(auditid):
    try:
        sqliteConnection = sqlite3.connect('autoaudit.db')
        cursor = sqliteConnection.cursor()
        query=f"SELECT DS from DSName where Audit_id='{auditid}'"
        sql_query=pd.read_sql_query(query,sqliteConnection)
        DSName = pd.DataFrame(sql_query)
        cursor.close()
    except sqlite3.Error as error:
        DSName=("Error while creating Data Set Criteria", error)
        
    finally:
        if sqliteConnection:
            sqliteConnection.close()
            #message=("The SQLite connection is closed")
        
    return DSName

def get_dsname_personresponsible(auditid,pr):
    try:
        sqliteConnection = sqlite3.connect('autoaudit.db')
        cursor = sqliteConnection.cursor()
        query=f"SELECT DS,person_responsible from DSName where Audit_id='{auditid}' AND person_responsible='{pr}'"
        sql_query=pd.read_sql_query(query,sqliteConnection)
        DSName = pd.DataFrame(sql_query)
        cursor.close()
    except sqlite3.Error as error:
        DSName=("Error while creating Data Set Criteria", error)
        
    finally:
        if sqliteConnection:
            sqliteConnection.close()
            #message=("The SQLite connection is closed")
        
    return DSName

def get_dataset(DSname):
    #this is for auditing
    try:
        sqliteConnection = sqlite3.connect('autoaudit.db')
        cursor = sqliteConnection.cursor()
        query=f"SELECT * from '{DSname}' where Status ='Unaudited'"
        sql_query=pd.read_sql_query(query,sqliteConnection)
        df = pd.DataFrame(sql_query)
        cursor.close()
    except sqlite3.Error as error:
        df=("Error while creating Data Set Criteria", error)
        
    finally:
        if sqliteConnection:
            sqliteConnection.close()
            #message=("The SQLite connection is closed")
        
    return df

def get_verification(DSname,Audit_id):
    try:
        sqliteConnection = sqlite3.connect('autoaudit.db')
        cursor = sqliteConnection.cursor()
        query=f"SELECT Verification_Criteria from DSCriteria where DsName='{DSname}' AND Audit_id='{Audit_id}'"
        sql_query=pd.read_sql_query(query,sqliteConnection)
        df = pd.DataFrame(sql_query)
        cursor.close()
    except sqlite3.Error as error:
        df=("Error while creating Data Set Criteria", error)
    finally:
        if sqliteConnection:
            sqliteConnection.close()
            #message=("The SQLite connection is closed")
        
    return df

def add_analytical_review (review,DsName,comp_name):
    
    try:
        sqliteConnection = sqlite3.connect('autoaudit.db')
        cursor = sqliteConnection.cursor()
        #st.info("Done1")
        #add DS name in table
        #table_name="AR_"+DsName
        sqlite_insert_with_param = f"""INSERT INTO Audit_AR
                          (Review,DataSetName,CompanyName,Created_on,created_by,Audit_Name,Audit_id) 
                          VALUES (?,?,?,?,?,?,?);"""
        
        currentime=datetime.now()
        data_tuple = (review,DsName,comp_name,currentime,st.session_state['User'],st.session_state['Audit'],int(st.session_state['AuditID']))
        #st.info("Done2")
        
        cursor.execute(sqlite_insert_with_param, data_tuple)
        sqliteConnection.commit()
        st.info("Review inserted")
        #get list of reviews
        query=f"SELECT Review from Audit_AR where DataSetName='{DsName}' AND CompanyName='{comp_name}'"
        #st.write(query)
        sql_query=pd.read_sql_query(query,sqliteConnection)
        df = pd.DataFrame(sql_query)
        cursor.close()
        reviews=(df)
    except sqlite3.Error as error:
        reviews=("Error while creating Data Set Criteria", error)
    finally:
        if sqliteConnection:
            sqliteConnection.close()
            #message=("The SQLite connection is closed")
            
    return reviews

def insert_vouching(data_id,field,audit_value,remarks,DsName,comp_name):
     
    try:
        sqliteConnection = sqlite3.connect('autoaudit.db')
        cursor = sqliteConnection.cursor()
        #st.info("Done1")
        #add DS name in table
        
        sqlite_insert_with_param = f"""INSERT INTO Audit_Queries
                          (Data_Id,Field,Audit_Value,Remarks,Audited_on,DataSetName,CompanyName,Audited_By,Audit_Name,Audit_id) 
                          VALUES (?,?,?,?,?,?,?,?,?,?);"""
        currentime=datetime.now()
        data_tuple = (data_id,field,audit_value,remarks,currentime,DsName,comp_name,st.session_state['User'],st.session_state['Audit'],int(st.session_state['AuditID']))
        #st.info("Done2")
        
        cursor.execute(sqlite_insert_with_param, data_tuple)
        sqliteConnection.commit()
        #st.info("Vouching saved")
        cursor.close()
        vouching=("Vouching Data Saved....")
        #update DS table status
        #update_status=update_audit_status(data_id,DsName)
    except sqlite3.Error as error:
        vouching=("Error while saving Vouching", error)
    finally:
        if sqliteConnection:
            sqliteConnection.close()
            #message=("The SQLite connection is closed")
            
    return vouching


def update_audit_status(data_id,DsName):
     
    try:
        sqliteConnection = sqlite3.connect('autoaudit.db')
        cursor = sqliteConnection.cursor()
        #update audit status
        query=f"UPDATE '{DsName}' SET Status ='Audited' WHERE `index` = {data_id}"
        #query=f"SELECT Review from Audit_AR where DataSetName='{DsName}' AND CompanyName='{comp_name}'"
        #st.write(query)
        cursor.execute(query)
        sqliteConnection.commit()
        cursor.close()
        auditstatus=("Audit Status updated....")
    except sqlite3.Error as error:
        auditstatus=("Error while Updating Audit Status", error)
    finally:
        if sqliteConnection:
            sqliteConnection.close()
            #message=("The SQLite connection is closed")
            
    return auditstatus

  
def get_queries(auidt_id):
    try:
        sqliteConnection = sqlite3.connect('autoaudit.db')
        cursor = sqliteConnection.cursor()
        query=f"SELECT * from Audit_Queries where Audit_id={auidt_id}"
        sql_query=pd.read_sql_query(query,sqliteConnection)
        df = pd.DataFrame(sql_query)
        cursor.close()
    except sqlite3.Error as error:
        df=("Error while getting Audit Queries", error)
        
    finally:
        if sqliteConnection:
            sqliteConnection.close()
            #message=("The SQLite connection is closed")
        
    return df

def get_pending_queries(auidt_id):
    try:
        sqliteConnection = sqlite3.connect('autoaudit.db')
        cursor = sqliteConnection.cursor()
        query=f"SELECT * from Audit_Queries where Audit_id={auidt_id} AND Status='Pending' AND (Audit_Verification='No' OR Audit_Value IS NOT NULL)"
        sql_query=pd.read_sql_query(query,sqliteConnection)
        df = pd.DataFrame(sql_query)
        cursor.close()
    except sqlite3.Error as error:
        df=("Error while getting Audit Queries", error)
        
    finally:
        if sqliteConnection:
            sqliteConnection.close()
            #message=("The SQLite connection is closed")
        
    return df

def get_entire_dataset(DSname):
    #this is for auditing
    try:
        sqliteConnection = sqlite3.connect('autoaudit.db')
        cursor = sqliteConnection.cursor()
        query=f"SELECT * from '{DSname}'"
        sql_query=pd.read_sql_query(query,sqliteConnection)
        df = pd.DataFrame(sql_query)
        cursor.close()
    except sqlite3.Error as error:
        df=("Error while creating Data Set Criteria", error)
        
    finally:
        if sqliteConnection:
            sqliteConnection.close()
            #message=("The SQLite connection is closed")
        
    return df

def add_audit_verification(df):
    try:
            sqliteConnection = sqlite3.connect('autoaudit.db')
            cursor = sqliteConnection.cursor()
            df.to_sql("Audit_Queries",sqliteConnection,if_exists='append', index=False)
            
            sqliteConnection.commit()
            cursor.close()
            message=("Audit Verification added Successfully")
            
    except sqlite3.Error as error:
            message=("Error while saving Audit Verification", error)
    finally:
            if sqliteConnection:
                sqliteConnection.close()
                #message=("The SQLite connection is closed")
            
    return message

def get_ar(comp_name):
    try:
        sqliteConnection = sqlite3.connect('autoaudit.db')
        cursor = sqliteConnection.cursor()
        query=f"SELECT * from Audit_AR where CompanyName='{comp_name}'"
        sql_query=pd.read_sql_query(query,sqliteConnection)
        df = pd.DataFrame(sql_query)
        cursor.close()
    except sqlite3.Error as error:
        df=("Error while getting Audit Reviews", error)
        
    finally:
        if sqliteConnection:
            sqliteConnection.close()
            #message=("The SQLite connection is closed")
        
    return df

def get_ar_for_ds(ds_name):
    try:
        sqliteConnection = sqlite3.connect('autoaudit.db')
        cursor = sqliteConnection.cursor()
        query=f"SELECT Review from Audit_AR where DataSetName='{ds_name}' and Audit_id='{int(st.session_state['AuditID'])}'"
        sql_query=pd.read_sql_query(query,sqliteConnection)
        df = pd.DataFrame(sql_query)
        cursor.close()
    except sqlite3.Error as error:
        df=("Error while getting Audit Reviews", error)
        
    finally:
        if sqliteConnection:
            sqliteConnection.close()
            #message=("The SQLite connection is closed")
        
    return df

def get_company_names():
    try:
        sqliteConnection = sqlite3.connect('autoaudit.db')
        cursor = sqliteConnection.cursor()
        cursor.execute("SELECT Name from Company")
        compnamesT=cursor.fetchall()
        #tuple to nap arry convert
        compnames=pd.DataFrame(compnamesT)
        #st.write(compnames)
        cursor.close()
    except sqlite3.Error as error:
        compnames=("Error while getting Company Names", error)
        
    finally:
        if sqliteConnection:
            sqliteConnection.close()
            #message=("The SQLite connection is closed")
        
    return compnames

def get_user_rights():
    try:
        sqliteConnection = sqlite3.connect('autoaudit.db')
        cursor = sqliteConnection.cursor()
        query="SELECT * from Users_Rights"
        sql_query=pd.read_sql_query(query,sqliteConnection)
        userrights = pd.DataFrame(sql_query)
        cursor.close()
    except sqlite3.Error as error:
        userrights=("Error while getting user rights", error)
        st.write(userrights)
    finally:
        if sqliteConnection:
            sqliteConnection.close()
            #message=("The SQLite connection is closed")
        
    return userrights

def get_active_users():
    try:
        sqliteConnection = sqlite3.connect('autoaudit.db')
        cursor = sqliteConnection.cursor()
        cursor.execute("SELECT user from Users where is_active='Yes'")
        usersT=cursor.fetchall()
        #tuple to list convert
        users=pd.DataFrame(usersT)
        #st.write(users)
        cursor.close()
    except sqlite3.Error as error:
        users=("Error while getting User Names", error)
        st.write(users)
    finally:
        if sqliteConnection:
            sqliteConnection.close()
            #message=("The SQLite connection is closed")
        
    return users

def get_auditee_comp():
    try:
        sqliteConnection = sqlite3.connect('autoaudit.db')
        cursor = sqliteConnection.cursor()
        query=f"SELECT user from Users_Rights where company_name='{st.session_state['Company']}' AND role ='Auditee'"
        sql_query=pd.read_sql_query(query,sqliteConnection)
        auditee = pd.DataFrame(sql_query)
        cursor.close()
    except sqlite3.Error as error:
        auditee=("Error while getting user name", error)
        st.write(auditee)
    finally:
        if sqliteConnection:
            sqliteConnection.close()
            #message=("The SQLite connection is closed")
        
    return auditee

def get_audit(compname):
    try:
        sqliteConnection = sqlite3.connect('autoaudit.db')
        cursor = sqliteConnection.cursor()
        query=f"SELECT Audit_Name from Audit where Company_name='{compname}' AND Status ='Open'"
        sql_query=pd.read_sql_query(query,sqliteConnection)
        audits = pd.DataFrame(sql_query)
        cursor.close()
    except sqlite3.Error as error:
        audits=("Error while getting user name", error)
        st.write(audits)
    finally:
        if sqliteConnection:
            sqliteConnection.close()
            #message=("The SQLite connection is closed")
        
    return audits

def get_comp_by_user():
    try:
        sqliteConnection = sqlite3.connect('autoaudit.db')
        cursor = sqliteConnection.cursor()
        query=f"SELECT company_name from Users_Rights where user='{st.session_state['User']}' and role='Manager'"
        sql_query=pd.read_sql_query(query,sqliteConnection)
        companies = pd.DataFrame(sql_query)
        cursor.close()
    except sqlite3.Error as error:
        companies=("Error while getting company names", error)
        st.write(companies)
    finally:
        if sqliteConnection:
            sqliteConnection.close()
            #message=("The SQLite connection is closed")
        
    return companies

def creat_audit(Audit_Name,Company_name, Period,Remarks):
    try:
        sqliteConnection = sqlite3.connect('autoaudit.db')
        cursor = sqliteConnection.cursor()
        #st.info("Done1")
        #add DS name in table
        currentime=datetime.now()
        sqlite_insert_with_param = """INSERT INTO Audit
                          (Audit_Name,Company_name,Period,Remarks,Created_by,Created_on) 
                          VALUES (?,?,?,?,?,?);"""
        data_tuple = (Audit_Name,Company_name,Period,Remarks,st.session_state['User'],currentime)
        #st.info("Done2")
        cursor.execute(sqlite_insert_with_param, data_tuple)
        sqliteConnection.commit()
        cursor.close()
        st.info("Audit created...")
        message_verify=("Audit Created...")
    except sqlite3.Error as error:
        message_verify=("Error while creating New Audit", error)
        st.info(error)
        
    finally:
        if sqliteConnection:
            sqliteConnection.close()
            #message=("The SQLite connection is closed")
            
    return message_verify

def add_query_reply(id,reply):
    
    try:
        sqliteConnection = sqlite3.connect('autoaudit.db')
        cursor = sqliteConnection.cursor()
        #update audit status
        query=f"UPDATE Audit_Queries SET Reply ='{reply}' WHERE Id = {id}"
        #query=f"SELECT Review from Audit_AR where DataSetName='{DsName}' AND CompanyName='{comp_name}'"
        #st.write(query)
        cursor.execute(query)
        sqliteConnection.commit()
        cursor.close()
        updatereply=("Query Reply updated....")
    except sqlite3.Error as error:
        updatereply=("Error while Updating Query Status", error)
    finally:
        if sqliteConnection:
            sqliteConnection.close()
            #message=("The SQLite connection is closed")
            
    return updatereply

def update_query_status(id,reply,close):
    
    try:
        sqliteConnection = sqlite3.connect('autoaudit.db')
        cursor = sqliteConnection.cursor()
        #update audit status
        query=f"UPDATE Audit_Queries SET status_udate_by ='{reply}',Status ='{close}' WHERE Id = {id}"
        #query=f"SELECT Review from Audit_AR where DataSetName='{DsName}' AND CompanyName='{comp_name}'"
        #st.write(query)
        cursor.execute(query)
        sqliteConnection.commit()
        cursor.close()
        updatereply=("Query Status updated....")
    except sqlite3.Error as error:
        updatereply=("Error while Updating Query Status", error)
    finally:
        if sqliteConnection:
            sqliteConnection.close()
            #message=("The SQLite connection is closed")
            
    return updatereply
