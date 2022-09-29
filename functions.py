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
                st.info("Invalid password")
                return False
        else:
            st.session_state['loggedIn'] = False
            st.info("Invalid user name ")
            return False
            
    except sqlite3.Error as error:
        if sqliteConnection:
            sqliteConnection.close()
        st.info(error)
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
                          (Name,Address,email,mobile,contact_person,Created_by) 
                          VALUES (?,?,?,?,?,?);"""
        data_tuple = (comp_name, com_address,com_email,com_mobile,com_person,st.session_state['User'])
        #st.info("Done2")
        cursor.execute(sqlite_insert_with_param, data_tuple)
        sqliteConnection.commit()
        cursor.close()
        st.info("created...")
        message_verify=("Company Created...")
    except sqlite3.Error as error:
        message_verify=("Error while creating New Company", error)
        st.info(error)
        #st.info(comp_name)
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
        st.info("Values Mismatch...Data Set NOT Appended ")
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
        # add default risk to risk master table
        #get list of columns in df
        sqliteConnection.close()
        sqliteConnection = sqlite3.connect('autoaudit.db')
        cursor = sqliteConnection.cursor()
        cols=list(df.columns)
        risk_df=pd.DataFrame(cols,columns=['Field'])
        risk_df['audit_id']=int(st.session_state['AuditID'])
        risk_df['DataSetName']=ds
        risk_df['created_by']=st.session_state['User']
        risk_df['created_on']=currentime
        risk_df['Criteria']=risk_df['Field']+': should be Correct'
        #st.dataframe(risk_df)
        risk_df.to_sql("Risk_Master",sqliteConnection,if_exists='append', index=False)
        #st.write('okkkkkk')
        sqliteConnection.commit()
        cursor.close()
    except sqlite3.Error as error:
        st.info=("Error while creating Data Set to sqlite", error)
        message="Error in Dataset Creation"
    except ValueError:
        message=("DS Name aready exist...You can create new Dataset with Other Name")
        #st.info("DS Name aready exist...You can create new Dataset with Other Name")
    finally:
        
        if sqliteConnection:
            sqliteConnection.close()
            #message=("The SQLite connection is closed")
            
    return message

def add_verification_criteria (Criteria,DsName,comp_name,risk_weight,risk_category):
    
    try:
        sqliteConnection = sqlite3.connect('autoaudit.db')
        cursor = sqliteConnection.cursor()
        #st.info("Done1")
        #add DS name in table
        currentime=datetime.now()
        sqlite_insert_with_param = """INSERT INTO DSCriteria
                          (Verification_Criteria,DSName,Risk_Weight,Risk_Category,CompanyName,created_by,created_on,Audit_Name,Audit_id) 
                          VALUES (?,?,?,?,?,?,?,?,?);"""
        data_tuple = (Criteria,DsName,risk_weight,risk_category,comp_name,st.session_state['User'],currentime,st.session_state['Audit'],int(st.session_state['AuditID']))
        #st.info("Done2")
        cursor.execute(sqlite_insert_with_param, data_tuple)
        sqliteConnection.commit()
        
        #Add in risk master
        sqlite_insert_with_param = """INSERT INTO Risk_Master
                          (Criteria,DataSetName,Risk_Weight,created_by,created_on,Audit_id,Risk_Category) 
                          VALUES (?,?,?,?,?,?,?);"""
        data_tuple = (Criteria,DsName,risk_weight,st.session_state['User'],currentime,int(st.session_state['AuditID']),risk_category)
        #st.info("Done2")
        cursor.execute(sqlite_insert_with_param, data_tuple)
        sqliteConnection.commit()
        message_verify = "Added Successfully.."
        
        cursor.close()
        st.info(message_verify)
    except sqlite3.Error as error:
        message_verify=("Error while creating Data Set Criteria", error)
        st.write(message_verify)
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
        query=f"SELECT DS from DSName where Audit_id='{auditid}' AND person_responsible='{pr}'"
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
        query=f"SELECT Verification_Criteria,Risk_Weight,Risk_Category from DSCriteria where DsName='{DSname}' AND Audit_id='{Audit_id}'"
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

def add_analytical_review (criteria,condition,cause,effect,DsName,comp_name,risk_weight,risk_category,file_name):
    
    try:
        sqliteConnection = sqlite3.connect('autoaudit.db')
        cursor = sqliteConnection.cursor()
        #st.info("Done1")
        #add DS name in table
        #table_name="AR_"+DsName
        sqlite_insert_with_param = f"""INSERT INTO Audit_AR
                          (Criteria,Condition,Cause,Effect,DataSetName,CompanyName,Created_on,Risk_Weight,Risk_Category,created_by,Audit_Name,Audit_id,Review_File) 
                          VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?);"""
        
        currentime=datetime.now()
        data_tuple = (criteria,condition,cause,effect,DsName,comp_name,currentime,risk_weight,risk_category,st.session_state['User'],st.session_state['Audit'],int(st.session_state['AuditID']),file_name)
        #st.info("Done2")
        
        cursor.execute(sqlite_insert_with_param, data_tuple)
        sqliteConnection.commit()
        st.info("Review Inserted")
        #get list of reviews
        #query=f"SELECT Criteria,Condition,Cause,Effect,Risk_Weight,Risk_Category,Review_File from Audit_AR where DataSetName='{DsName}' and Audit_id='{int(st.session_state['AuditID'])}'"
        #st.write(query)
        #sql_query=pd.read_sql_query(query,sqliteConnection)
        #df = pd.DataFrame(sql_query)
        cursor.close()
        df='Review Inserted'
    except sqlite3.Error as error:
        df=("Error while creating Data Set Criteria", error)
        st.info(df)
    finally:
        if sqliteConnection:
            sqliteConnection.close()
            #message=("The SQLite connection is closed")
            
    return df

def insert_vouching(df):
     
    try:
        sqliteConnection = sqlite3.connect('autoaudit.db')
        cursor = sqliteConnection.cursor()
        df.to_sql("Audit_Queries",sqliteConnection,if_exists='append', index=False)
            
        sqliteConnection.commit()
        cursor.close()
        vouching=("Audit Vouching added Successfully")
    except sqlite3.Error as error:
        vouching=("Error while saving Vouching", error)
        #st.info(vouching)
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
        query=f"SELECT * from Audit_Queries where Audit_id={auidt_id} AND Status='Pending' AND (Condition='No' OR Audit_Value IS NOT NULL)"
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
        query=f"SELECT Criteria,Condition,Cause,Effect,Risk_Weight,Risk_Category,Review_File from Audit_AR where DataSetName='{ds_name}' and Audit_id='{int(st.session_state['AuditID'])}'"
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
        cursor.execute(f"SELECT Name from Company")
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
        #if st.session_state['User']:
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
        query=f"UPDATE Audit_Queries SET Reply ='{reply}', Reply_by='{st.session_state['User']}' WHERE Id = {id}"
        #query=f"SELECT Review from Audit_AR where DataSetName='{DsName}' AND CompanyName='{comp_name}'"
        #st.write(query)
        cursor.execute(query)
        sqliteConnection.commit()
        cursor.close()
        updatereply=("Reply to Query is updated....")
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
        query=f"UPDATE Audit_Queries SET status_update_remarks ='{reply}',status_udate_by ='{st.session_state['User']}',Status ='{close}' WHERE Id = {id}"
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


def update_query_status_ar(id,reply,close):
    
    try:
        sqliteConnection = sqlite3.connect('autoaudit.db')
        cursor = sqliteConnection.cursor()
        #update audit status
        query=f"UPDATE Audit_AR SET status_update_remarks ='{reply}',status_update_by ='{st.session_state['User']}',Status ='{close}' WHERE Id = {id}"
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


def add_query_reply_AR(id,reply):
    
    try:
        sqliteConnection = sqlite3.connect('autoaudit.db')
        cursor = sqliteConnection.cursor()
        #update audit status
        query=f"UPDATE Audit_AR SET reply ='{reply}',reply_by ='{st.session_state['User']}' WHERE Id = {id}"
        #query=f"SELECT Review from Audit_AR where DataSetName='{DsName}' AND CompanyName='{comp_name}'"
        #st.write(query)
        cursor.execute(query)
        sqliteConnection.commit()
        cursor.close()
        updatereply=("Query Reply updated....")
    except sqlite3.Error as error:
        updatereply=("Error while Updating Query Reply", error)
    finally:
        if sqliteConnection:
            sqliteConnection.close()
            #message=("The SQLite connection is closed")
            
    return updatereply


def get_risk_weights_ds_vouching(ds_name):
    try:
        sqliteConnection = sqlite3.connect('autoaudit.db')
        cursor = sqliteConnection.cursor()
        query=f"SELECT Criteria,Risk_Weight,Risk_Category from Risk_Master where DataSetName='{ds_name}' and Audit_id={int(st.session_state['AuditID'])}"
        sql_query=pd.read_sql_query(query,sqliteConnection)
        df = pd.DataFrame(sql_query)
        #st.write(query)
        cursor.close()
    except sqlite3.Error as error:
        df=("Error while getting Audit Reviews", error)
        st.info(df)
    finally:
        if sqliteConnection:
            sqliteConnection.close()
            #message=("The SQLite connection is closed")
        
    return df



def get_risk_weights_ds(ds_name):
    try:
        sqliteConnection = sqlite3.connect('autoaudit.db')
        cursor = sqliteConnection.cursor()
        query=f"SELECT Criteria,Risk_Weight,Risk_Category from Risk_Master where DataSetName='{ds_name}' and Audit_id='{int(st.session_state['AuditID'])}'"
        sql_query=pd.read_sql_query(query,sqliteConnection)
        df = pd.DataFrame(sql_query)
        cursor.close()
    except sqlite3.Error as error:
        df=("Error while getting Audit Reviews", error)
        st.info(df)
    finally:
        if sqliteConnection:
            sqliteConnection.close()
            #message=("The SQLite connection is closed")
        
    return df

def update_risk_weights(criteria,DsName,auditid,risk_weight,risk_category):
     
    try:
        sqliteConnection = sqlite3.connect('autoaudit.db')
        cursor = sqliteConnection.cursor()
        #update audit status
        query=f"UPDATE Risk_Master  SET Risk_Weight={risk_weight} , Risk_Category ='{risk_category}' WHERE Criteria='{criteria}' AND audit_id ={auditid} AND DataSetName ='{DsName}'"
        #query=f"UPDATE  SET Status ='Audited' WHERE `index` = {data_id}"
        #query=f"SELECT Review from Audit_AR where DataSetName='{DsName}' AND CompanyName='{comp_name}'"
        #st.write(query)
        cursor.execute(query)
        sqliteConnection.commit()
        cursor.close()
        auditstatus=("Risk Weights updated....")
        st.info(auditstatus)
    except sqlite3.Error as error:
        auditstatus=("Error while Updating Audit Status", error)
        st.info(auditstatus)
    finally:
        if sqliteConnection:
            sqliteConnection.close()
            #message=("The SQLite connection is closed")
            
    return auditstatus


def update_verification_criteria(criteria,old_criteria,DsName,auditid,risk_weight,risk_category):
     
    try:
        sqliteConnection = sqlite3.connect('autoaudit.db')
        cursor = sqliteConnection.cursor()
        #update audit status
        query=f"UPDATE DSCriteria SET Verification_Criteria={criteria}, Risk_Weight={risk_weight} , Risk_Category ='{risk_category}' WHERE Verification_Criteria='{old_criteria}' AND audit_id ={auditid} AND DataSetName ='{DsName}'"
        #query=f"UPDATE  SET Status ='Audited' WHERE `index` = {data_id}"
        #query=f"SELECT Review from Audit_AR where DataSetName='{DsName}' AND CompanyName='{comp_name}'"
        #st.write(query)
        cursor.execute(query)
        sqliteConnection.commit()
        cursor.close()
        auditstatus=("Verification Criteria updated....")
        st.info(auditstatus)
    except sqlite3.Error as error:
        auditstatus=("Error while Updating Verification Criteria", error)
        #st.info(auditstatus)
    finally:
        if sqliteConnection:
            sqliteConnection.close()
            #message=("The SQLite connection is closed")
            
    return auditstatus

def get_dataset_values(DSname):
    #this is for auditing
    try:
        sqliteConnection = sqlite3.connect('autoaudit.db')
        cursor = sqliteConnection.cursor()
        values={}
        #get total count of DS
        query=f"SELECT count(*) from '{DSname}'"
        cursor.execute(query)
        total_records=cursor.fetchone()
        if total_records[0]!= None:
            total_records=int(total_records[0])
        #st.write(total_records,total_records)
            values['total_records']=total_records
        else:
            values['total_records']=0
        #get total count of DS where status=Audited
        query=f"SELECT count(*) from '{DSname}' WHERE status= 'Audited'"
        cursor.execute(query)
        total_audited=cursor.fetchone()
        if total_audited[0]!= None:
            #st.write(total_audited)
            total_audited=int(total_audited[0])
        #st.write(total_audited)
            values['total_audited']=total_audited
        else:
            values['total_audited']=0
        #st.write(values)
        cursor.close()
    except sqlite3.Error as error:
        message=("Error while creating Data Set Criteria", error)
        st.info(message)
    finally:
        if sqliteConnection:
            sqliteConnection.close()
            #message=("The SQLite connection is closed")
        
    return values


def get_audit_values(Audit_id):
    #this is for audit queries v&v per audit
    try:
        sqliteConnection = sqlite3.connect('autoaudit.db')
        cursor = sqliteConnection.cursor()
        values={}
        #get total count of audit queries v&v
        query=f"SELECT count(*) from Audit_Queries WHERE Status= 'Pending' AND Audit_Id='{Audit_id}'"
        cursor.execute(query)
        total_records=cursor.fetchone()
        if total_records[0]!= None:
            total_queries_vv=int(total_records[0])
        #st.write(total_records,total_records)
            values['total_queries_vv']=total_queries_vv
        else:
            values['total_queries_vv']=0
        
        #get total count of audit queries AR
        query=f"SELECT count(*) from Audit_AR WHERE status= 'Pending' AND Audit_Id='{Audit_id}'"
        cursor.execute(query)
        total_records=cursor.fetchone()
        if total_records[0]!= None:
            total_queries_ar=int(total_records[0])
        #st.write(total_records,total_records)
            values['total_queries_ar']=total_queries_ar
        else:
            values['total_queries_ar']=0
       
        cursor.close()
    except sqlite3.Error as error:
        message=("Error while creating Data Set Criteria", error)
        st.info(message)
    finally:
        if sqliteConnection:
            sqliteConnection.close()
            #message=("The SQLite connection is closed")
        
    return values

def get_values_id_dsn(Audit_id,datasetname):
    #this is for audit queries v&v- per DS
    try:
        sqliteConnection = sqlite3.connect('autoaudit.db')
        cursor = sqliteConnection.cursor()
        values={}
        #get total count of audit queries v&v
        query=f"SELECT count(*) from Audit_Queries WHERE Status= 'Pending' AND Audit_Id='{Audit_id}' AND DataSetName='{datasetname}'"
        cursor.execute(query)
        total_records=cursor.fetchone()
        if total_records[0]!= None:
            total_queries_vv=int(total_records[0])
        #st.write(total_records,total_records)
            values['total_queries_vv']=total_queries_vv
        else:
            values['total_queries_vv']=0
        
        #get total count of audit queries AR
        query=f"SELECT count(*) from Audit_AR WHERE status= 'Pending' AND Audit_id='{Audit_id}'AND DataSetName='{datasetname}'"
        cursor.execute(query)
        total_records=cursor.fetchone()
        if total_records[0]!= None:
            total_queries_ar=int(total_records[0])
        #st.write(total_records,total_records)
            values['total_queries_ar']=total_queries_ar
        else:
            values['total_queries_ar']=0
       
       #get risk score for Queries of DS
        query=f"SELECT sum (Risk_Weight) FROM queries_risk WHERE Audit_id='{Audit_id}'AND DataSetName='{datasetname}'"
        cursor.execute(query)
        total_records=cursor.fetchone()
        #st.write(total_records)
        if total_records[0]!= None:
            auditrisk_audited=int(total_records[0])
            #st.write(total_records,total_records)
            values['auditrisk_audited']=auditrisk_audited
        else:
            values['auditrisk_audited']=0
        
        #get risk score for Dataset
        query=f"SELECT sum (Risk_Weight) FROM Risk_Master WHERE Audit_id='{Audit_id}'AND DataSetName='{datasetname}'"
        cursor.execute(query)
        total_records=cursor.fetchone()
        if total_records[0]!= None:
            auditrisk_total=int(total_records[0])
         #st.write(total_records,total_records)
            values['auditrisk_total']=auditrisk_total
        else:
            values['auditrisk_total']=0
        cursor.close()
        #total Risk for DS= Total audited records * above
    except sqlite3.Error as error:
        message=("Error while creating Data Set Criteria", error)
        st.info(message)
    finally:
        if sqliteConnection:
            sqliteConnection.close()
            #message=("The SQLite connection is closed")
        
    return values

def get_vv_quries(DSfilename,DSName,audit_id):
    #this is for auditing
    try:
        sqliteConnection = sqlite3.connect('autoaudit.db')
        cursor = sqliteConnection.cursor()
        query=f"""
        SELECT b.*,a.Id,a.Criteria, a.Condition, a.Cause, a.Effect, a.Risk_Weight, a.Risk_Category, a.Audited_By, a.Audited_on, a.reply, a.reply_by, a.reply_on, 
            a.status_udate_by,a.status_update_remarks,a.Field
            FROM queries_risk a LEFT JOIN  "{DSfilename}" b ON a.Data_Id = b."index" WHERE DataSetName='{DSName}'
            AND audit_id ={audit_id} order by b."index";"""
        sql_query=pd.read_sql_query(query,sqliteConnection)
        df = pd.DataFrame(sql_query)
        cursor.close()
    except sqlite3.Error as error:
        df=("Error while creating Data Set Criteria", error)
        st.info(df)
    finally:
        if sqliteConnection:
            sqliteConnection.close()
            #message=("The SQLite connection is closed")
        
    return df

def get_ar_queries(ds_name):
    try:
        sqliteConnection = sqlite3.connect('autoaudit.db')
        cursor = sqliteConnection.cursor()
        query=f"""SELECT Id,Criteria,Condition,Cause,Effect,Risk_Weight,Risk_Category,created_by,
        created_on,reply,reply_by,reply_on,status_update_remarks,status_update_by,Review_File 
        from Audit_AR where DataSetName='{ds_name}' and Audit_id='{int(st.session_state['AuditID'])}'
        and status='Pending'"""
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

def get_Summary_audit_values(Audit_id,ds):
    #this is for summary audit queries v&v per audit id
    try:
        sqliteConnection = sqlite3.connect('autoaudit.db')
        cursor = sqliteConnection.cursor()
               
        query=f"SELECT Criteria,count(Criteria) as 'Total Queries' FROM queries_risk WHERE Audit_id='{Audit_id}' AND DataSetName='{ds}' GROUP BY Criteria"
        sql_query=pd.read_sql_query(query,sqliteConnection)
        df = pd.DataFrame(sql_query)
        #cursor.execute(query)
        
        cursor.close()
    except sqlite3.Error as error:
        message=("Error while creating Data Set Criteria", error)
        st.info(message)
    finally:
        if sqliteConnection:
            sqliteConnection.close()
            #message=("The SQLite connection is closed")
        
    return df

def get_Summary_audit_values_comp(Audit_id):
    #this is for summary audit queries v&v per audit id
    try:
        sqliteConnection = sqlite3.connect('autoaudit.db')
        cursor = sqliteConnection.cursor()
               
        query=f"SELECT DataSetName as 'Data Set Name',count(Criteria) as 'Total Queries' FROM queries_risk WHERE Audit_id='{Audit_id}' GROUP BY DataSetName"
        sql_query=pd.read_sql_query(query,sqliteConnection)
        df = pd.DataFrame(sql_query)
        #cursor.execute(query)
        
        cursor.close() 
    except sqlite3.Error as error:
        message=("Error while creating Data Set Criteria", error)
        st.info(message)
    finally:
        if sqliteConnection:
            sqliteConnection.close()
            #message=("The SQLite connection is closed")
        
    return df

def get_Summary_audit_values_riskweight(Audit_id,ds):
    #this is for summary audit queries v&v per audit id
    try:
        sqliteConnection = sqlite3.connect('autoaudit.db')
        cursor = sqliteConnection.cursor()
        #for V&V     
        query=f"SELECT Criteria,sum(Risk_Weight) as 'Total Risk Weight' FROM queries_risk WHERE Audit_id='{Audit_id}' AND DataSetName='{ds}' GROUP BY Criteria"
        sql_query=pd.read_sql_query(query,sqliteConnection)
        df = pd.DataFrame(sql_query)
        #for AR
        query=f"SELECT Criteria,sum(Risk_Weight) as 'Total Risk Weight' FROM Audit_AR WHERE Audit_id='{Audit_id}' AND DataSetName='{ds}' GROUP BY Criteria"
        sql_query=pd.read_sql_query(query,sqliteConnection)
        dfar = pd.DataFrame(sql_query)
        cursor.close()
        #merge 2 df
        df=df.append(dfar,ignore_index=True)
        
    except sqlite3.Error as error:
        message=("Error while creating Data Set Criteria", error)
        st.info(message)
    finally:
        if sqliteConnection:
            sqliteConnection.close()
            #message=("The SQLite connection is closed")
        
    return df

def get_Summary_audit_values_riskweight_comp(Audit_id):
    #this is for summary audit queries v&v per audit id
    try:
        sqliteConnection = sqlite3.connect('autoaudit.db')
        cursor = sqliteConnection.cursor()
               
        query=f"SELECT DataSetName as 'Data Set Name',sum(Risk_Weight) as 'Total Risk Weight' FROM queries_risk WHERE Audit_id='{Audit_id}'  GROUP BY DataSetName"
        sql_query=pd.read_sql_query(query,sqliteConnection)
        df = pd.DataFrame(sql_query)
        #cursor.execute(query)
        
        cursor.close()
    except sqlite3.Error as error:
        message=("Error while creating Data Set Criteria", error)
        st.info(message)
    finally:
        if sqliteConnection:
            sqliteConnection.close()
            #message=("The SQLite connection is closed")
        
    return df

def get_Summary_audit_values_riskcategory(Audit_id,ds):
    #this is for summary audit queries v&v per audit id
    try:
        sqliteConnection = sqlite3.connect('autoaudit.db')
        cursor = sqliteConnection.cursor()
               
        query=f"SELECT Criteria,Risk_Category,sum(Risk_Weight) as 'Total Risk Weight' FROM queries_risk WHERE Audit_id='{Audit_id}' AND DataSetName='{ds}' GROUP BY Criteria,Risk_Category"
        sql_query=pd.read_sql_query(query,sqliteConnection)
        df = pd.DataFrame(sql_query)
        #cursor.execute(query)
        
        cursor.close()
    except sqlite3.Error as error:
        message=("Error while creating Data Set Criteria", error)
        st.info(message)
    finally:
        if sqliteConnection:
            sqliteConnection.close()
            #message=("The SQLite connection is closed")
        
    return df

def get_company_docs(comp_name):
    try:
        sqliteConnection = sqlite3.connect('autoaudit.db')
        cursor = sqliteConnection.cursor()
        query=f"SELECT * from Company_File where Company='{comp_name}'"
        sql_query=pd.read_sql_query(query,sqliteConnection)
        df = pd.DataFrame(sql_query)
        cursor.close()
    except sqlite3.Error as error:
        df=("Error while getting Audit Reviews", error)
        st.info(df)
    finally:
        if sqliteConnection:
            sqliteConnection.close()
            #message=("The SQLite connection is closed")
        
    return df

def add_comp_doc(title,remarks,file_ref,doc_type,comp_name):
    try:
        sqliteConnection = sqlite3.connect('autoaudit.db')
        cursor = sqliteConnection.cursor()
        
        currentime=datetime.now()
        sqlite_insert_with_param = """INSERT INTO Company_File
                          (Title,Remarks,File_Ref,Document_Type,Company,Created_by,Created_on) 
                          VALUES (?,?,?,?,?,?,?);"""
        data_tuple = (title,remarks,file_ref,doc_type,comp_name,st.session_state['User'],currentime)
        #st.info("Done2")
        cursor.execute(sqlite_insert_with_param, data_tuple)
        sqliteConnection.commit()
        cursor.close()
        st.info("Record Added...")
        message_verify=("Record Added...")
    except sqlite3.Error as error:
        message_verify=("Error while creating New Company", error)
        st.info(error)
        #st.info(comp_name)
    finally:
        if sqliteConnection:
            sqliteConnection.close()
            #message=("The SQLite connection is closed")
            
    return message_verify

def del_comp_doc(id):
    try:
        sqliteConnection = sqlite3.connect('autoaudit.db')
        cursor = sqliteConnection.cursor()
        
        #currentime=datetime.now()
        sqlite_insert_with_param = f"DELETE FROM Company_File WHERE id = {id}"
        #data_tuple = (title,remarks,file_ref,doc_type,comp_name,st.session_state['User'],currentime)
        #st.info("Done2")
        cursor.execute(sqlite_insert_with_param)
        sqliteConnection.commit()
        cursor.close()
        st.info("Record Deleted...")
        message_verify=("Record Deleted...")
    except sqlite3.Error as error:
        message_verify=("Error while creating New Company", error)
        st.info(error)
        #st.info(comp_name)
    finally:
        if sqliteConnection:
            sqliteConnection.close()
            #message=("The SQLite connection is closed")
            
    return message_verify

def modif_comp_doc(roid,title,remarks,file_ref,doc_type):
    try:
        sqliteConnection = sqlite3.connect('autoaudit.db')
        cursor = sqliteConnection.cursor()
        #update audit status
        if file_ref==None:
            query=f"""UPDATE Company_File  SET Title='{title}',Remarks ='{remarks}',Document_Type='{doc_type}'
                WHERE id={roid} """
        else:
            query=f"""UPDATE Company_File  SET Title='{title}',Remarks ='{remarks}', File_Ref='{file_ref}' , Document_Type='{doc_type}'
                WHERE id={roid} """
            
        #query=f"""UPDATE Company_File  SET Title='{title}',Remarks ='{remarks}', File_Ref='{file_ref}' , Document_Type='{doc_type}'
            #WHERE id={roid} """
        #query=f"UPDATE  SET Status ='Audited' WHERE `index` = {data_id}"
        #query=f"SELECT Review from Audit_AR where DataSetName='{DsName}' AND CompanyName='{comp_name}'"
        #st.write(query)
        cursor.execute(query)
        sqliteConnection.commit()
        cursor.close()
        auditstatus=("Record updated....")
        st.info(auditstatus)
    except sqlite3.Error as error:
        auditstatus=("Error while Updating Record", error)
        st.info(auditstatus)
    finally:
        if sqliteConnection:
            sqliteConnection.close()
            #message=("The SQLite connection is closed")
            
    return auditstatus

