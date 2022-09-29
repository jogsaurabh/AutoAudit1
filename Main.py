import streamlit as st
import pandas as pd
import numpy as np
from functions import get_user_rights,get_active_users,get_audit,get_comp_by_user,creat_audit
from functions import create_user,check_login,assign_user_rights,create_company,get_company_names
#import sqlite3
from PIL import Image
image = Image.open('autoaudit_t.png')
st.set_page_config(page_title="AutoAudit", page_icon=":white_check_mark:", layout="wide")
#st.title(":white_check_mark: AutoAudit")
st.image(image,width=250)
st.markdown("""---""")
#get list of companies

#st.write(company_list.__str__())
headerSection = st.container()
mainSection = st.container()
loginSection = st.container()
createcompanysection=st.container()
logOutSection = st.container()
def login(userName: str, password: str) -> bool:
        #this checks login & password is correct
    if (userName is None):
        return False
    else:
        if (password is None):
            return False
        else:
            if userName=="abc" and password=='abc':
                return True
            else:
                return False
 
#def create_company_show():
    #with createcompanysection:
        #st.title("Create New Company")
    
    
    #st.write(comp_name)
    #st.info(reply)

def assign_user_rights_show():
    st.title("Assign User")
    
def show_main_page():
    company_list=get_company_names()
    with mainSection:
        #st.success(f"{st.session_state['Company']}_{st.session_state['AuditID']}_filename")
        st.write(f"User:-{st.session_state['User']}",f"  | Company:-{st.session_state['Company']}",
                 f"  | Audit:-{st.session_state['Audit']}",f"  | Role:-{st.session_state['Role']}")
        
        with st.sidebar.markdown("# Masters "):
            master_options = st.radio("Select",('Create Company','Assign User Rights','Add New Audit'))
        #st.sidebar.button("Assign User Rights",key="ba1",on_click=assign_user_rights_show)
        if master_options=="Create Company":
            #st.success("""For First Time Login- """)
            with st.form("Create New Company",clear_on_submit=True):
                        st.title("Create New Company")
                        comp_name = st.text_input (label="",value="",placeholder="Enter company Name",key="comp_name1")
                        com_address = st.text_input (label="", value="",placeholder="Enter company Address",key="com_address1")
                        com_email = st.text_input (label="", value="", placeholder="Enter email",key="com_email1")
                        com_mobile = st.number_input("Mobile No",min_value=1111111111,max_value=9999999999,key="com_mobile1")
                        com_person = st.text_input (label="", value="", placeholder="Enter Contact Person",key="com_person1")
                        
                        #st.write(comp_name)
                        #st.button("Submit",on_click=create_company, args= (comp_name, com_address,com_email,com_mobile,com_person))
                        #st.button("Submit",key="sub11"):
                        if st.form_submit_button("Submit"):
                            create_company(comp_name, com_address,com_email,com_mobile,com_person)
                            
        elif master_options=="Assign User Rights":
            showrights=st.button("Show User Rights",key="seur")
            if showrights:
                
                userrights_df=get_user_rights()
                st.title("Existing User Rights")
                st.dataframe(userrights_df)
            
            users=get_active_users()
            if company_list.empty:
                    st.info('You can assign rights for Company created by you.')
                    
            else:
                    with st.form("Assign User Rights",clear_on_submit=True):
                        
                        st.title("Assign User Rights")
                        
                        company_name=st.selectbox("Select Company",company_list,key="company_name")
                                #users=get_unassigned_users(comapname)
                        user=st.selectbox("Select User",users,key="usersb")
                        role=st.selectbox("Select Role",("Manager","Auditor","Auditee"),key="usersb1")
                    
                    
                        submitb = st.form_submit_button("Submit")
                        if submitb:
                            assign_user_rights(user,company_name,role)
                            #st.write("OK")
                                #assign_user_rights(user,company_name,role)
        else:
            if st.session_state['User']=='admin':
                companies=get_company_names()
            else:
                
                companies=get_comp_by_user()
            if companies.empty:
                st.info(f"Only Users with Manager Role can add Audit...\n You are not Manager for any Company.")
            else:
                with st.form("Add New Audit",clear_on_submit=True):
                        st.title("Add New Audit")
                        Audit_Name = st.text_input (label="Enter Audit Name",value="",placeholder="-Max lenght 6",key="Audit_Name1")
                        #companies=get_comp_by_user()
                        Company_name = st.selectbox("Select Company",companies,key="Company_name1")
                        Period = st.text_input (label="Enter Period", value="", placeholder="Audit Period",key="Period1")
                        Remarks = st.text_input (label="Enter Remarks", value="", placeholder="Remarks",key="Remarks1")
                        #st.write(comp_name)
                        
                        #st.button("Submit",on_click=create_company, args= (comp_name, com_address,com_email,com_mobile,com_person))
                        #st.button("Submit",key="sub11"):
                        
                        if st.form_submit_button("Submit"):
                            if Audit_Name:
                                    creat_audit(Audit_Name,Company_name,Period,Remarks)
                            else:
                                st.success("Audit Name is Required")
    
