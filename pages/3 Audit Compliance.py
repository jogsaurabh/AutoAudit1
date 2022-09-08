from datetime import datetime
from functions import get_user_rights,get_active_users,add_datato_ds,get_verification,get_audit,add_audit_verification
from functions import create_user,check_login,get_dsname_personresponsible,assign_user_rights,create_company,get_company_names,get_pending_queries
from functions import create_dataset,add_verification_criteria,get_dsname,get_entire_dataset,get_auditee_comp
from functions import get_dataset,update_query_status,add_analytical_review,insert_vouching,update_audit_status,get_ar_for_ds,add_query_reply
import pandas as pd
import streamlit as st
from PIL import Image
image = Image.open('autoaudit_t.png')
from st_aggrid import AgGrid,DataReturnMode, GridUpdateMode, GridOptionsBuilder, JsCode, grid_options_builder
import sqlite3
st.set_page_config(page_title="AutoAudit", page_icon=":white_check_mark:", layout="wide")
#st.title(":white_check_mark: AutoAudit")
st.image(image,width=250)
st.markdown("""---""")
cont_audit_status=st.container()
cont_queryupdate=st.container()

def show_update_audit_status():
    with cont_audit_status:
        auditid=int(st.session_state['AuditID'])
        st.write(f"User:-{st.session_state['User']}",f"  | Company:-{st.session_state['Company']}",
                 f"  | Audit:-{st.session_state['Audit']}",f"  | Role:-{st.session_state['Role']}")
        #get pending queries for DS current Audit
        pending=get_pending_queries(auditid)
        st.title("Update Status of Audit Queries")
        st.markdown("""---""")
        #st.dataframe(pending)
        #get dsnames with personrisponsible= auditee
        pr=st.session_state['User']
        #df_dsnames=get_dsname_personresponsible(auditid,pr)
        #merge DSNmae with Queries to get person risponsible
        #pending=pd.merge(pending,df_dsnames,how="left",left_on="DataSetName",right_on="DS")
        #pending.dropna(subset=['DS'], how='all', inplace=True)
        
        pending_groupby=pending.groupby(['DataSetName'])['Field','Verification','Id'].count().rename(columns={'Status':'Pending','Id':'Total'})
        pending_groupby.rename(columns={'Field':'Vouching'},inplace=True)
        st.header("Summary of Pending Audit Queries")
        rep1,rep2 =st.columns(2)
        with rep1:
            st.dataframe(pending_groupby.style.set_properties(**{'color':'red'},subset=['Vouching','Verification','Total']))
        with rep2:
            st.bar_chart(pending_groupby)
        #show only relevent colums
        st.markdown("""---""")
        builder = GridOptionsBuilder.from_dataframe(pending.loc[:, ['DataSetName','Field','Data_Id','Audit_Value','Remarks','Verification','Audit_Verification','Reply','status_update_remarks']])
        builder.configure_pagination(enabled=True,paginationPageSize=10,paginationAutoPageSize=False)
        builder.configure_selection(selection_mode="single",use_checkbox=True)
                    #builder.configure_default_column(editable=True)
        go = builder.build()
                    #uses the gridOptions dictionary to configure AgGrid behavior.
        #grid_response=AgGrid(pending, gridOptions=go,update_mode= (GridUpdateMode.SELECTION_CHANGED|GridUpdateMode.MODEL_CHANGED),theme="blue")
        grid_response=AgGrid(pending, gridOptions=go,update_mode= (GridUpdateMode.SELECTION_CHANGED|GridUpdateMode.MODEL_CHANGED),fit_columns_on_grid_load=True)

                    #selelcted row to show in audit AGGrid
        selected = grid_response['selected_rows']
        #st.dataframe(pending.loc[:, ['DataSetName','Field','Audit_Value','Remarks','Verification','Audit_Verification','Reply','status_update_remarks']])
        
        if selected:
            #st.write(selected)
            one ,two= st.columns(2)
            with one:
                reply=st.text_area("Add Status Update Remarks to Selected Query",key="ta")
            with two:
                close=st.selectbox("Close / Pending",["Closed","Pending"],key="cq")
            submit=st.button("Submit",key="submitquery")
            if submit:
                    currentime=datetime.now()
                    id=int(selected[0]['Id'])
                    currentremark=selected[0]['status_update_remarks']
                    if currentremark is None:
                        currentremark=""
                        reply=f"{reply}-(by- {st.session_state['User']} , on {currentime})"
                    else:
                        reply=f"{currentremark} ;\n{reply}-(by- {st.session_state['User']} , on {currentime})"
                    #st.text(reply)
                    #st.text(id)
                    #update remark
                    updatereply=update_query_status(id,reply,close)
                    st.success(updatereply)
        else:
            st.info("Selected a Row to Update Query Status")

        