def get_audit_docs(auditid):
    try:
        sqliteConnection = sqlite3.connect('autoaudit.db')
        cursor = sqliteConnection.cursor()
        query=f"SELECT * from Audit_File where Audit_id='{auditid}'"
        sql_query=pd.read_sql_query(query,sqliteConnection)
        df = pd.DataFrame(sql_query)
        cursor.close()
    except sqlite3.Error as error:
        df=("Error while getting Audit Reviews", error)
        st.info(df)
    finally:
        if sqliteConnection:
            sqliteConnection.close()
            #message=("The SQLite connection is closed")
        
    return df

def add_audit_doc(title,remarks,file_ref,doc_type,audit_id):
    try:
        sqliteConnection = sqlite3.connect('autoaudit.db')
        cursor = sqliteConnection.cursor()
        
        currentime=datetime.now()
        sqlite_insert_with_param = """INSERT INTO Audit_File
                          (Title,Remarks,File_Ref,Document_Type,Audit_id,Created_by,Created_on) 
                          VALUES (?,?,?,?,?,?,?);"""
        data_tuple = (title,remarks,file_ref,doc_type,audit_id,st.session_state['User'],currentime)
        #st.info("Done2")
        cursor.execute(sqlite_insert_with_param, data_tuple)
        sqliteConnection.commit()
        cursor.close()
        st.info("Record Added...")
        message_verify=("Record Added...")
    except sqlite3.Error as error:
        message_verify=("Error while creating New Company", error)
        st.info(error)
        #st.info(comp_name)
    finally:
        if sqliteConnection:
            sqliteConnection.close()
            #message=("The SQLite connection is closed")
            
    return message_verify

