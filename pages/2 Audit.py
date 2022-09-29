#from cgitb import enable
#from distutils.command.build import build
#from sys import audit
#from turtle import onclick
import os
from queue import Empty
#import numpy as np
from jinja2 import Environment, FileSystemLoader
#from email.policy import default
#from operator import index
#from sys import audit
#from tkinter import HORIZONTAL
from matplotlib.cbook import report_memory
import streamlit as st
#from streamlit import caching
from datetime import datetime
from docx import Document
from htmldocx import HtmlToDocx
from functions import get_ar_queries,modify_audit_summ,add_audit_summ,get_Audit_summ,get_audit_observations,del_audit_doc,modif_comp_doc,get_company_docs,get_user_rights,get_active_users,add_datato_ds,get_verification,get_audit,add_audit_verification
from functions import closed_audit,create_user,check_login,get_dsname_personresponsible,assign_user_rights,create_company,get_company_names,get_pending_queries
from functions import del_comp_doc,add_comp_doc,create_dataset,add_verification_criteria,get_dsname,get_entire_dataset,get_auditee_comp
from functions import get_pending_Compliance,del_audit_sum,modify_audit_observation,modif_audit_doc,add_audit_doc,get_audit_docs,get_dataset,add_analytical_review,insert_vouching,update_audit_status,get_ar_for_ds,add_query_reply
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
cont_observation=st.container()
cont_oaudit_summary=st.container()
#st.write(f"User:-{st.session_state['username']}")
#comp_name=st.session_state['Company']
def show_Audit_observations():
    with cont_observation:
        crud=st.radio("",('Show Observations','Update Audit Observations'),horizontal=True,key='strcrudas')
        auditid=int(st.session_state['AuditID'])
        df=get_audit_observations(auditid)
        if crud=='Update Audit Observations':
            st.success('Update Audit Observations...')
            #auditid=int(st.session_state['AuditID'])
            #df=get_audit_observations(auditid)
            builder = GridOptionsBuilder.from_dataframe(df)
            builder.configure_pagination(enabled=True,paginationAutoPageSize=False,paginationPageSize=10)
            builder.configure_selection(selection_mode="single",use_checkbox=True)
                            #builder.configure_default_column(editable=True)
            #builder.configure_default_column(groupable=True)
            go = builder.build()
                            #uses the gridOptions dictionary to configure AgGrid behavior.
            grid_response=AgGrid(df, gridOptions=go,update_mode= (GridUpdateMode.SELECTION_CHANGED|GridUpdateMode.MODEL_CHANGED))
                            #selelcted row to show in audit AGGrid
            selected = grid_response['selected_rows']
            #csv=df.to_csv().encode('utf-8')
            #st.download_button("Download CSV file",csv,f"Audit_Obs.csv")
            if selected:
                st.success(f"""Criteria:- \n{selected[0]['Criteria']}""")
                
                filename=selected[0]['Annexure']
                rev_filename=f"{auditid}_{filename}"
                                    
                if filename:
                                        
                    with open(os.path.join("obsev_docs",rev_filename), 'rb') as f:
                        st.download_button('Download Attachment', f, file_name=filename,key="reveiewdld")    
                    
                with st.form("Mdify Observation Doc",clear_on_submit=True):
                    
                    Condition=st.text_area("Update Condition",key='condition')
                    Cause=st.text_area("Update Cause",key='Cause')
                    Effect=st.text_area("Update Effect",key='Effect')
                    
                    Conclusion=st.text_area("Update Conclusion",key='Conclusion1')
                    
                    Impact=st.text_area("Update Impact",key='Impact')
                    Recomendation=st.text_area("Update Recomendation",key='Recomendation')
                    Corrective_Action_Plan=st.text_area("Update Corrective_Action_Plan",key='Corrective_Action_Plan')
                    Is_Adverse_Remark=st.selectbox("Update Is_Adverse_Remark",key='isactive',options=("Yes","No"))
                    #Is_Adverse_Remark=st.text_input("Update Is_Adverse_Remark",key='Is_Adverse_Remark',value=selected[0]['Is_Adverse_Remark'])
                    DeadLine=st.date_input('Update DeadLine',key='DeadLine')
                    Annexure=st.file_uploader("Upload File",type=['pdf','xlsx','docx'],key='Annexure')
                    file_name=st.text_input("Enter File Name without extention...Name should be Unique",key='comfilname')
                    
                                    
                    roid=selected[0]['id']
                                    
                                    
                    submitted_Obsr_mod =st.form_submit_button("Submit")
                    if submitted_Obsr_mod:
                        if Is_Adverse_Remark=="Yes" or Is_Adverse_Remark=="No":
                            
                            if Annexure is not None:
                                                    #st.write(f'again-{file_name}')
                                if file_name:
                                    if Annexure.type=="application/vnd.openxmlformats-officedocument.wordprocessingml.document":
                                        extn="docx"
                                    elif Annexure.type=="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet":
                                        extn='xlsx'
                                    else :
                                        extn='pdf'
                                                        #if st.button("Upload file",key='uf1'):
                                    comp_filename=f"{auditid}_{file_name}.{extn}"
                                    file_name=f"{file_name}.{extn}"
                                    with open(os.path.join("obsev_docs",comp_filename),"wb") as f: 
                                        f.write(Annexure.getbuffer())
                                                        
                                    updatobr=modify_audit_observation(roid,Condition,Cause,Effect,Conclusion,Impact,Recomendation,Corrective_Action_Plan,Is_Adverse_Remark,DeadLine,file_name)                                        
                                else:
                                    st.info("Enter File Name")    
                            else:
                                                #st.write(f'befor-{file_name}')
                                file_name=None
                                                #st.write(f'then-{file_name}')
                                                    #reviws_table.add_row({"Criteria":"criteria","Condition":"condition","Cause":"cause","Effect":"effect"})
                                updatobr=modify_audit_observation(roid,Condition,Cause,Effect,Conclusion,Impact,Recomendation,Corrective_Action_Plan,Is_Adverse_Remark,DeadLine,file_name)                                        
                                        
                        else: 
                            st.info('Is_Adverse_Remark can either be Yes or No') 
                        
            else:
                st.info('Select a Record to Update ....')
        else:
            #show summary
            #table = pd.pivot_table(df, values='Risk_Weight', index=['Audit_Area', 'Heading','Criteria'],
                     #aggfunc=np.sum) 
            #table=df.groupby(['Audit_Area', 'Heading','Criteria','Condition','Cause','Effect'])['Risk_Weight'].sum()  
            #table.drop_duplicates("Audit_Area",keep='first',inplace=True)  
            #st.dataframe(table)            
            builder = GridOptionsBuilder.from_dataframe(df)
            builder.configure_default_column(groupable=True)
            #builder.configure_columns(column_names=['Audit_Area', 'Heading','Criteria'])
            builder.configure_pagination(enabled=True,paginationAutoPageSize=False,paginationPageSize=10)
            builder.configure_selection(selection_mode="single",use_checkbox=True)
                            #builder.configure_default_column(editable=True)
            #builder.configure_columns(['Audit_Area'],columnDefs={'field': 'Audit_Area', 'rowGroup': 'true', 'hide': 'true' })
            #gridOptionsset = {'columnDefs': {'field': 'Audit_Area', 'rowGroup': 'true', 'hide': 'true' }}
            #builder.configure_grid_options(gridOptionsset)
            go = builder.build()
                            #uses the gridOptions dictionary to configure AgGrid behavior.
            st.success(f"""Use Options to Group Report by Mutiple Levels.
                       Right Click to Export Report to Excel""")
            grid_response=AgGrid(df, gridOptions=go,update_mode= (GridUpdateMode.SELECTION_CHANGED|GridUpdateMode.MODEL_CHANGED))
            
        
        
            
       