headerSection = st.container()
mainSection = st.container()
loginSection = st.container()
logOutSection = st.container()
 
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
    with cont_queryupdate:
        auditid=int(st.session_state['AuditID'])
        st.write(f"User:-{st.session_state['User']}",f"  | Company:-{st.session_state['Company']}",
                 f"  | Audit:-{st.session_state['Audit']}",f"  | Role:-{st.session_state['Role']}")
        #get pending queries for DS current Audit
        pending=get_pending_queries(auditid)
        st.title("Reply to Audit Queries")
        
        #st.dataframe(pending)
        #get dsnames with personrisponsible= auditee
        pr=st.session_state['User']
        df_dsnames=get_dsname_personresponsible(auditid,pr)
        #merge DSNmae with Queries to get person risponsible
        pending=pd.merge(pending,df_dsnames,how="left",left_on="DataSetName",right_on="DS")
        pending.dropna(subset=['DS'], how='all', inplace=True)
        
        pending_groupby=pending.groupby(['DataSetName'])['Field','Verification','Id'].count().rename(columns={'Status':'Pending','Id':'Total'})
        pending_groupby.rename(columns={'Field':'Vouching'},inplace=True)
        st.header("Summary of Pending Audit Queries")
        rep1,rep2 =st.columns(2)
        with rep1:
            st.dataframe(pending_groupby.style.set_properties(**{'color':'red'},subset=['Vouching','Verification','Total']))
        with rep2:
            st.bar_chart(pending_groupby)
        #show only relevent colums
        builder = GridOptionsBuilder.from_dataframe(pending.loc[:, ['DataSetName','Field','Data_Id','Audit_Value','Remarks','Verification','Audit_Verification','Reply','status_update_remarks']])
        builder.configure_pagination(enabled=True,paginationAutoPageSize=False,paginationPageSize=10)
        builder.configure_selection(selection_mode="single",use_checkbox=True)
                    #builder.configure_default_column(editable=True)
        go = builder.build()
                    #uses the gridOptions dictionary to configure AgGrid behavior.
        grid_response=AgGrid(pending, gridOptions=go,update_mode= (GridUpdateMode.SELECTION_CHANGED|GridUpdateMode.MODEL_CHANGED),fit_columns_on_grid_load=True)
                    #selelcted row to show in audit AGGrid
        selected = grid_response['selected_rows']
        #st.dataframe(pending.loc[:, ['DataSetName','Field','Audit_Value','Remarks','Verification','Audit_Verification','Reply','status_update_remarks']])
        
        if selected:
            #st.write(selected)
            reply=st.text_area("Add Reply to Selected Query",key="ta")
            submit=st.button("Submit",key="submitquery")
            if submit:
                if not reply:
                    st.warning("Reply can not be Blank")
                else:
                    currentime=datetime.now()
                    id=int(selected[0]['Id'])
                    currentremark=selected[0]['Reply']
                    if currentremark is None:
                        currentremark=""
                        reply=f"{reply}-(by- {st.session_state['User']} , on {currentime})"
                    else:
                        reply=f"{currentremark} ;\n{reply}-(by- {st.session_state['User']} , on {currentime})"
                    #st.text(reply)
                    #st.text(id)
                    #update remark
                    updatereply=add_query_reply(id,reply)
                    st.success(updatereply)
        else:
            st.info("Selected a Row to reply Query")
            
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
                    show_update_audit_status()  
                    
            else:
                #st.title("Login")
                show_login_page()
        