def del_audit_doc(id):
    try:
        sqliteConnection = sqlite3.connect('autoaudit.db')
        cursor = sqliteConnection.cursor()
        
        #currentime=datetime.now()
        sqlite_insert_with_param = f"DELETE FROM Audit_File WHERE id = {id}"
        #data_tuple = (title,remarks,file_ref,doc_type,comp_name,st.session_state['User'],currentime)
        #st.info("Done2")
        cursor.execute(sqlite_insert_with_param)
        sqliteConnection.commit()
        cursor.close()
        st.info("Record Deleted...")
        message_verify=("Record Deleted...")
    except sqlite3.Error as error:
        message_verify=("Error while Deleting", error)
        st.info(error)
        #st.info(comp_name)
    finally:
        if sqliteConnection:
            sqliteConnection.close()
            #message=("The SQLite connection is closed")
            
    return message_verify

def modif_audit_doc(roid,title,remarks,file_ref,doc_type):
    try:
        sqliteConnection = sqlite3.connect('autoaudit.db')
        cursor = sqliteConnection.cursor()
        #update audit status
        if file_ref==None:
            query=f"""UPDATE Audit_File  SET Title='{title}',Remarks ='{remarks}',Document_Type='{doc_type}'
                WHERE id={roid} """
        else:
            query=f"""UPDATE Audit_File  SET Title='{title}',Remarks ='{remarks}', File_Ref='{file_ref}' , Document_Type='{doc_type}'
                WHERE id={roid} """
            
        #query=f"""UPDATE Company_File  SET Title='{title}',Remarks ='{remarks}', File_Ref='{file_ref}' , Document_Type='{doc_type}'
            #WHERE id={roid} """
        #query=f"UPDATE  SET Status ='Audited' WHERE `index` = {data_id}"
        #query=f"SELECT Review from Audit_AR where DataSetName='{DsName}' AND CompanyName='{comp_name}'"
        #st.write(query)
        cursor.execute(query)
        sqliteConnection.commit()
        cursor.close()
        auditstatus=("Record updated....")
        st.info(auditstatus)
    except sqlite3.Error as error:
        auditstatus=("Error while Updating Record", error)
        st.info(auditstatus)
    finally:
        if sqliteConnection:
            sqliteConnection.close()
            #message=("The SQLite connection is closed")
            
    return auditstatus