def show_Audit_summary():
    with cont_oaudit_summary:
        st.success('Summary of Audit Observations...')
        crud=st.radio("",('View','Add New','Modify','Delete'),horizontal=True,key='strcrud')
        auditid=int(st.session_state['AuditID'])
        df=get_Audit_summ(auditid)
        builder = GridOptionsBuilder.from_dataframe(df)
        builder.configure_pagination(enabled=True,paginationAutoPageSize=False,paginationPageSize=15)
        builder.configure_selection(selection_mode="single",use_checkbox=True)
                        #builder.configure_default_column(editable=True)
        go = builder.build()
                        #uses the gridOptions dictionary to configure AgGrid behavior.
        grid_response=AgGrid(df, gridOptions=go,update_mode= (GridUpdateMode.SELECTION_CHANGED|GridUpdateMode.MODEL_CHANGED))
                        #selelcted row to show in audit AGGrid
        selected = grid_response['selected_rows']
        #col1,col2,c3,c4 =st.columns(4)
        #with col1:
            #csv=df.to_csv().encode('utf-8')
            #st.download_button("Download CSV file",csv,f"Audit_Summ.csv")
        #report in word
        #with col2:
            
        if st.button("Generate Report in Word",key="grwrs"):
                    df.drop(['id', 'Audit_id','Created_by','Created_on'], axis=1,inplace=True)
                    fname=f"{st.session_state['Company']}_{st.session_state['AuditID']}"
                    #st.write(fname)
                    # 2. Create a template Environment
                    env = Environment(loader=FileSystemLoader('templates'))
                    # 3. Load the template from the Environment
                    template = env.get_template('summ.html')
                    # 4. Render the template with variables
                    
                    titler=f"Company:- {st.session_state['Company']}| Audit:- {st.session_state['Audit']}"
                    html1 = template.render(logo='autoaudit_t.png',
                                            page_title_text=titler,
                                            title_text='Executive Summary',
                                            DF1_heading="Summary Observations",                      
                                            df1=df.to_html())
                                            
                                            
                                            
                    #docx to rport
                    document = Document()
                    new_parser = HtmlToDocx()
                    document=new_parser.parse_html_string(html1)
                    document.save(fname)
                    #st.markdown(html1, unsafe_allow_html=True)
                    #components.html(html1, width=800, height=400,scrolling=True)
                    with open(fname,'rb') as f:
                        st.download_button('Download Reports',f,'Summ_report.docx')

        
        
        if crud=='Add New':
                    st.success('Enter details to Add New Record')
                    with st.form("Add AduSumm docs",clear_on_submit=True):
                        Observation=st.text_input("Enter Observation",key='Observation')
                        Impact=st.text_input("Enter Impact",key='Impact')
                        Area=st.text_input("Enter Area",key='Area')
                        Need_for_Management_Intervention=st.text_input("Need_for_Management_Intervention",key='Need_for_Management_Intervention')
                        risk_weight=st.slider("Set Risk Weights",min_value=1,max_value=10,key='slider2rws')
                        if risk_weight >=1 and risk_weight <=3:
                                    risk_category='Low'
                        elif risk_weight >=4 and risk_weight <=7:
                                    risk_category='Medium'
                        else:
                                    risk_category='High'
                        submitted_com_sum = st.form_submit_button("Submit")
                        if submitted_com_sum:
                            if Observation:
                                audsum=add_audit_summ(auditid,Observation,risk_weight,risk_category,Impact,
                                                       Area,Need_for_Management_Intervention)                                        
                            else:
                                st.info("Please Enter -Observation. It is Mandatory field")
        elif crud=='Modify':
                           
            if selected:
                st.success('Enter details to Modify Selected Record')
                with st.form("Mdify Summ",clear_on_submit=True):
                                    
                        roid=selected[0]['id']
                        Observation=st.text_input("Update Observation",key='Observationm',value=selected[0]['Observation'])
                        Impact=st.text_input("Update Impactm",key='Impact',value=selected[0]['Impact'])
                        Area=st.text_input("Update Area",key='Aream',value=selected[0]['Impact'])
                        Need_for_Management_Intervention=st.text_input("Need_for_Management_Intervention",key='Need_for_Management_Interventionm',value=selected[0]['Need_for_Management_Intervention'])
                        risk_weight=st.slider("Set Risk Weights",min_value=1,max_value=10,key='slider2rwsm')
                        if risk_weight >=1 and risk_weight <=3:
                                    risk_category='Low'
                        elif risk_weight >=4 and risk_weight <=7:
                                    risk_category='Medium'
                        else:
                                    risk_category='High'
                        submitted_com_summ = st.form_submit_button("Submit")
                        if submitted_com_summ:
                            if Observation:
                                audsum=modify_audit_summ(roid,Observation,Impact,Area,
                                                         Need_for_Management_Intervention,risk_weight,risk_category)                                        
                            else:
                                st.info("Please Enter - Observation. It is Mandatory field")
                            
            else:
                st.info('Select a Record to Modify ....')
                        
                    
        elif crud=='View':
            st.success('')
        else:
                if selected:
                        st.success('Are you sure you want to Delete Selected Record')
                        if st.button("Delete Selected Record",key='delcompdocacks'):
                            rid=selected[0]['id']
                            rdel=del_audit_sum(rid)
                else:
                        st.info('Select a Record to Delete ....')

        
        
        
        
       