def LoggedOut_Clicked():
    st.session_state['loggedIn'] = False
    loginuser=""
    
def show_logout_page():
    loginSection.empty()
    with logOutSection:
        st.sidebar.button ("Log Out", key="logout", on_click=LoggedOut_Clicked)


def LoggedIn_Clicked(userName, password):
    if login(userName, password):
        st.session_state['loggedIn'] = True
        st.session_state['username']=userName
        loginuser=userName
    else:
        st.session_state['loggedIn'] = False
        st.info("Invalid user name or password")

def Register_Clicked(userid, password,designation,displayname):
    createuser=create_user(displayname,userid,password,designation)
    st.info(createuser)
    #show_login_page()
    
def show_login_page():
    with loginSection:
        tab1,tab2 =st.tabs(["   Existing Users  ","   New Users   "])
        with tab1:
            
            if st.session_state['loggedIn'] == False:
                #st.session_state['username'] = ''
                st.title("Login") 
                userName = st.text_input (label="", value="", placeholder="Enter your user name",key="k1")
                password = st.text_input (label="", value="",placeholder="Enter password", type="password",key="k2")
                #get Companies for user
                rights=get_user_rights()
                mask = rights['user'] == userName
                comp_name= rights[mask]
                #comp_name=comp_name['company_name']
                compname=st.selectbox("Select Company",comp_name['company_name'])
                mask1=comp_name['company_name']==compname
                roleds=comp_name[mask1]
                if roleds.size !=0:
                    role=roleds['role'].values[0]
                else:
                    role=""
                #st.write(compname)
                #st.write(comp_name['company_name'])
                #get Audit for company
                audits=get_audit(compname)
                audit=st.selectbox("Select Audit Name",audits,key="auit_name")
                #st.write(audit.value[1])
                if audit:
                    st.button ("Login", on_click=check_login, args= (userName, password,compname,role,audit))
                
        with tab2:
            with st.form("New User",clear_on_submit=True):
                
                st.title("Register")
                userid = st.text_input (label="", value="", placeholder="Enter your user ID",key="k5")
                password = st.text_input (label="", value="",placeholder="Set password", type="password",key="k6")
                designation = st.text_input (label="", value="", placeholder="Enter your Designation",key="k3")
                displayname = st.text_input (label="", value="", placeholder="Enter your Display Name",key="k4")
                st.form_submit_button("Submit",on_click=Register_Clicked, args= (userid, password,designation,displayname))
                #st.button ("Register", on_click=Register_Clicked, args= (userid, password,designation,displayname))

def show_auditee():
    st.warning(f"You Have Logged In as {st.session_state['Role']}...You have no access to this Menu")


with headerSection:
    if 'User' not in st.session_state:
        st.session_state['User'] = ""
    
    if 'Company' not in st.session_state:
        st.session_state['Company'] = ""
    
    if 'Role' not in st.session_state:
        st.session_state['Role'] = ""
    
    if 'Audit' not in st.session_state:
        st.session_state['Audit'] = ""
    
    if 'AuditID' not in st.session_state:
        st.session_state['AuditID'] = ""
    
    if 'loggedIn' not in st.session_state:
        st.session_state['loggedIn'] = False
        show_login_page()
                
    else:
        if st.session_state['loggedIn']:
            show_logout_page()   
            if st.session_state['Role'] == "Auditee" or st.session_state['Role'] == "Auditor":
                    show_auditee()
            else:
                    show_main_page()   
        else:
            show_login_page()
                       
                