def get_audit_checklist(auditid):
    try:
        sqliteConnection = sqlite3.connect('autoaudit.db')
        cursor = sqliteConnection.cursor()
        query=f"SELECT id,Criteria,Risk_Weight,Risk_Level,Audit_Area,Heading,person_responsible,created_by,created_on,audit_id from Audit_Observations where Audit_id={auditid}"
        sql_query=pd.read_sql_query(query,sqliteConnection)
        df = pd.DataFrame(sql_query)
        cursor.close()
    except sqlite3.Error as error:
        df=("Error while getting Audit Checklist", error)
        st.info(df)
    finally:
        if sqliteConnection:
            sqliteConnection.close()
            #message=("The SQLite connection is closed")
        
    return df

def del_checklist(id):
    try:
        sqliteConnection = sqlite3.connect('autoaudit.db')
        cursor = sqliteConnection.cursor()
        
        #currentime=datetime.now()
        sqlite_insert_with_param = f"DELETE FROM Audit_Observations WHERE id = {id}"
        #data_tuple = (title,remarks,file_ref,doc_type,comp_name,st.session_state['User'],currentime)
        #st.info("Done2")
        cursor.execute(sqlite_insert_with_param)
        sqliteConnection.commit()
        cursor.close()
        st.info("Record Deleted...")
        message_verify=("Record Deleted...")
    except sqlite3.Error as error:
        message_verify=("Error while Deleting", error)
        st.info(error)
        #st.info(comp_name)
    finally:
        if sqliteConnection:
            sqliteConnection.close()
            #message=("The SQLite connection is closed")
            
    return message_verify

