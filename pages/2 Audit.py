#from cgitb import enable
#from distutils.command.build import build
#from sys import audit
#from turtle import onclick
from matplotlib.cbook import report_memory
import streamlit as st
#from streamlit import caching
from datetime import datetime
from functions import get_user_rights,get_active_users,add_datato_ds,get_verification,get_audit,add_audit_verification
from functions import create_user,check_login,get_dsname_personresponsible,assign_user_rights,create_company,get_company_names,get_pending_queries
from functions import create_dataset,add_verification_criteria,get_dsname,get_entire_dataset,get_auditee_comp
from functions import get_dataset,add_analytical_review,insert_vouching,update_audit_status,get_ar_for_ds,add_query_reply
import pandas as pd
from PIL import Image
image = Image.open('autoaudit_t.png')
from st_aggrid import AgGrid,DataReturnMode, GridUpdateMode, GridOptionsBuilder, JsCode, grid_options_builder
#from pandas_profiling import ProfileReport
import pandas_profiling
from streamlit_pandas_profiling import st_profile_report
import sqlite3
st.set_page_config(page_title="AutoAudit", page_icon=":white_check_mark:", layout="wide")
#st.title(":white_check_mark: AutoAudit")
st.image(image,width=250)
st.markdown("""---""")
audit_container=st.container()
updatecontainer=st.container()
#st.write(f"User:-{st.session_state['username']}")
#comp_name=st.session_state['Company']

       
            