def show_audit():
    
    with audit_container:
        st.write(f"User:-{st.session_state['User']}",f"  | Company:-{st.session_state['Company']}",
                 f"  | Audit:-{st.session_state['Audit']}",f"  | Role:-{st.session_state['Role']}")
        
        st.title("Audit")
        with st.sidebar.markdown("# Audit"):
            sel_option= st.radio("Select Option",('Documents & Info.','Select Data Set to Audit','Audit Observations','Audit Summary','Close Audit'),key='raiodmainop')
        if sel_option=='Documents & Info.':
            
            docs_ops=st.selectbox('Select Audit File',options=('-----','Company Audit File','Audit Working Papers'))
            if docs_ops=="-----":
                st.info("Select type of Audit File...")
            elif docs_ops=="Company Audit File":
                #st.markdown("""---""")
                #st. success(docs_ops)
                crud=st.radio("",('View','Add New','Modify','Delete'),horizontal=True,key='strcrud')
                df=get_company_docs(st.session_state['Company'])
                builder = GridOptionsBuilder.from_dataframe(df)
                builder.configure_pagination(enabled=True,paginationAutoPageSize=False,paginationPageSize=10)
                builder.configure_selection(selection_mode="single",use_checkbox=True)
                        #builder.configure_default_column(editable=True)
                go = builder.build()
                        #uses the gridOptions dictionary to configure AgGrid behavior.
                grid_response=AgGrid(df, gridOptions=go,update_mode= (GridUpdateMode.SELECTION_CHANGED|GridUpdateMode.MODEL_CHANGED))
                        #selelcted row to show in audit AGGrid
                selected = grid_response['selected_rows']
                #st.dataframe(selected)
                                
                if crud=='Add New':
                    st.success('Enter details to Add New Record')
                    with st.form("Add Comp docs",clear_on_submit=True):
                        dtitle=st.text_input("Enter Title",key='dtitle')
                        dremarks=st.text_input("Enter Remarks",key='dremarks')
                        c1,c2 =st.columns(2)
                        with c1:
                            ddoctype=st.selectbox("Select Docuement / Information Type",('Other','Appointment','Communications','Legal','Organisation Details','Registrations'),key='sbadd')
                        with c2:
                            compfile=st.file_uploader("Upload File",type=['pdf','xlsx','docx'],key='compfile')
                            
                            file_name=st.text_input("Enter File Name without extention...Name should be Unique",key='comfilname')
                        submitted_com = st.form_submit_button("Submit")
                        if submitted_com:
                            if dtitle:
                                if compfile is not None:
                                        if file_name:
                                            if compfile.type=="application/vnd.openxmlformats-officedocument.wordprocessingml.document":
                                                extn="docx"
                                            elif compfile.type=="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet":
                                                extn='xlsx'
                                            else :
                                                extn='pdf'
                                            #if st.button("Upload file",key='uf1'):
                                            comp_filename=f"{st.session_state['Company']}_{file_name}.{extn}"
                                            file_name=f"{file_name}.{extn}"
                                            with open(os.path.join("comp_docs",comp_filename),"wb") as f: 
                                                f.write(compfile.getbuffer())
                                            Reveiew=add_comp_doc(dtitle,dremarks,file_name,ddoctype,st.session_state['Company'])                                        
                                        else:
                                            st.info("Enter File Name")    
                                else:
                                    file_name=None
                                        #reviws_table.add_row({"Criteria":"criteria","Condition":"condition","Cause":"cause","Effect":"effect"})
                                    Reveiew=add_comp_doc(dtitle,dremarks,file_name,ddoctype,st.session_state['Company'])                                        
                            else:
                                st.info("Please Enter -Title. It is Mandatory field")

                           
                elif crud=='Modify':
                    if selected:
                        st.success('Enter details to Modify Selected Record')
                        with st.form("Mdify Comp Doc",clear_on_submit=True):
                            dtitle=st.text_input("Enter New Title",key='dtitlem',value=selected[0]['Title'])
                            dremarks=st.text_input("Enter New Remarsk",key='dremarksm',value=selected[0]['Remarks'])
                            roid=selected[0]['id']
                            c1,c2 =st.columns(2)
                            with c1:
                                ddoctype=st.selectbox("Select Docuement / Information Type",('Other','Appointment','Communications','Legal','Organisation Details','Registrations'),key='sbmodif')
                            with c2:
                                compfile=st.file_uploader("Upload File",type=['pdf','xlsx','docx'],key='compfilem')
                                st.write(f"Uploaded filename: {selected[0]['File_Ref']}")
                                #if selected[0]['File_Ref']:
                                    #file_name=selected[0]['File_Ref']
                                    #st.write(f"Uploaded filename: {file_name}")
                                file_name=st.text_input("Enter File Name without extention...Name should be Unique",key='comfilnamem')
                                #else: 
                                    #file_name=st.text_input("Enter File Name without extention...Name should be Unique",key='comfilnamem2')
                            submitted_com_mod =st.form_submit_button("Submit")
                            if submitted_com_mod:
                                #st.write(file_name)
                                if dtitle:
                                    
                                    if compfile is not None:
                                            #st.write(f'again-{file_name}')
                                            if file_name:
                                                if compfile.type=="application/vnd.openxmlformats-officedocument.wordprocessingml.document":
                                                    extn="docx"
                                                elif compfile.type=="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet":
                                                    extn='xlsx'
                                                else :
                                                    extn='pdf'
                                                #if st.button("Upload file",key='uf1'):
                                                comp_filename=f"{st.session_state['Company']}_{file_name}.{extn}"
                                                file_name=f"{file_name}.{extn}"
                                                with open(os.path.join("comp_docs",comp_filename),"wb") as f: 
                                                    f.write(compfile.getbuffer())
                                                
                                                Reveiew=modif_comp_doc(roid,dtitle,dremarks,file_name,ddoctype)                                        
                                            else:
                                                st.info("Enter File Name")    
                                    else:
                                        #st.write(f'befor-{file_name}')
                                        file_name=None
                                        #st.write(f'then-{file_name}')
                                            #reviws_table.add_row({"Criteria":"criteria","Condition":"condition","Cause":"cause","Effect":"effect"})
                                        Reveiew=modif_comp_doc(roid,dtitle,dremarks,file_name,ddoctype)                                        
                                else:
                                    st.info("Please Enter -Title. It is Mandatory field")

                            
                           
                    else:
                        st.info('Select a Record to Modify ....')
                        
                elif crud=='View':
                    #st.markdown("""---""")
                    if selected:
                        filename=selected[0]['File_Ref']
                        com_filename=f"{st.session_state['Company']}_{filename}"
                                    
                        if filename:
                                        
                            with open(os.path.join("comp_docs",com_filename), 'rb') as f:
                                st.download_button('Download Attachment', f, file_name=filename,key="dlcompfile")    
                    
                else:
                    if selected:
                        st.success('Are you sure you want to Delete Selected Record')
                        if st.button("Delete Selected Record",key='delcompdoc'):
                            rid=selected[0]['id']
                            rdel=del_comp_doc(rid)
                    else:
                        st.info('Select a Record to Delete ....')

                  
            else:
                st. success(docs_ops)
                auditid=int(st.session_state['AuditID'])
                crud=st.radio("",('View','Add New','Modify','Delete'),horizontal=True,key='strcruda')
                df=get_audit_docs(st.session_state['AuditID'])
                builder = GridOptionsBuilder.from_dataframe(df)
                builder.configure_pagination(enabled=True,paginationAutoPageSize=False,paginationPageSize=10)
                builder.configure_selection(selection_mode="single",use_checkbox=True)
                        #builder.configure_default_column(editable=True)
                go = builder.build()
                        #uses the gridOptions dictionary to configure AgGrid behavior.
                grid_response=AgGrid(df, gridOptions=go,update_mode= (GridUpdateMode.SELECTION_CHANGED|GridUpdateMode.MODEL_CHANGED))
                        #selelcted row to show in audit AGGrid
                selected = grid_response['selected_rows']
                #st.dataframe(selected)
                           
                if crud=='Add New':
                    st.success('Enter details to Add New Record')
                    #st.write(st.session_state['AuditID'])
                    with st.form("Add Audit docs",clear_on_submit=True):
                        dtitle=st.text_input("Enter Title",key='dtitlea')
                        dremarks=st.text_input("Enter Remarks",key='dremarksa')
                        c1,c2 =st.columns(2)
                        with c1:
                            ddoctype=st.selectbox("Select Docuement / Information Type",('Other','Scope & Objective','Organisation Background','Minutes of Meetings',
                                                                                         'Interviews','Risk Analysis','Management Represenatations','Process Walk Through'),key='sbadda')
                        with c2:
                            compfile=st.file_uploader("Upload File",type=['pdf','xlsx','docx'],key='compfilea')
                            
                            file_name=st.text_input("Enter File Name without extention...Name should be Unique",key='comfilnamea')
                        submitted_coma = st.form_submit_button("Submit")
                        if submitted_coma:
                            if dtitle:
                                if compfile is not None:
                                        if file_name:
                                            if compfile.type=="application/vnd.openxmlformats-officedocument.wordprocessingml.document":
                                                extn="docx"
                                            elif compfile.type=="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet":
                                                extn='xlsx'
                                            else :
                                                extn='pdf'
                                            #if st.button("Upload file",key='uf1'):
                                            #comp_filename=f"{auditid}_{file_name}.{extn}"
                                            comp_filename=f"{st.session_state['Company']}_{file_name}.{extn}"
                                            file_name=f"{file_name}.{extn}"
                                            with open(os.path.join("audit_docs",comp_filename),"wb") as f: 
                                                f.write(compfile.getbuffer())
                                            Reveiew=add_audit_doc(dtitle,dremarks,file_name,ddoctype,auditid)                                        
                                        else:
                                            st.info("Enter File Name")    
                                else:
                                    file_name=None
                                        #reviws_table.add_row({"Criteria":"criteria","Condition":"condition","Cause":"cause","Effect":"effect"})
                                    Reveiew=add_audit_doc(dtitle,dremarks,file_name,ddoctype,auditid)                                        
                            else:
                                st.info("Please Enter -Title. It is Mandatory field")

                           
                elif crud=='Modify':
                    if selected:
                        st.success('Enter details to Modify Selected Record')
                        with st.form("Mdify Audit Doc",clear_on_submit=True):
                            dtitle=st.text_input("Enter New Title",key='dtitlema',value=selected[0]['Title'])
                            dremarks=st.text_input("Enter New Remarsk",key='dremarksma',value=selected[0]['Remarks'])
                            roid=selected[0]['id']
                            c1,c2 =st.columns(2)
                            with c1:
                                ddoctype=st.selectbox("Select Docuement / Information Type",('Other','Scope & Objective','Organisation Background','Minutes of Meetings',
                                                                                         'Interviews','Risk Analysis','Management Represenatations','Process Walk Through'),key='sbadda')
                  
                            with c2:
                                compfile=st.file_uploader("Upload File",type=['pdf','xlsx','docx'],key='compfilema')
                                st.write(f"Uploaded filename: {selected[0]['File_Ref']}")
                                #if selected[0]['File_Ref']:
                                    #file_name=selected[0]['File_Ref']
                                    #st.write(f"Uploaded filename: {file_name}")
                                file_name=st.text_input("Enter File Name without extention...Name should be Unique",key='comfilnamema')
                                #else: 
                                    #file_name=st.text_input("Enter File Name without extention...Name should be Unique",key='comfilnamem2')
                            submitted_com_moda =st.form_submit_button("Submit")
                            if submitted_com_moda:
                                #st.write(file_name)
                                if dtitle:
                                    
                                    if compfile is not None:
                                            #st.write(f'again-{file_name}')
                                            if file_name:
                                                if compfile.type=="application/vnd.openxmlformats-officedocument.wordprocessingml.document":
                                                    extn="docx"
                                                elif compfile.type=="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet":
                                                    extn='xlsx'
                                                else :
                                                    extn='pdf'
                                                #if st.button("Upload file",key='uf1'):
                                                comp_filename=f"{st.session_state['Company']}_{file_name}.{extn}"
                                                file_name=f"{file_name}.{extn}"
                                                with open(os.path.join("audit_docs",comp_filename),"wb") as f: 
                                                    f.write(compfile.getbuffer())
                                                
                                                Reveiew=modif_audit_doc(roid,dtitle,dremarks,file_name,ddoctype)                                        
                                            else:
                                                st.info("Enter File Name")    
                                    else:
                                        #st.write(f'befor-{file_name}')
                                        file_name=None
                                        #st.write(f'then-{file_name}')
                                            #reviws_table.add_row({"Criteria":"criteria","Condition":"condition","Cause":"cause","Effect":"effect"})
                                        Reveiew=modif_audit_doc(roid,dtitle,dremarks,file_name,ddoctype)                                        
                                else:
                                    st.info("Please Enter -Title. It is Mandatory field")

                            
                           
                    else:
                        st.info('Select a Record to Modify ....')
                        
                elif crud=='View':
                    #st.markdown("""---""")
                    if selected:
                        filename=selected[0]['File_Ref']
                        #com_filename=f"{auditid}_{filename}"
                        com_filename=f"{st.session_state['Company']}_{filename}"          
                        if filename:
                                        
                            with open(os.path.join("audit_docs",com_filename), 'rb') as f:
                                st.download_button('Download Attachment', f, file_name=filename,key="dlcompfilea")    
                    
                else:
                    if selected:
                        st.success('Are you sure you want to Delete Selected Record')
                        if st.button("Delete Selected Record",key='delcompdoca'):
                            rid=selected[0]['id']
                            rdel=del_audit_doc(rid)
                    else:
                        st.info('Select a Record to Delete ....')

                
                
        elif sel_option=='Audit Observations':
            #st.success('Update Audit Observations...')
            show_Audit_observations()
            
        elif sel_option=='Audit Summary':
            show_Audit_summary()
        
        elif sel_option=='Close Audit':
            auditid=int(st.session_state['AuditID'])
            pending_qs=get_pending_Compliance(auditid)
            if pending_qs.empty:
                st.success("All Audit Observations are Closed ;so Now You can Close this Audit ")
                if st.button("Close Audit",key='closeauit'):
                    cl=closed_audit(auditid)
                    st.success(cl)
                    st.success("Login Again")
                    st.session_state['loggedIn'] = False
                    loginuser=""
            else:
                st.info("Following are Open Audit Observations, First Close all the Open Items & then you can Close Audit")
                st.dataframe(pending_qs)
                
        else:
                #do V&V
            optionsdf=get_dsname(int(st.session_state['AuditID']))
            #add blank row at begining of list
            optionsdf.loc[-1]=['---']
            optionsdf.index=optionsdf.index+1
            optionsdf.sort_index(inplace=True)
            d_sname=st.selectbox("Select Data Set to Audit",optionsdf,key="selectdsname")
            ds_name=f"{st.session_state['Company']}_{(st.session_state['AuditID'])}_{d_sname}"
            #select dataset 
        
                
            if d_sname=="---":
                st.info("Select Data Set to Audit")
            else:
                
                df=get_dataset(ds_name)
                df.drop(['Status', 'Sampled'], axis=1,inplace=True)
                tab1,tab2 =st.tabs(["   Vouching & Verification  ","   Analytical & Other Reviews   "])
                with tab1:
                    st.header(d_sname)
                    st.success("Select Row to Audit")
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
                    if selected:
                        #st.info("selected")
                        
                        with st.form("Auditing",clear_on_submit=True):
                                                    
                            colum1,colum2 =st.columns(2)
                            with colum1:
                                #selected = grid_response['data']
                                selected_df = pd.DataFrame(selected)
                                
                                #rowinedx if added delet
                                if '_selectedRowNodeInfo' in selected_df.columns:
                                    selected_df.drop(['_selectedRowNodeInfo'], axis=1,inplace=True)
                                #st.dataframe(selected_df)
                                data_id=int(selected_df.iloc[0,0])
                                #st.write(data_id)
                                #st.dataframe(selected_df.describe())
                                #st.write(selected_df.info())
                                selected_df=selected_df.applymap(str)
                                selected_df=selected_df.transpose()
                                selected_df["Field"]=selected_df.index
                                selected_df.rename(columns={0:'Value'},inplace=True)
                                selected_df['Audit_Value']=selected_df['Value']
                                selected_df["Cause"]=''
                                selected_df["Effect"]=''
                                selected_df=selected_df[['Field','Value','Audit_Value','Cause','Effect']]
                                #selected_df.reset_index()
                                #selected_df=selected_df.rename(columns={'0':'Value'},inplace=True)
                                #st.dataframe(selected_df)  
                                #show Vouching AGGrid
                                builder_Audit=GridOptionsBuilder.from_dataframe(selected_df)
                                #builder_Audit.configure_default_column(editable=True)
                                builder_Audit.configure_columns((['Audit_Value','Cause','Effect']),editable=True)
                                go_audit = builder_Audit.build()
                                st.success("Vouching...If values are wrong...Double click to enter correct value.")
                                #audited=AgGrid(selected_df, gridOptions=go_audit,update_mode= GridUpdateMode.VALUE_CHANGED,height = 80)
                                audited=AgGrid(selected_df, gridOptions=go_audit,update_mode=(GridUpdateMode.VALUE_CHANGED|GridUpdateMode.SELECTION_CHANGED))
                                #st.write(veri
                                audited_data=audited['data']
                                #df_audited_data=pd.DataFrame(audited_data)
                                #aud_df=pd.DataFrame(audited_data)
                                #st.dataframe(df_audited_data)
                                #st.write(audited_data)
                            with colum2:
                                currentime=datetime.now()
                                #Verification
                                st.success("Check Verification if Criteria is met, else keep Unchecked.")
                                df_verif=get_verification(d_sname,int(st.session_state['AuditID']))
                                df_verif["Cause"]=''
                                df_verif["Effect"]=''
                                df_verif.drop(['Risk_Weight','Risk_Category'], axis=1,inplace=True)
                                
                                builder_verif=GridOptionsBuilder.from_dataframe(df_verif)
                                builder_verif.configure_selection(selection_mode="multiple",use_checkbox=True)
                                builder_verif.configure_columns((['Cause','Effect']),editable=True)
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
                                df_selected_ver.rename(columns={'Verification_Criteria':'Criteria'},inplace=True)
                                df_selected_ver['DataSetName']=d_sname
                                df_selected_ver['CompanyName']=st.session_state['Company']
                                df_selected_ver['Condition']="Yes"
                                
                                    
                                #add colums to Unselected    
                                df_unselected_ver.rename(columns={'Verification_Criteria':'Criteria'},inplace=True)
                                df_unselected_ver['DataSetName']=d_sname
                                df_unselected_ver['CompanyName']=st.session_state['Company']
                                df_unselected_ver['Condition']="No"  
                                if 'rowIndex' in df_unselected_ver.columns:
                                    df_unselected_ver.drop(['rowIndex'], axis=1,inplace=True)
                                    
                                #st.dataframe(df_selected_ver)   
                                #st.dataframe(df_unselected_ver)  
                                Submit_audit= st.form_submit_button("Submit")
                                if Submit_audit:
                                    if  audited_data.empty:
                                        st.info("Select row to Audit")
                                    else:
                                        #add  in database####new code required
                                        #data_id=int(audited_data.iloc[0,0])
                                        
                                        audited_data = audited_data[audited_data['Value'] != audited_data['Audit_Value']]
                                        audited_data['DataSetName']=d_sname
                                        audited_data['CompanyName']=st.session_state['Company']
                                        audited_data['Data_Id']=data_id
                                        audited_data['Audited_on']=currentime
                                        audited_data['Audited_By']=st.session_state['User']
                                        audited_data['Audit_Name']=st.session_state['Audit']
                                        audited_data['Audit_id']=int(st.session_state['AuditID'])
                                        audited_data['Condition']=audited_data['Field']+': Value asper Records is- '+audited_data['Value']+'; but as per Audit is-'+audited_data['Audit_Value']
                                        audited_data['Criteria']=audited_data['Field']+': should be Correct'
                                        del audited_data['Value'] 
                                                            
                                        #st.dataframe(audited_data)
                                        vouching=insert_vouching(audited_data)
                                        st.info(vouching)
                                                
                                        
                                        #for verification =yes insert in Audit_queries
                                        df_selected_ver['Data_Id']=data_id
                                        df_selected_ver['Condition']="Yes"
                                        df_selected_ver['Audited_on']=currentime
                                        df_selected_ver['Audited_By']=st.session_state['User']
                                        df_selected_ver['Audit_Name']=st.session_state['Audit']
                                        df_selected_ver['Audit_id']=int(st.session_state['AuditID'])
                                        df_selected_ver['Status']="Closed"
                                        very=add_audit_verification(df_selected_ver)
                                        
                                        
                                        #for verification =No insert in Audit_queries
                                        df_unselected_ver['Data_Id']=data_id
                                        df_unselected_ver['Condition']="No"
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
                                        #del & clear DataFrame
                                        del [[df_verif,df_unselected_ver,df_selected_ver,audited_data,selected_df,df_all_verif]]
                                        df_all_verif=pd.DataFrame()
                                        df_unselected_ver=pd.DataFrame()
                                        df_selected_ver=pd.DataFrame()
                                        audited_data=pd.DataFrame()
                                        selected_df=pd.DataFrame()
                                        df_verif=pd.DataFrame()
                                    #auditnext()
                        
                            

                with tab2:
                    st.header(d_sname)
                    #add Reveiew Remark
                    #show in DF
                    st.success("Add Analytical Review & Other Comments for Data Set...")
                    # add verification list
                    #st.markdown("""---""")
                    Reveiew=get_ar_for_ds(d_sname)  
                    st.header("Add Comments")
                    with st.form("Analytical Review & Other Comments",clear_on_submit=True):
                        criteria=st.text_input("Criteria",key='t1')
                        condition=st.text_input("Condition",key='t2')
                        cause=st.text_input("Cause",key='t3')
                        effect=st.text_input("Effect",key='t4')
                        #reviewfile=st.file_uploader("Upload Remarks/ Calculation File",type=['pdf','xlsx','docx'],key='reviewfile11')
                        
                                        
                                        #with open(os.path.join("rev_files",rev_filename), 'rb') as f:
                                            #st.download_button('Download File', f, file_name=rev_filename)    
                        c1,c2 =st.columns(2)
                        with c1:
                            risk_weight=st.slider("Risk Weights",min_value=1,max_value=10,key='slider1')
                                                            
                            if risk_weight >=1 and risk_weight <=3:
                                risk_category='Low'
                            elif risk_weight >=4 and risk_weight <=7:
                                risk_category='Medium'
                            else:
                                risk_category='High'
                        with c2:
                            #file_name=st.text_input("Enter File Name without extention...Name should be Unique",key='stfn1')
                            reviewfile=st.file_uploader("Upload Remarks/ Calculation File",type=['pdf','xlsx','docx'],key='reviewfile1')
                            #if reviewfile is not None:
                                #st.write("file_name")
                                #file_name=st.text_input("Enter File Name...Name should be Unique",key='stfn')                
                        #reviewfile=st.file_uploader("Upload Remarks/ Calculation File",type=['pdf','xlsx','docx'],key='reviewfile1')
                            #if reviewfile is not None:
                            file_name=st.text_input("Enter File Name without extention...Name should be Unique",key='stfn')
                        submitted = st.form_submit_button("Submit")                   
                        #submitted = st.button("Submit",key="sumbitform1")
                        if submitted:
                            if criteria and condition:
                                if reviewfile is not None:
                                    if file_name:
                                        if reviewfile.type=="application/vnd.openxmlformats-officedocument.wordprocessingml.document":
                                            extn="docx"
                                        elif reviewfile.type=="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet":
                                            extn='xlsx'
                                        else :
                                            extn='pdf'
                                        #if st.button("Upload file",key='uf1'):
                                        rev_filename=f"{(st.session_state['AuditID'])}{d_sname}_{file_name}.{extn}"
                                        file_name=f"{file_name}.{extn}"
                                        with open(os.path.join("rev_files",rev_filename),"wb") as f: 
                                            f.write(reviewfile.getbuffer()) 
                                        
                                        #with open(rev_filename, 'rb') as f:
                                        Reveiew=add_analytical_review(criteria,condition,cause,effect,d_sname,st.session_state['Company'],risk_weight,risk_category,file_name)
                                    else:
                                        st.info("Enter File Name")    
                                else:
                                    file_name=None
                                    #reviws_table.add_row({"Criteria":"criteria","Condition":"condition","Cause":"cause","Effect":"effect"})
                                    Reveiew=add_analytical_review(criteria,condition,cause,effect,d_sname,st.session_state['Company'],risk_weight,risk_category,file_name)
                            else:
                                st.info("Criteria & Condition are Mandatory fields")

                        
                    
                    with st.expander("View Analytical Review & Other Comments"):
                        st.success(f"Analytical Review & Other Comments for {d_sname}")
                        Reveiew=get_ar_queries(d_sname)
                        #st.dataframe(Reveiew)
                        #show Aggrid
                        builder = GridOptionsBuilder.from_dataframe(Reveiew)
                        #.loc[:, ['DataSetName','Field','Data_Id','Audit_Value','Remarks','Verification','Audit_Verification','Reply','status_update_remarks']])
                        builder.configure_pagination(enabled=True,paginationPageSize=10,paginationAutoPageSize=False)
                        builder.configure_selection(selection_mode="single",use_checkbox=True)
                                    #builder.configure_default_column(editable=True)
                        #cc=JsCode("return{color: 'red'}")
                        #builder.configure_columns(['Criteria','Condition','Cause','Effect','Reply'],cellStyle={'color': 'red'})
                        go = builder.build()
                                    #uses the gridOptions dictionary to configure AgGrid behavior.
                        #grid_response=AgGrid(pending, gridOptions=go,update_mode= (GridUpdateMode.SELECTION_CHANGED|GridUpdateMode.MODEL_CHANGED),theme="blue")
                        grid_response=AgGrid(Reveiew, gridOptions=go,update_mode= (GridUpdateMode.SELECTION_CHANGED|GridUpdateMode.MODEL_CHANGED))
                        selected = grid_response['selected_rows']
                        #download file option
                        if selected:
                            filename=selected[0]['Review_File']
                            com_filename=f"{(st.session_state['AuditID'])}{d_sname}_{filename}"
                            #com_filename=f"{st.session_state['Company']}_{filename}"
                                   
                            if filename:
                                        
                                with open(os.path.join("rev_files",com_filename), 'rb') as f:
                                    st.download_button('Download Attachment', f, file_name=filename,key="dlcompfile")    
                    
                        #reviws_table=st.table(Reveiew)
                    st.markdown("""---""")   
                    st.info("Analyse Data")
                    ds=get_entire_dataset(ds_name)
                    ds=get_entire_dataset(ds_name)
                    with st.expander("View Statistical Summary"):
                        st.success(f"Stats Summary for {d_sname}")
                        st.dataframe(ds.describe())
                        
                    with st.expander('Analyse Data Set'):
                        st.success(f"Data Set for {d_sname}")
                        builder = GridOptionsBuilder.from_dataframe(ds)
                        builder.configure_pagination(enabled=True,paginationPageSize=15,paginationAutoPageSize=False)
                        go = builder.build()
                        AgGrid(ds,gridOptions=go)
                        csv=ds.to_csv().encode('utf-8')
                        st.download_button("Download csv file...",csv,f"{d_sname}.csv")
                
                        
                
                    
                    with st.expander('Generate Detailed Statistical Analysis Report'):
                        st.success(f"Statistical Analysis Report for {d_sname}")
                        #Click to generate pandas profiling report
                        if st.button("Generate Analytical Report"):
                            
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
        