def add_audit_cheklist(criteria,Audit_area,heading,risk_weight,risk_category,person_responsible,auditid):
    try:
        sqliteConnection = sqlite3.connect('autoaudit.db')
        cursor = sqliteConnection.cursor()
        
        currentime=datetime.now()
        sqlite_insert_with_param = """INSERT INTO Audit_Observations
                          (Criteria,Risk_Weight,Risk_Level,Audit_Area,Heading,Person_Responsible,created_by,created_on,audit_id) 
                          VALUES (?,?,?,?,?,?,?,?,?);"""
        data_tuple = (criteria,risk_weight,risk_category,Audit_area,heading,person_responsible,st.session_state['User'],currentime,auditid)
        #st.info("Done2")
        cursor.execute(sqlite_insert_with_param, data_tuple)
        sqliteConnection.commit()
        cursor.close()
        st.info("Record Added...")
        message_verify=("Record Added...")
    except sqlite3.Error as error:
        message_verify=("Error while Adding Record", error)
        st.info(error)
        #st.info(comp_name)
    finally:
        if sqliteConnection:
            sqliteConnection.close()
            #message=("The SQLite connection is closed")
            
    return message_verify


def modify_audit_cheklist(roid,Criteria,Risk_Weight,Risk_Level,Audit_Area,Heading,Person_Responsible):
    try:
        sqliteConnection = sqlite3.connect('autoaudit.db')
        cursor = sqliteConnection.cursor()
        #update audit status
        query=f"""UPDATE Audit_Observations SET Criteria='{Criteria}', Risk_Weight ={Risk_Weight}, Risk_Level='{Risk_Level}' , Audit_Area='{Audit_Area}',
            Heading ='{Heading}', Person_Responsible='{Person_Responsible}' WHERE id={roid} """
            
        #query=f"""UPDATE Company_File  SET Title='{title}',Remarks ='{remarks}', File_Ref='{file_ref}' , Document_Type='{doc_type}'
            #WHERE id={roid} """
        #query=f"UPDATE  SET Status ='Audited' WHERE `index` = {data_id}"
        #query=f"SELECT Review from Audit_AR where DataSetName='{DsName}' AND CompanyName='{comp_name}'"
        #st.write(query)
        cursor.execute(query)
        sqliteConnection.commit()
        cursor.close()
        status=("Record updated....")
        st.info(status)
    except sqlite3.Error as error:
        status=("Error while Updating Record", error)
        st.info(status)
    finally:
        if sqliteConnection:
            sqliteConnection.close()
            #message=("The SQLite connection is closed")
            
    return status