def show_audit():
    
    with audit_container:
        st.write(f"User:-{st.session_state['User']}",f"  | Company:-{st.session_state['Company']}",
                 f"  | Audit:-{st.session_state['Audit']}",f"  | Role:-{st.session_state['Role']}")
        
        st.title("Audit")
        with st.sidebar.markdown("# Audit"):
            optionsdf=get_dsname(int(st.session_state['AuditID']))
            #add blank row at begining of list
            optionsdf.loc[-1]=['---']
            optionsdf.index=optionsdf.index+1
            optionsdf.sort_index(inplace=True)
            d_sname=st.selectbox("Select Data Set to Audit",optionsdf,key="selectdsname")
            ds_name=f"{st.session_state['Company']}_{(st.session_state['AuditID'])}_{d_sname}"
            #select dataset 
                      
        
            
        if d_sname=="---":
            st.warning("Select Data Set to Audit")
        else:
            df=get_dataset(ds_name)
            df.drop(['Status', 'Sampled'], axis=1,inplace=True)
            tab1,tab2 =st.tabs(["   Vouching & Verification  ","   Analytical Review   "])
            with tab1:
                st.header(d_sname)
                #st.dataframe(df)
                    #builds a gridOptions dictionary using a GridOptionsBuilder instance.
                builder = GridOptionsBuilder.from_dataframe(df)
                builder.configure_pagination(enabled=True,paginationAutoPageSize=False,paginationPageSize=10)
                builder.configure_selection(selection_mode="single",use_checkbox=True)
                    #builder.configure_default_column(editable=True)
                go = builder.build()
                    #uses the gridOptions dictionary to configure AgGrid behavior.
                grid_response=AgGrid(df, gridOptions=go,update_mode= (GridUpdateMode.SELECTION_CHANGED|GridUpdateMode.MODEL_CHANGED))
                    #selelcted row to show in audit AGGrid
                selected = grid_response['selected_rows']
                with st.form("Auditing",clear_on_submit=True):
                                            
                    
                    #selected = grid_response['data']
                    selected_df = pd.DataFrame(selected)
                    #rowinedx if added delet
                    if '_selectedRowNodeInfo' in selected_df.columns:
                        selected_df.drop(['_selectedRowNodeInfo'], axis=1,inplace=True)
                        
                    #show Vouching AGGrid
                    builder_Audit=GridOptionsBuilder.from_dataframe(selected_df)
                    builder_Audit.configure_default_column(editable=True)
                    go_audit = builder_Audit.build()
                    st.subheader("Vouching...If values are wrong...Double click to enter correct value.")
                    #audited=AgGrid(selected_df, gridOptions=go_audit,update_mode= GridUpdateMode.VALUE_CHANGED,height = 80)
                    audited=AgGrid(selected_df, gridOptions=go_audit,update_mode= GridUpdateMode.VALUE_CHANGED,height = 80)
                    #st.text(audited["data"])
                    audited_data=audited['data']
                    #aud_df=pd.DataFrame(audited_data)
                    #Verification
                    st.subheader("Verification...Check Verification if YES else keep Unchecked.")
                    df_verif=get_verification(d_sname,int(st.session_state['AuditID']))
                    df_verif["Remarks"]=''
                    builder_verif=GridOptionsBuilder.from_dataframe(df_verif)
                    builder_verif.configure_selection(selection_mode="multiple",use_checkbox=True)
                    builder_verif.configure_columns((['Remarks']),editable=True)
                    go_verif=builder_verif.build()
                    verif=AgGrid(df_verif, gridOptions=go_verif,update_mode=(GridUpdateMode.VALUE_CHANGED|GridUpdateMode.SELECTION_CHANGED))
                    #st.write(verif)
                    all_verif=verif["data"]
                    df_all_verif=pd.DataFrame(all_verif)
                    #st.dataframe(df_all_verif)
                    if '_selectedRowNodeInfo' in df_all_verif.columns:
                        df_all_verif.drop(['_selectedRowNodeInfo'], axis=1,inplace=True)
                    #get DF for selected
                    selected_verif=verif["selected_rows"]
                    df_selected_ver=pd.DataFrame(selected_verif)
                    #st.dataframe(df_selected_ver)
                    if '_selectedRowNodeInfo' in df_selected_ver.columns:
                        df_selected_ver.drop(['_selectedRowNodeInfo'], axis=1,inplace=True)
                    
                    #get df for not selected
                    df_unselected_ver=pd.concat([df_all_verif,df_selected_ver]).drop_duplicates(keep=False).reset_index(drop=True)
                    #st.dataframe(df_all_verif)
                    #st.dataframe(df_unselected_ver)
                    #add colums to selected    
                    df_selected_ver.rename(columns={'Verification_Criteria':'Verification'},inplace=True)
                    df_selected_ver['DataSetName']=d_sname
                    df_selected_ver['CompanyName']=st.session_state['Company']
                    df_selected_ver['Audit_Verification']="Yes"
                    
                        
                    #add colums to Unselected    
                    df_unselected_ver.rename(columns={'Verification_Criteria':'Verification'},inplace=True)
                    df_unselected_ver['DataSetName']=d_sname
                    df_unselected_ver['CompanyName']=st.session_state['Company']
                    df_unselected_ver['Audit_Verification']="No"  
                    if 'rowIndex' in df_unselected_ver.columns:
                        df_unselected_ver.drop(['rowIndex'], axis=1,inplace=True)
                        
                    #st.dataframe(df_selected_ver)   
                    #st.dataframe(df_unselected_ver)  
                    Submit_audit= st.form_submit_button("Submit")
                    if Submit_audit:
                        if  audited_data.empty:
                            st.error("Select row to Audit")
                        else:
                            #add  in database
                            data_id=int(audited_data.iloc[0,0])
                            for col in audited_data.columns:
                                if audited_data[col].iloc[0] != selected_df[col].iloc[0]:
                                    #st.write(audited_data[col].iloc[0],col)
                                    audit_value=audited_data[col].iloc[0]
                                    accountin_value=selected_df[col].iloc[0]
                                    remarks=f"{col} as per Records is- {accountin_value} ; but as per Audit is- {audit_value} ."
                                    #st.write(data_id,col,str(audit_value),ds_name,comp_name)
                                    vouching=insert_vouching(data_id,col,str(audit_value),remarks,d_sname,st.session_state['Company'])
                                    st.info(vouching)
                                    
                            currentime=datetime.now()
                            #for verification =yes insert in Audit_queries
                            df_selected_ver['Data_Id']=data_id
                            df_selected_ver['Audit_Verification']="Yes"
                            df_selected_ver['Audited_on']=currentime
                            df_selected_ver['Audited_By']=st.session_state['User']
                            df_selected_ver['Audit_Name']=st.session_state['Audit']
                            df_selected_ver['Audit_id']=int(st.session_state['AuditID'])
                            df_selected_ver['Status']="Closed"
                            very=add_audit_verification(df_selected_ver)
                            
                            
                            #for verification =No insert in Audit_queries
                            df_unselected_ver['Data_Id']=data_id
                            df_unselected_ver['Audit_Verification']="No"
                            df_unselected_ver['Audited_on']=currentime
                            df_unselected_ver['Audited_By']=st.session_state['User']
                            df_unselected_ver['Audit_Name']=st.session_state['Audit']
                            df_unselected_ver['Audit_id']=int(st.session_state['AuditID'])
                            very=add_audit_verification(df_unselected_ver)
                            st.info(very)
                            #st.dataframe(df_unselected_ver)
                            #update audit status
                            update_audit=update_audit_status(data_id,ds_name)
                            #refresh AGGrid-update_mode=GridUpdateMode.MODEL_CHANGED also added with OR
                            #df = df.drop([0],inplace=True)
                            st.info(update_audit)
                            
                            #auditnext()
                       
                        
                        

            with tab2:
                st.header(d_sname)
                #add Reveiew Remark
                #show in DF
                st.title("Add Review Comments for  Data Set...")
                # add verification list
                Reveiew=get_ar_for_ds(d_sname)
                cl1,cl2 =st.columns(2)
                with cl1:
                    with st.form("Analytical Review Comments",clear_on_submit=True):
                        Areview=st.text_area("Enter Comments")
                        # Every form must have a submit button.
                        submitted = st.form_submit_button("Submit")
                        if submitted:
                            #add above to database
                            Reveiew=add_analytical_review(Areview,d_sname,st.session_state['Company'])
                
                with cl2:
                    st.header("Analytical Review Comments")
                    st.table(Reveiew)
                    
                st.markdown("""---""")   
                col1,col2 =st.columns(2)
                ds=get_entire_dataset(ds_name)
                with col1:
                    st.header("Data Set")
                    #st.dataframe(ds)
                    ds=AgGrid(ds)
                    
                with col2:
                    ds=get_entire_dataset(ds_name)
                    st.header("Stats Summary")
                    st.dataframe(ds.describe())
            
                st.markdown("""---""")
                st.header("Generate Detailed Statistical Analysis Report")
                #Click to generate pandas profiling report
                if st.button("Generate Analytical Report"):
                    with st.expander("Report on Data Set"):
                        #profile = ProfileReport(df, title="Data Profiling Report")
                        #ProfileReport(profile)
                        pr = df.profile_report()
                        st_profile_report(pr)
                
    
headerSection = st.container()
mainSection = st.container()
loginSection = st.container()
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
 

def show_main_page():
    with mainSection:
        st.write(f"User:-{st.session_state['username']}")
        
 
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
        st.error("Invalid user name or password")

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
                    show_audit()  
                    
            else:
                #st.title("Login")
                show_login_page()
        