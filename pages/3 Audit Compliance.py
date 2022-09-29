from datetime import datetime
from functions import get_user_rights,get_active_users,add_datato_ds,get_verification,get_audit,add_audit_verification
from functions import create_user,check_login,get_dsname_personresponsible,assign_user_rights,create_company,get_company_names,get_pending_queries
from functions import update_mgt_comm,update_query_status_ar,get_ar_queries,get_vv_quries,create_dataset,add_verification_criteria,get_dsname,get_entire_dataset,get_auditee_comp
from functions import update_compliance_remarks,get_pending_Compliance,update_corre_action,get_pending_Corrective,get_pending_obser,add_query_reply_AR,get_dataset,update_query_status,add_analytical_review,insert_vouching,update_audit_status,get_ar_for_ds,add_query_reply
import pandas as pd
import os
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
        #pending=get_pending_queries(auditid)
        
        #st.markdown("""---""")
        with st.sidebar.markdown("# Select Data Set"):
            sta_opts=st.comp_opps=st.radio('Audit Compliance',('Update Query Status','Update Audit Compliance Status'),key='opcompr')
            
        if sta_opts=='Update Query Status':
                st.title("Update Status of Audit Queries")
                optionsdf=get_dsname(int(st.session_state['AuditID']))
                #add blank row at begining of list
                optionsdf.loc[-1]=['---']
                optionsdf.index=optionsdf.index+1
                optionsdf.sort_index(inplace=True)
                d_sname=st.selectbox("Select Data Set to Audit",optionsdf,key="selectdsname")
                ds_name=f"{st.session_state['Company']}_{(st.session_state['AuditID'])}_{d_sname}"
                #select dataset 
            
                if d_sname=="---":
                    st.warning("Select Data Set to Update Audit Status")
                else:
                    st.success(f"Update Remarks for {d_sname} Queries")
                    with st.expander("Vouching & Verification Queries"):
                    
                        pending=get_vv_quries(f"{st.session_state['Company']}_{st.session_state['AuditID']}_{d_sname}",d_sname,int(st.session_state['AuditID']))
                        #st.dataframe(pending)
                        builder = GridOptionsBuilder.from_dataframe(pending)
                        #.loc[:, ['DataSetName','Field','Data_Id','Audit_Value','Remarks','Verification','Audit_Verification','Reply','status_update_remarks']])
                        builder.configure_pagination(enabled=True,paginationPageSize=10,paginationAutoPageSize=False)
                        builder.configure_selection(selection_mode="single",use_checkbox=True)
                                    #builder.configure_default_column(editable=True)
                        #cc=JsCode("return{color: 'red'}")
                        builder.configure_columns(['Criteria','Condition','Cause','Effect','Reply'],cellStyle={'color': 'red'})
                        go = builder.build()
                                    #uses the gridOptions dictionary to configure AgGrid behavior.
                        #grid_response=AgGrid(pending, gridOptions=go,update_mode= (GridUpdateMode.SELECTION_CHANGED|GridUpdateMode.MODEL_CHANGED),theme="blue")
                        grid_response=AgGrid(pending, gridOptions=go,update_mode= (GridUpdateMode.SELECTION_CHANGED|GridUpdateMode.MODEL_CHANGED))

                                    #selelcted row to show in audit AGGrid
                        csv=pending.to_csv().encode('utf-8')
                        st.download_button("Download csv file",csv,f"{d_sname}.csv")
                        selected = grid_response['selected_rows']
                        #st.dataframe(pending.loc[:, ['DataSetName','Field','Audit_Value','Remarks','Verification','Audit_Verification','Reply','status_update_remarks']])
                        
                        if selected:
                            #st.write(selected)
                            currentremark=selected[0]['status_update_remarks']
                            currentquryreply=selected[0]['Reply']
                            one ,two= st.columns(2)
                            with one:
                                "Auditee Reply:-"
                                st.warning(currentquryreply)
                                "Current Remarks:-"
                                st.warning(currentremark)
                            
                            with two:
                                reply=st.text_area("Add Status Update Remarks to Selected Query",key="ta")
                                close=st.selectbox("Close / Pending",["Closed","Pending"],key="cq")
                            submit=st.button("Submit",key="submitquery")
                            if submit:
                                    currentime=datetime.now()
                                    id=int(selected[0]['Id'])
                                    #currentremark=selected[0]['status_update_remarks']
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
                    st.markdown("""---""")
                    with st.expander("Analytical Review & Other Queries"):
                            
                                pending=get_ar_queries(d_sname)
                                #st.dataframe(pending)
                                builder = GridOptionsBuilder.from_dataframe(pending)
                                #.loc[:, ['DataSetName','Field','Data_Id','Audit_Value','Remarks','Verification','Audit_Verification','Reply','status_update_remarks']])
                                builder.configure_pagination(enabled=True,paginationPageSize=10,paginationAutoPageSize=False)
                                builder.configure_selection(selection_mode="single",use_checkbox=True)
                                            #builder.configure_default_column(editable=True)
                                #cc=JsCode("return{color: 'red'}")
                                builder.configure_columns(['Criteria','Condition','Cause','Effect','Reply'],cellStyle={'color': 'red'})
                                go = builder.build()
                                            #uses the gridOptions dictionary to configure AgGrid behavior.
                                #grid_response=AgGrid(pending, gridOptions=go,update_mode= (GridUpdateMode.SELECTION_CHANGED|GridUpdateMode.MODEL_CHANGED),theme="blue")
                                grid_response=AgGrid(pending, gridOptions=go,update_mode= (GridUpdateMode.SELECTION_CHANGED|GridUpdateMode.MODEL_CHANGED))

                                            #selelcted row to show in audit AGGrid
                                csv=pending.to_csv().encode('utf-8')
                                st.download_button("Download csv file",csv,f"{d_sname}.csv")
                                selected = grid_response['selected_rows']
                                #st.dataframe(pending.loc[:, ['DataSetName','Field','Audit_Value','Remarks','Verification','Audit_Verification','Reply','status_update_remarks']])
                                
                                if selected:
                                    #st.write(selected)
                                    currentremark=selected[0]['status_update_remarks']
                                    currentquryreply=selected[0]['reply']
                                    filename=selected[0]['Review_File']
                                    rev_filename=f"{(st.session_state['AuditID'])}{d_sname}_{filename}"
                                    
                                    if filename:
                                        
                                        with open(os.path.join("rev_files",rev_filename), 'rb') as f:
                                            st.download_button('Download Attachment', f, file_name=filename,key="reveiewdl")    
                    
                                    one ,two= st.columns(2)
                                    
                                    with one:
                                        "Auditee Reply:-"
                                        st.warning(currentquryreply)
                                        "Current Remarks:-"
                                        st.warning(currentremark)
                                    with two:
                                        reply=st.text_area("Add Status Update Remarks to Selected Query",key="ta1")
                                        close=st.selectbox("Close / Pending",["Closed","Pending"],key="cq2")
                                    submit=st.button("Submit",key="submitquery2")
                                    if submit:
                                            currentime=datetime.now()
                                            id=int(selected[0]['Id'])
                                            #currentremark=selected[0]['status_update_remarks']
                                            if currentremark is None:
                                                currentremark=""
                                                reply=f"{reply}-(by- {st.session_state['User']} , on {currentime})"
                                            else:
                                                reply=f"{currentremark} ;\n{reply}-(by- {st.session_state['User']} , on {currentime})"
                                            #st.text(reply)
                                            #st.text(id)
                                            #update remark
                                            updatereply=update_query_status_ar(id,reply,close)
                                            st.success(updatereply)
                                else:
                                    st.info("Selected a Row to Update Query Status")
        else:
                    st.title("Update Audit Compliance")
                    auditid=int(st.session_state['AuditID'])
                    pending_qs=get_pending_Compliance(auditid)   
                    builder = GridOptionsBuilder.from_dataframe(pending_qs)
                    builder.configure_pagination(enabled=True,paginationAutoPageSize=False,paginationPageSize=10)
                    builder.configure_selection(selection_mode="single",use_checkbox=True)
                    builder.configure_columns(['Criteria','Condition','Cause','Effect','Reply'],cellStyle={'color': 'red'})
                    go = builder.build()
                                #uses the gridOptions dictionary to configure AgGrid behavior.
                    grid_response=AgGrid(pending_qs, gridOptions=go,update_mode= (GridUpdateMode.SELECTION_CHANGED|GridUpdateMode.MODEL_CHANGED))
                                #selelcted row to show in audit AGGrid
                    #csv=pending_ob.to_csv().encode('utf-8')
                    #st.download_button("Download csv file",csv,f"{d_sname}.csv")
                    selected = grid_response['selected_rows']
                    #st.dataframe(pending.loc[:, ['DataSetName','Field','Audit_Value','Remarks','Verification','Audit_Verification','Reply','status_update_remarks']])
                    
                    if selected:
                        #st.write(selected)
                        actionremarks=selected[0]['Action_Remarks']
                        c_Corrective_Action_Plan=selected[0]['Corrective_Action_Plan']
                        
                        
                        co1,co2,co3 =st.columns(3)
                        with co1:
                            "Corrective_Action_Plan:-"
                            st.warning(c_Corrective_Action_Plan)
                            #st.write(selected)
                        with co2:
                            "Current Action_Remarks:-"
                            st.warning(actionremarks)
                        with co3:
                            "Current Compliance_Remarks:-"
                            st.warning(selected[0]['Compliance_Remarks'])
                        reply=st.text_area("Add Compliance Remarks",key="taocc")
                        status=st.selectbox("Update Status of Audit Observation",('Open','Close'),key='ocu')
                        submit=st.button("Submit",key="submitqueryocc")
                        if submit:
                            if not reply:
                                st.warning("Comments can not be Blank")
                            else:
                                currentime=datetime.now()
                                id=int(selected[0]['id'])
                                currentremark=selected[0]['Compliance_Remarks']
                                if currentremark is None:
                                    currentremark=""
                                    reply=f"{reply}-(by- {st.session_state['User']} , on {currentime})"
                                else:
                                    reply=f"{currentremark} ;\n{reply}-(by- {st.session_state['User']} , on {currentime})"
                                #st.text(reply)
                                #st.text(id)
                                #update remark
                                mgt_comments=update_compliance_remarks(id,reply,status)
                                st.success(mgt_comments)
                    else:
                        st.info("Selected a Row to Update Compliance Remarks")
                
                
                
        

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
        
        #pending=get_pending_queries(auditid)
        #st.markdown("""---""")
        pr=st.session_state['User']
        with st.sidebar.markdown(" Select Data Set."):
            comp_opps=st.radio('Audit Compliance',('Reply to Queries','Reply to Audit Observations','Update Corrective Actions'),key='opcomp')
        if comp_opps=='Reply to Queries':
            st.title("Reply to Audit Queries")                
            #optionsdf=get_dsname(int(st.session_state['AuditID']))
            optionsdf=get_dsname_personresponsible(auditid,pr)
            #st.dataframe(optionsdf)
            #add blank row at begining of list
            optionsdf.loc[-1]=['---']
            optionsdf.index=optionsdf.index+1
            optionsdf.sort_index(inplace=True)
            d_sname=st.selectbox("Select Data Set to Audit",optionsdf,key="selectdsname")
            ds_name=f"{st.session_state['Company']}_{(st.session_state['AuditID'])}_{d_sname}"
            #select dataset 
            if d_sname=="---":
                st.warning("Select Data Set to ReplyAudit Queries")
            else:
                st.success(f"Reply for {d_sname} Queries")
                with st.expander("Vouching & Verification Queries"):
                    pending=get_vv_quries(f"{st.session_state['Company']}_{st.session_state['AuditID']}_{d_sname}",d_sname,int(st.session_state['AuditID']))   
                    builder = GridOptionsBuilder.from_dataframe(pending)
                    builder.configure_pagination(enabled=True,paginationAutoPageSize=False,paginationPageSize=10)
                    builder.configure_selection(selection_mode="single",use_checkbox=True)
                    builder.configure_columns(['Criteria','Condition','Cause','Effect','Reply'],cellStyle={'color': 'red'})
                    go = builder.build()
                                #uses the gridOptions dictionary to configure AgGrid behavior.
                    grid_response=AgGrid(pending, gridOptions=go,update_mode= (GridUpdateMode.SELECTION_CHANGED|GridUpdateMode.MODEL_CHANGED))
                                #selelcted row to show in audit AGGrid
                    csv=pending.to_csv().encode('utf-8')
                    st.download_button("Download csv file",csv,f"{d_sname}.csv")
                    selected = grid_response['selected_rows']
                    #st.dataframe(pending.loc[:, ['DataSetName','Field','Audit_Value','Remarks','Verification','Audit_Verification','Reply','status_update_remarks']])
                    
                    if selected:
                        #st.write(selected)
                        currentremark=selected[0]['Reply']
                        replyremarks=selected[0]['status_update_remarks']
                        
                        co1,co2 =st.columns(2)
                        with co1:
                            "Current Auditee Reply:-"
                            st.warning(currentremark)
                            #st.write(selected)
                        with co2:
                            "Auditors Remarks for Reply:-"
                            st.warning(replyremarks)
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
                        st.info("Selected a Row to Reply the Query")
                st.markdown("""---""")
                with st.expander("Analytical Review & Other Queries"):
                    pending=get_ar_queries(d_sname)
                    builder = GridOptionsBuilder.from_dataframe(pending)
                    builder.configure_pagination(enabled=True,paginationAutoPageSize=False,paginationPageSize=10)
                    builder.configure_selection(selection_mode="single",use_checkbox=True)
                    builder.configure_columns(['Criteria','Condition','Cause','Effect','Reply'],cellStyle={'color': 'red'})
                    go = builder.build()
                                #uses the gridOptions dictionary to configure AgGrid behavior.
                    grid_response=AgGrid(pending, gridOptions=go,update_mode= (GridUpdateMode.SELECTION_CHANGED|GridUpdateMode.MODEL_CHANGED))
                                #selelcted row to show in audit AGGrid
                    csv=pending.to_csv().encode('utf-8')
                    st.download_button("Download csv file",csv,f"{d_sname}.csv")
                    selected = grid_response['selected_rows']
                    #st.dataframe(pending.loc[:, ['DataSetName','Field','Audit_Value','Remarks','Verification','Audit_Verification','Reply','status_update_remarks']])
                    
                    if selected:
                        currentremark=selected[0]['reply']
                        replyremarks=selected[0]['status_update_remarks']
                        filename=selected[0]['Review_File']
                        rev_filename=f"{(st.session_state['AuditID'])}{d_sname}_{filename}"
                                    
                        if filename:
                                        
                            with open(os.path.join("rev_files",rev_filename), 'rb') as f:
                                st.download_button('Download Attachment', f, file_name=filename,key="auditeedl")    
                        
                        co1,co2 =st.columns(2)
                        with co1:
                            "Current Auditee Reply:-"
                            st.warning(currentremark)
                            #st.write(selected)
                        with co2:
                            "Auditors Remarks for Reply:-"
                            st.warning(replyremarks)
                            #st.write(selected)
                        reply=st.text_area("Add Reply to Selected Query",key="ta1")
                        submit=st.button("Submit",key="submitquery111")
                        if submit:
                            if not reply:
                                st.warning("Reply can not be Blank")
                            else:
                                currentime=datetime.now()
                                id=int(selected[0]['Id'])
                                #currentremark=selected[0]['reply']
                                if currentremark is None:
                                    currentremark=""
                                    reply=f"{reply}-(by- {st.session_state['User']} , on {currentime})"
                                else:
                                    reply=f"{currentremark} ;\n{reply}-(by- {st.session_state['User']} , on {currentime})"
                                #st.text(reply)
                                #st.text(id)
                                #update remark
                                updatereply=add_query_reply_AR(id,reply)
                                st.success(updatereply)
                    else:
                        st.info("Selected a Row to Reply the Query")
        
        elif comp_opps=='Update Corrective Actions':
                    st.title("Update Corrective Actions")
                    auditid=int(st.session_state['AuditID'])
                    pending_ob=get_pending_Corrective(auditid)   
                    builder = GridOptionsBuilder.from_dataframe(pending_ob)
                    builder.configure_pagination(enabled=True,paginationAutoPageSize=False,paginationPageSize=10)
                    builder.configure_selection(selection_mode="single",use_checkbox=True)
                    builder.configure_columns(['Criteria','Condition','Cause','Effect','Reply'],cellStyle={'color': 'red'})
                    go = builder.build()
                                #uses the gridOptions dictionary to configure AgGrid behavior.
                    grid_response=AgGrid(pending_ob, gridOptions=go,update_mode= (GridUpdateMode.SELECTION_CHANGED|GridUpdateMode.MODEL_CHANGED))
                                #selelcted row to show in audit AGGrid
                    #csv=pending_ob.to_csv().encode('utf-8')
                    #st.download_button("Download csv file",csv,f"{d_sname}.csv")
                    selected = grid_response['selected_rows']
                    #st.dataframe(pending.loc[:, ['DataSetName','Field','Audit_Value','Remarks','Verification','Audit_Verification','Reply','status_update_remarks']])
                    
                    if selected:
                        #st.write(selected)
                        actionremarks=selected[0]['Action_Remarks']
                        c_Corrective_Action_Plan=selected[0]['Corrective_Action_Plan']
                        
                        
                        co1,co2 =st.columns(2)
                        with co1:
                            "Corrective_Action_Plan:-"
                            st.warning(c_Corrective_Action_Plan)
                            #st.write(selected)
                        with co2:
                            "Current Action_Remarks:-"
                            st.warning(actionremarks)
                        reply=st.text_area("Add Comments to Selected Action_Plan",key="taoc")
                        submit=st.button("Submit",key="submitqueryoc")
                        if submit:
                            if not reply:
                                st.warning("Comments can not be Blank")
                            else:
                                currentime=datetime.now()
                                id=int(selected[0]['id'])
                                currentremark=selected[0]['Action_Remarks']
                                if currentremark is None:
                                    currentremark=""
                                    reply=f"{reply}-(by- {st.session_state['User']} , on {currentime})"
                                else:
                                    reply=f"{currentremark} ;\n{reply}-(by- {st.session_state['User']} , on {currentime})"
                                #st.text(reply)
                                #st.text(id)
                                #update remark
                                mgt_comments=update_corre_action(id,reply)
                                st.success(mgt_comments)
                    else:
                        st.info("Selected a Row to Reply the Audit Observation")
                
            
        else:
                    st.title("Reply to Audit Observations")
                    auditid=int(st.session_state['AuditID'])
                    pending_ob=get_pending_obser(auditid)   
                    builder = GridOptionsBuilder.from_dataframe(pending_ob)
                    builder.configure_pagination(enabled=True,paginationAutoPageSize=False,paginationPageSize=10)
                    builder.configure_selection(selection_mode="single",use_checkbox=True)
                    builder.configure_columns(['Criteria','Condition','Cause','Effect','Reply'],cellStyle={'color': 'red'})
                    go = builder.build()
                                #uses the gridOptions dictionary to configure AgGrid behavior.
                    grid_response=AgGrid(pending_ob, gridOptions=go,update_mode= (GridUpdateMode.SELECTION_CHANGED|GridUpdateMode.MODEL_CHANGED))
                                #selelcted row to show in audit AGGrid
                    #csv=pending_ob.to_csv().encode('utf-8')
                    #st.download_button("Download csv file",csv,f"{d_sname}.csv")
                    selected = grid_response['selected_rows']
                    #st.dataframe(pending.loc[:, ['DataSetName','Field','Audit_Value','Remarks','Verification','Audit_Verification','Reply','status_update_remarks']])
                    
                    if selected:
                        #st.write(selected)
                        recomendarions=selected[0]['Recomendation']
                        c_Management_Comments=selected[0]['Management_Comments']
                        
                        
                        co1,co2 =st.columns(2)
                        with co1:
                            "Audit Recomendations:-"
                            st.warning(recomendarions)
                            #st.write(selected)
                        with co2:
                            "Current Management_Comments:-"
                            st.warning(c_Management_Comments)
                        reply=st.text_area("Add Comments to Selected Observation",key="tao")
                        submit=st.button("Submit",key="submitqueryo")
                        if submit:
                            if not reply:
                                st.warning("Comments can not be Blank")
                            else:
                                currentime=datetime.now()
                                id=int(selected[0]['id'])
                                currentremark=selected[0]['Management_Comments']
                                if currentremark is None:
                                    currentremark=""
                                    reply=f"{reply}-(by- {st.session_state['User']} , on {currentime})"
                                else:
                                    reply=f"{currentremark} ;\n{reply}-(by- {st.session_state['User']} , on {currentime})"
                                #st.text(reply)
                                #st.text(id)
                                #update remark
                                mgt_comments=update_mgt_comm(id,reply)
                                st.success(mgt_comments)
                    else:
                        st.info("Selected a Row to Reply the Audit Observation")
                
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
        