def import_defalut_checklist(df):
    try:
        sqliteConnection = sqlite3.connect('autoaudit.db')
        cursor = sqliteConnection.cursor()
        df.to_sql("Audit_Observations",sqliteConnection,if_exists='append', index=False)
            
        sqliteConnection.commit()
        cursor.close()
        #vouching=("Audit Vouching added Successfully")
        vouching='Defalut CheckList Imported...You can Modify Later.'
        st.dataframe(df)
    except sqlite3.Error as error:
        vouching=("Error while Importing Checklist:-", error)
        st.info("Audit Criteria MUST be UNIQUE...if Existing Audit Criteria is in Defalut CheckList, Can not Import file.")
    finally:
        if sqliteConnection:
            sqliteConnection.close()
            #message=("The SQLite connection is closed")
            
    return vouching

def get_audit_observations(auditid):
    try:
        sqliteConnection = sqlite3.connect('autoaudit.db')
        cursor = sqliteConnection.cursor()
        query=f"""SELECT id,Criteria,Condition,Cause,Effect,Conclusion,Impact,Recomendation,
	                Annexure,Is_Adverse_Remark,Corrective_Action_Plan,DeadLine,Risk_Weight,Risk_Level,Audit_Area,Heading,person_responsible,Management_Comments,audit_id,Observation_by,Observation_on from Audit_Observations 
                    where Audit_id={auditid}"""
        sql_query=pd.read_sql_query(query,sqliteConnection)
        df = pd.DataFrame(sql_query)
        cursor.close()
    except sqlite3.Error as error:
        df=("Error while getting Audit Checklist", error)
        st.info(df)
    finally:
        if sqliteConnection:
            sqliteConnection.close()
            #message=("The SQLite connection is closed")
        
    return df

