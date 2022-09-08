#from logging import PlaceHolder
import streamlit as st
import pandas as pd
import numpy as np
#from main import show_login_page,LoggedOut_Clicked
from functions import get_user_rights,get_active_users,add_datato_ds,get_verification,get_audit
from functions import create_user,check_login,assign_user_rights,create_company,get_company_names
from functions import create_dataset,add_verification_criteria,get_dsname,get_entire_dataset,get_auditee_comp
import sqlite3
from PIL import Image
image = Image.open('autoaudit_t.png')
st.set_page_config(page_title="AutoAudit", page_icon=":white_check_mark:", layout="wide")
#st.title(":white_check_mark: AutoAudit")
st.image(image,width=250)
st.markdown("""---""")
masters=st.container()
#from st_aggrid import AgGrid
headerSection = st.container()
#masterSection = st.container()
loginSection = st.container()
logOutSection = st.container()

def show_masters():
    comp_name=st.session_state['Company']
    with masters:
        st.write(f"User:-{st.session_state['User']}",f"  | Company:-{st.session_state['Company']}",
                 f"  | Audit:-{st.session_state['Audit']}",f"  | Role:-{st.session_state['Role']}")
        
        st.title("Masters")
        with st.sidebar.markdown("# Masters "):
            master_options = st.radio(
            'Masters- Dataset',
            ('Add New Data Set', 'Add Records to Data Set','Add Check List','Compare with Audited Dataset'))            
        if master_options=='Add New Data Set':
            
            st.title("Add New Data Set")
            st.info(f"1) Check that - First Row contains column Headings..\n2) File is of - .xlsx type\n3) File contains only 1 sheet")
            #with st.form("New Dataset",clear_on_submit=True):
            #st.warning("Check ...First Column is Primary Key / Unique")
            auditee=get_auditee_comp()
            if auditee.empty:
                st.error(f"No Auditee assigned to Current Company...\n Assign Atleast 1 user with Auditee Role")
                
            else:
                table_name=st.text_input("Enter Name of Data Set",key="tablename1")
                person_responsible=st.selectbox("Select Auditee, who will answer Queries",auditee,key="sbperson_responsible")
                uploaded_file = st.file_uploader("Upload a xlsx file",type='xlsx',key="uploadfile1")
                if uploaded_file is not None:
                        st.write(uploaded_file.name)
                        filename=uploaded_file.name
                        dataframe = pd.read_excel(uploaded_file,)
                        st.dataframe(dataframe)
                        if st.button("Create Data Set",key="b1"):
                            if table_name:
                                message=create_dataset(dataframe,table_name,comp_name,person_responsible)
                                st.success(message) 
                                #masters.empty()       
                            else:
                                st.error("Please enter Data Set Name")
                                #masters.empty()
                                
        elif master_options=='Add Records to Data Set':
                st.title("Add data to Existing Data Set")
                st.warning("Check that all colums are Exactly same as per Existing Data Set, before uploading.")
                #get list of ds_name for current company
                ds_names=get_dsname(int(st.session_state['AuditID']))
                if ds_names.empty:
                    st.error(f"No Data Sets for Current Company...\n First Add Data Set in current Company.")
                else:
                    col1, col2 =st.columns(2)
                    with col1:
                        st.info("Select Data Set to add Records...")
                        ds_name=st.selectbox("Select Data Set Name...",ds_names,key="sb0")
                        st.write("Current Data Set")
                        dsname=f"{comp_name}_{st.session_state['AuditID']}_{ds_name}"
                        df=get_entire_dataset(dsname)
                        st.dataframe(df)
                    with col2:
                        st.info("Check Data to Add to Current Data Set")
                        uploaded_file = st.file_uploader("Upload a xlsx file",type='xlsx',key="1uploadfile1")
                        
                    
                        if uploaded_file is not None:
                                st.write("Data to Add ")
                                #filename=uploaded_file.name
                                dataframe = pd.read_excel(uploaded_file,)
                                #dataframe['index'] = range(880, 880+len(dataframe))
                                dfmax=df['index'].max()
                                dataframe.insert(0,"index",range(dfmax+1, dfmax+1 + len(dataframe)))
                                st.dataframe(dataframe)
                                
                                if st.button("Append to Data Set",key="b11"):
                                    message=add_datato_ds(dataframe,ds_name,comp_name)
                                    st.success(message)
                
                
        elif master_options=='Add Check List':
                st.title("Add Verification Check List for Data Set")
                #get list of ds_name for current company
                ds_names=get_dsname(int(st.session_state['AuditID']))
                ds_name=st.selectbox("Select Data Set Name...",ds_names,key="sb1")
                if st.button("View Current check list",key="cc1"):
                    veri_df=get_verification(ds_name,int(st.session_state['AuditID']))
                    st.dataframe(veri_df)
                #Chek_List=pd.DataFrame()
                with st.form("Verification Criteria",clear_on_submit=True):
                    
                    # Every form must have a submit button.
                    #veri_df=get_verification(ds_name,comp_name)
                    
                    #st.dataframe(veri_df)
                    
                    Crtiteria=st.text_area("Enter Verification Criteria")
                    submitted = st.form_submit_button("Submit")
                    if submitted:
                        #add above to database
                        Chek_List=add_verification_criteria(Crtiteria,ds_name,comp_name)
                        st.header("Verification Criteria")
                        
                        veri_df=get_verification(ds_name,int(st.session_state['AuditID']))
                        st.dataframe(veri_df)
                        
                                    
                
                #st.dataframe(Chek_List,width=1000)
        else:
                st.title("Compare Audited Dataset with Current Version of Dataset")
                st.info("Upload Current Version of Dataset..")
                st.warning("Check ...Data Structure is Excatly same, with same colum names")
                ds_names=get_dsname(int(st.session_state['AuditID']))
                ds=st.selectbox("Select Data Set Name...",ds_names,key="sb2")
                #ds_name=ds[0]
                ds_name=f"{comp_name}_{st.session_state['AuditID']}_{ds}"
                st.write(ds_name)
                uploaded_file = st.file_uploader("Upload a xlsx file",type='xlsx',key="uploadfile2")

                if uploaded_file is not None:
                    st.write(uploaded_file.name)
                    #filename=uploaded_file.name
                    dataframe_new = pd.read_excel(uploaded_file)
                    #dataframe_new=dataframe_new.index.name = 'id'
                    #get audited DF
                    df=get_entire_dataset(ds_name)
                    #df.drop(columns=['Status','index','Sampled'],inplace=True)
                    df.drop(columns=['Status','index','Sampled'],inplace=True)
                    #df.sort_index(inplace=True)
                    st.write("Audited Dataset")
                    st.dataframe(df)
                    st.write("Current Version of Dataset")
                    st.dataframe(dataframe_new)
                    dfcol1=df.columns.tolist()
                    dfcol2=dataframe_new.columns.tolist()
                    #indexkey=df.columns[0]
                    #indexkey2=dataframe_new.columns[0]
                    if dfcol1==dfcol2:                       
                        if st.button("Compare Data Set",key="b2"):
                            df_all = pd.concat([df, dataframe_new],axis='columns', keys=['Audited', 'Current'])
                            #df_all = pd.concat([df.set_index(indexkey), dataframe_new.set_index(indexkey)], 
                                    #axis='columns', keys=['Audited', 'Current'])
                            #st.dataframe(df_all)
                            df_final = df_all.swaplevel(axis='columns')[df.columns[0:]]
                            df_final.fillna('No Value',inplace=True)
                            df_final=df_final.astype(str)
                            def highlight_diff(data, color='yellow'):
                                attr = 'background-color: {}'.format(color)
                                other = data.xs('Audited', axis='columns', level=-1)
                                return pd.DataFrame(np.where(data.ne(other, level=0), attr, ''),index=data.index, columns=data.columns)
                                
                            st.dataframe(df_final.reset_index(drop=True).style.apply(highlight_diff, axis=None))
                            csv=df_final.to_csv().encode('utf-8')
                            st.download_button("Download csv file",csv,f"com_{ds_name}.csv")
                    else:
                        st.warning("Mismatch in Colums of two Datasets...please upload Data set with same structure.")
                                            


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
 

#def show_main_page():
    #with mainSection:
        #st.write(f"User:-{st.session_state['username']}")
        
 
def LoggedOut_Clicked():
    st.session_state['loggedIn'] = False
    loginuser=""
    
def show_logout_page():
    loginSection.empty()
    with logOutSection:
        st.sidebar.button ("Log Out", key="logout", on_click=LoggedOut_Clicked)


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
    st.warning("You Have Logged In as Auditee...You have no access to this Menu")



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
        #st.title("Login")
    else:
        if st.session_state['loggedIn']:
            show_logout_page() 
            if st.session_state['Role'] == "Auditee":
                    show_auditee()
            else:
                    show_masters()     
            
        else:
            #st.title("Login")
            show_login_page()

    
    