def modify_audit_observation(roid,Condition,Cause,Effect,Conclusion,Impact,Recomendation,Corrective_Action_Plan,Is_Adverse_Remark,DeadLine,file_name):
    try:
        sqliteConnection = sqlite3.connect('autoaudit.db')
        cursor = sqliteConnection.cursor()
        #update audit status
        currentime=datetime.now()
        if file_name==None:
            query=f"""UPDATE Audit_Observations  SET Condition='{Condition}',Cause ='{Cause}',Effect='{Effect}', 
                Conclusion='{Conclusion}',Impact='{Impact}',Impact='{Recomendation}',Corrective_Action_Plan='{Corrective_Action_Plan}' 
                ,Is_Adverse_Remark='{Is_Adverse_Remark}',DeadLine='{DeadLine}',Observation_by='{st.session_state['User']}', 
                Observation_on='{currentime}' WHERE id={roid} """
        else:
            query=f"""UPDATE Audit_Observations  SET Condition='{Condition}',Cause ='{Cause}', Effect='{Effect}' , 
                Conclusion='{Conclusion}',Impact='{Impact}',Impact='{Recomendation}',Corrective_Action_Plan='{Corrective_Action_Plan}' 
                ,Is_Adverse_Remark='{Is_Adverse_Remark}',DeadLine='{DeadLine}',Observation_by='{st.session_state['User']}',
                Observation_on='{currentime}',Annexure='{file_name}' WHERE id={roid} """
        
        cursor.execute(query)
        sqliteConnection.commit()
        cursor.close()
        auditstatus=("Record updated....")
        st.info(auditstatus)
    except sqlite3.Error as error:
        auditstatus=("Error while Updating Record", error)
        st.info(auditstatus)
    finally:
        if sqliteConnection:
            sqliteConnection.close()
            #message=("The SQLite connection is closed")
            
    return auditstatus

def get_Audit_summ(auditid):
    try:
        sqliteConnection = sqlite3.connect('autoaudit.db')
        cursor = sqliteConnection.cursor()
        query=f"""SELECT * from Audit_Summary where Audit_id={auditid}"""
        sql_query=pd.read_sql_query(query,sqliteConnection)
        df = pd.DataFrame(sql_query)
        cursor.close()
    except sqlite3.Error as error:
        df=("Error while getting Audit Summary", error)
        st.info(df)
    finally:
        if sqliteConnection:
            sqliteConnection.close()
            #message=("The SQLite connection is closed")
        
    return df

def add_audit_summ(auditid,Observation,risk_weight,risk_category,Impact,
                            Area,Need_for_Management_Intervention):
    try:
        sqliteConnection = sqlite3.connect('autoaudit.db')
        cursor = sqliteConnection.cursor()
        
        currentime=datetime.now()
        sqlite_insert_with_param = """INSERT INTO Audit_Summary
                          (Observation,Risk_Weight,Risk_Level,Impact,Area,Need_for_Management_Intervention,Audit_id,Created_by,Created_on) 
                          VALUES (?,?,?,?,?,?,?,?,?);"""
        data_tuple = (Observation,risk_weight,risk_category,Impact,Area,Need_for_Management_Intervention,auditid,st.session_state['User'],currentime)
        #st.info("Done2")
        cursor.execute(sqlite_insert_with_param, data_tuple)
        sqliteConnection.commit()
        cursor.close()
        st.info("Record Added...")
        message_verify=("Record Added...")
    except sqlite3.Error as error:
        message_verify=("Error while Adding Record", error)
        st.info(error)
        #st.info(comp_name)
    finally:
        if sqliteConnection:
            sqliteConnection.close()
            #message=("The SQLite connection is closed")
            
    return message_verify

def modify_audit_summ(roid,Observation,Impact,Area,Need_for_Management_Intervention,risk_weight,risk_category):
    try:
        sqliteConnection = sqlite3.connect('autoaudit.db')
        cursor = sqliteConnection.cursor()
        #update audit status
        query=f"""UPDATE Audit_Summary SET Observation='{Observation}', Impact ='{Impact}', Area='{Area}' , Need_for_Management_Intervention='{Need_for_Management_Intervention}',
            Risk_Weight ={risk_weight}, Risk_Level='{risk_category}' WHERE id={roid} """
         
        cursor.execute(query)
        sqliteConnection.commit()
        cursor.close()
        status=("Record updated....")
        st.info(status)
    except sqlite3.Error as error:
        status=("Error while Updating Record", error)
        st.info(status)
    finally:
        if sqliteConnection:
            sqliteConnection.close()
            #message=("The SQLite connection is closed")
            
    return status

def del_audit_sum(id):
    try:
        sqliteConnection = sqlite3.connect('autoaudit.db')
        cursor = sqliteConnection.cursor()
        
        #currentime=datetime.now()
        sqlite_insert_with_param = f"DELETE FROM Audit_Summary WHERE id = {id}"
        #data_tuple = (title,remarks,file_ref,doc_type,comp_name,st.session_state['User'],currentime)
        #st.info("Done2")
        cursor.execute(sqlite_insert_with_param)
        sqliteConnection.commit()
        cursor.close()
        st.info("Record Deleted...")
        message_verify=("Record Deleted...")
    except sqlite3.Error as error:
        message_verify=("Error while Deleting", error)
        st.info(error)
        #st.info(comp_name)
    finally:
        if sqliteConnection:
            sqliteConnection.close()
            #message=("The SQLite connection is closed")
            
    return message_verify

def get_pending_obser(auditid):   
    try:
        sqliteConnection = sqlite3.connect('autoaudit.db')
        cursor = sqliteConnection.cursor()
        query=f"""SELECT id,Criteria,Condition,Cause,Effect,Conclusion,Impact,Recomendation,
	                Annexure,Is_Adverse_Remark,Corrective_Action_Plan,DeadLine,Risk_Weight,Risk_Level,Audit_Area,Heading,person_responsible,Management_Comments,audit_id,Observation_by,Observation_on from Audit_Observations 
                    where Audit_id={auditid} and Compliance_Status='Open'"""
        sql_query=pd.read_sql_query(query,sqliteConnection)
        df = pd.DataFrame(sql_query)
        cursor.close()
    except sqlite3.Error as error:
        df=("Error while getting Audit Observations", error)
        st.info(df)
    finally:
        if sqliteConnection:
            sqliteConnection.close()
            #message=("The SQLite connection is closed")
        
    return df

def get_pending_advere_obser(auditid):   
    try:
        sqliteConnection = sqlite3.connect('autoaudit.db')
        cursor = sqliteConnection.cursor()
        query=f"""SELECT id,Criteria,Condition,Cause,Effect,Conclusion,Impact,Recomendation,
	                Annexure,Is_Adverse_Remark,Corrective_Action_Plan,DeadLine,Risk_Weight,Risk_Level,Audit_Area,Heading,person_responsible,Management_Comments,audit_id,Observation_by,Observation_on from Audit_Observations 
                    where Audit_id={auditid} and Compliance_Status='Open' and Is_Adverse_Remark = 'Yes' """
        sql_query=pd.read_sql_query(query,sqliteConnection)
        df = pd.DataFrame(sql_query)
        cursor.close()
    except sqlite3.Error as error:
        df=("Error while getting Audit Observations", error)
        st.info(df)
    finally:
        if sqliteConnection:
            sqliteConnection.close()
            #message=("The SQLite connection is closed")
        
    return df
     
def update_mgt_comm(id,reply):
    try:
        sqliteConnection = sqlite3.connect('autoaudit.db')
        cursor = sqliteConnection.cursor()
        #update audit status
        query=f"UPDATE Audit_Observations SET Management_Comments ='{reply}' WHERE id = {id}"
        #query=f"SELECT Review from Audit_AR where DataSetName='{DsName}' AND CompanyName='{comp_name}'"
        #st.write(query)
        cursor.execute(query)
        sqliteConnection.commit()
        cursor.close()
        updatereply=("Management_Comments updated....")
    except sqlite3.Error as error:
        updatereply=("Error while Updating Query Status", error)
    finally:
        if sqliteConnection:
            sqliteConnection.close()
            #message=("The SQLite connection is closed")
            
    return updatereply

def get_pending_Corrective(auditid):
    try:
        sqliteConnection = sqlite3.connect('autoaudit.db')
        cursor = sqliteConnection.cursor()
        query=f"""SELECT id,Criteria,Condition,Cause,Effect,Conclusion,Impact,Recomendation,
	                Annexure,Is_Adverse_Remark,Corrective_Action_Plan,DeadLine,Risk_Weight,Risk_Level,Audit_Area,Heading,person_responsible,
                    Management_Comments,Action_Remarks,audit_id,Observation_by,Observation_on from Audit_Observations 
                    where Audit_id={auditid} and Compliance_Status='Open'"""
        sql_query=pd.read_sql_query(query,sqliteConnection)
        df = pd.DataFrame(sql_query)
        cursor.close()
    except sqlite3.Error as error:
        df=("Error while getting Audit Observations", error)
        st.info(df)
    finally:
        if sqliteConnection:
            sqliteConnection.close()
            #message=("The SQLite connection is closed")
        
    return df
    
def update_corre_action(id,reply):
    try:
        sqliteConnection = sqlite3.connect('autoaudit.db')
        cursor = sqliteConnection.cursor()
        #update audit status
        query=f"UPDATE Audit_Observations SET Action_Remarks ='{reply}' WHERE id = {id}"
        #query=f"SELECT Review from Audit_AR where DataSetName='{DsName}' AND CompanyName='{comp_name}'"
        #st.write(query)
        cursor.execute(query)
        sqliteConnection.commit()
        cursor.close()
        updatereply=("Action_Remarks updated....")
    except sqlite3.Error as error:
        updatereply=("Error while Updating Query Status", error)
    finally:
        if sqliteConnection:
            sqliteConnection.close()
            #message=("The SQLite connection is closed")
            
    return updatereply

def get_pending_Compliance(auditid): 
    try:
        sqliteConnection = sqlite3.connect('autoaudit.db')
        cursor = sqliteConnection.cursor()
        query=f"""SELECT id,Criteria,Condition,Cause,Effect,Conclusion,Impact,Recomendation,
	                Annexure,Is_Adverse_Remark,Corrective_Action_Plan,DeadLine,Risk_Weight,Risk_Level,Audit_Area,Heading,person_responsible,
                    Management_Comments,Action_Remarks,Compliance_Status,Compliance_Remarks,audit_id,Observation_by,Observation_on from Audit_Observations 
                    where Audit_id={auditid} and Compliance_Status='Open'"""
        sql_query=pd.read_sql_query(query,sqliteConnection)
        df = pd.DataFrame(sql_query)
        cursor.close()
    except sqlite3.Error as error:
        df=("Error while getting Audit Observations", error)
        st.info(df)
    finally:
        if sqliteConnection:
            sqliteConnection.close()
            #message=("The SQLite connection is closed")
        
    return df
       
def update_compliance_remarks(id,reply,status):
    try:
        sqliteConnection = sqlite3.connect('autoaudit.db')
        cursor = sqliteConnection.cursor()
        #update audit status
        query=f"UPDATE Audit_Observations SET Compliance_Remarks ='{reply}', Compliance_Status='{status}' WHERE id = {id}"
        #query=f"SELECT Review from Audit_AR where DataSetName='{DsName}' AND CompanyName='{comp_name}'"
        #st.write(query)
        cursor.execute(query)
        sqliteConnection.commit()
        cursor.close()
        updatereply=("Compliance_Remarks updated....")
    except sqlite3.Error as error:
        updatereply=("Error while Updating Query Status", error)
    finally:
        if sqliteConnection:
            sqliteConnection.close()
            #message=("The SQLite connection is closed")
            
    return updatereply

def closed_audit(auditid):
    try:
        sqliteConnection = sqlite3.connect('autoaudit.db')
        cursor = sqliteConnection.cursor()
        #update audit status
        query=f"UPDATE Audit SET Status ='Closed' WHERE id = {auditid}"
        #query=f"SELECT Review from Audit_AR where DataSetName='{DsName}' AND CompanyName='{comp_name}'"
        #st.write(query)
        cursor.execute(query)
        sqliteConnection.commit()
        cursor.close()
        updatereply=("Audit Closed....")
    except sqlite3.Error as error:
        updatereply=("Error while Updating Status", error)
    finally:
        if sqliteConnection:
            sqliteConnection.close()
            #message=("The SQLite connection is closed")
            
    return updatereply

    