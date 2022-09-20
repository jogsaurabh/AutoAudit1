#from turtle import color
#from re import X
from docx import Document
from htmldocx import HtmlToDocx
from PIL import Image
#import streamlit.components.v1 as components
import plotly.io as pio
from jinja2 import Environment, FileSystemLoader
image = Image.open('autoaudit_t.png')
import pandas as pd  # pip install pandas openpyxl
import plotly.express as px  # pip install plotly-express
import streamlit as st  # pip install streamlit
from st_aggrid import AgGrid,DataReturnMode, GridUpdateMode, GridOptionsBuilder, JsCode, grid_options_builder
from functions import get_Summary_audit_values,get_ar_queries,get_vv_quries,get_values_id_dsn,get_audit_values,get_queries,get_ar,get_pending_queries,get_dataset_values
from functions import get_Summary_audit_values_riskweight_comp,get_Summary_audit_values_riskcategory,get_user_rights,get_active_users,add_datato_ds,get_verification,get_audit
from functions import get_Summary_audit_values_comp,get_Summary_audit_values_riskweight,create_user,check_login,assign_user_rights,create_company,get_company_names
from functions import create_dataset,add_verification_criteria,get_dsname,get_entire_dataset,get_auditee_comp
st.set_page_config(page_title="Audit Dashboard", page_icon=":bar_chart:", layout="wide")
#st.title(":bar_chart: Audit Dashboard")
st.image(image,width=250)
st.markdown("""---""")
# emojis: https://www.webfx.com/tools/emoji-cheat-sheet/

comp_name=st.session_state['Company']
report_container=st.container()
def show_report():
    with report_container:
        st.write(f"User:-{st.session_state['User']}",f"  | Company:-{st.session_state['Company']}",
                 f"  | Audit:-{st.session_state['Audit']}",f"  | Role:-{st.session_state['Role']}")
        # ---- SIDEBAR ----
        
        with st.sidebar.markdown("# Reports"):
            optionsdf=get_dsname(int(st.session_state['AuditID']))
            #add blank row at begining of list
            optionsdf.loc[-1]=['---']
            optionsdf.index=optionsdf.index+1
            optionsdf.sort_index(inplace=True)
            ds=st.selectbox("Select Data Set ",optionsdf,key="1selectdsname")
            #ds_name=f"{st.session_state['Company']}_{(st.session_state['AuditID'])}_{d_sname}"
            #select dataset 
        if ds=="---":
            st.success("Select Data Set ")
        else:
            st.title("Audit Reports")
            tab1,tab2 =st.tabs(["Reports by Data Set ","   Summary Report for Audit  "])
            with tab1:
                #st.header(f"Audit Summary for {ds}")
                #get queries for selected Dataset
                
                audit_id=int(st.session_state['AuditID'])
                st.success(f"Audit Summary for {ds}")
                #st.markdown("""---""")
                #df=get_dataset(ds_name)
                values=get_dataset_values(f"{comp_name}_{st.session_state['AuditID']}_{ds}")
                totalrecords= values['total_records']
                totalaudit=values['total_audited']
                #st.info(totalrecords)
                #st.info(totalaudit)
                #dsvalues=get_audit_values(int(st.session_state['AuditID']))
                auditvalues=get_values_id_dsn(int(st.session_state['AuditID']),ds)
                #st.info(dsvalues)
                #st.info(auditvalues)
                total_queries=auditvalues['total_queries_vv'] + auditvalues['total_queries_ar']
                totalrisk=auditvalues['auditrisk_total']*totalaudit
                auditrisk=auditvalues['auditrisk_audited']
                if totalrisk==0:
                    riskpercent='0.00 %'
                else:
                    riskpercent='{percent:.2%}'.format(percent=auditrisk/totalrisk)
                #show KPIs
                col1,col2,col3= st.columns(3)
                with col1:
                    new_title = '<p style="font-family:sans-serif; color:Navy; font-size: 20px;">Total Transactions:</p>'
                    st.markdown(new_title, unsafe_allow_html=True)
                        #st.markdown('<style>p{color:red;}</style>"Total Transactions:"',unsafe_allow_html=True)
                    st.subheader(f"{totalrecords}")
                    new_title = '<p style="font-family:sans-serif; color:Navy; font-size: 20px;">Total Risk Score:</p>'
                    st.markdown(new_title, unsafe_allow_html=True)
                    st.subheader(f"{totalrisk}")
                with col2:
                    new_title = '<p style="font-family:sans-serif; color:Navy; font-size: 20px;">Transactions Audited:</p>'
                    st.markdown(new_title, unsafe_allow_html=True)
                        #st.subheader("Transactions Audited:")
                    st.subheader(f"{totalaudit}")
                    new_title = '<p style="font-family:sans-serif; color:Navy; font-size: 20px;">Audited Risk Score:</p>'
                    st.markdown(new_title, unsafe_allow_html=True)
                    st.subheader(f"{auditrisk}")
                with col3:
                    new_title = '<p style="font-family:sans-serif; color:Red; font-size: 20px;">Total Queries:</p>'
                    st.markdown(new_title, unsafe_allow_html=True)
                        #st.subheader("Total Queries:")
                    new_title = f'<p style="font-family:sans-serif;font-weight: bold; color:Red; font-size: 27px;">{total_queries}</p>'
                    st.markdown(new_title, unsafe_allow_html=True)
                    #st.subheader(f"{total_queries}")
                    new_title = '<p style="font-family:sans-serif; color:Red; font-size: 20px;">Risk Percentage:</p>'
                    st.markdown(new_title, unsafe_allow_html=True)
                    #st.subheader(f"{riskpercent}")
                    new_title = f'<p style="font-family:sans-serif;font-weight: bold; color:Red; font-size: 27px;">{riskpercent}</p>'
                    st.markdown(new_title, unsafe_allow_html=True)
                #st.markdown("""---""")
                #charts for V&V
                
                st.success(f"Queries Summary for {ds}")
                #get DF for vouching & verification
                auditdf_1=get_Summary_audit_values(int(st.session_state['AuditID']),ds)
                dict={'Criteria':'Analytical Review & Other','Total Queries':auditvalues['total_queries_ar']}
                auditdf_1=auditdf_1.append(dict,ignore_index=True)
                col1, col2= st.columns(2)
                with col1:
                    st.bar_chart(auditdf_1,x='Criteria',y='Total Queries')
                with col2:
                    st.dataframe(auditdf_1)
                    #st.bar_chart(auditdf,x='Criteria',y='Total Queries')
                st.success(f"Risk Based Audit Summary for {ds}")
                auditdf_r=get_Summary_audit_values_riskweight(int(st.session_state['AuditID']),ds)
                col1, col2= st.columns(2)
                with col1:
                
                    st.bar_chart(auditdf_r,x='Criteria',y='Total Risk Weight')
                with col2:
                    st.dataframe(auditdf_r)
                #by Risk Category
                #auditdf=get_Summary_audit_values_riskcategory(int(st.session_state['AuditID']),ds)
                
                #col1, col2= st.columns(2)
                #with col1:
                
                    #st.bar_chart(auditdf,x=['Criteria','Risk_Category'],y='Total Risk Weight')
                #with col2:
                    
                    #st.dataframe(auditdf)
                st.markdown("""---""")
                st.success(f"View / Download - Query List for {ds}...")
                with st.expander("Voching & Verification Queries"):
                        
                        queries_df=get_vv_quries(f"{comp_name}_{st.session_state['AuditID']}_{ds}",ds,int(st.session_state['AuditID']))
                        st.dataframe(queries_df.style.set_properties(**{'color':'red'},subset=['Criteria','Condition','Cause','Effect','Risk_Weight',
                                                                                            'Risk_Category']))
                        csv=queries_df.to_csv().encode('utf-8')
                        st.download_button("Download csv file",csv,f"{ds}.csv")
                #get AR queries lit
                #st.success("Query List of Analytical Reviw & Other Remarks...")
                with st.expander("Analytical Reviw & Other Remarks"):
                    queries_df=get_ar_queries(ds)
                    st.dataframe(queries_df.style.set_properties(**{'color':'red'},subset=['Criteria','Condition','Cause','Effect','Risk_Weight',
                                                                                        'Risk_Category']))
                    csv=queries_df.to_csv().encode('utf-8')
                    st.download_button("Download csv file",csv,f"{ds}.csv")
                

            with tab2:
                st.success(f"Audit Summary for {comp_name} -{st.session_state['Audit']}")
                auditvalues=get_audit_values(int(st.session_state['AuditID']))
                totalvvqueries=auditvalues['total_queries_vv']
                totalarqueries=auditvalues['total_queries_ar']
                col1,col2= st.columns(2)
                with col1:
                    new_title = '<p style="font-family:sans-serif; color:Navy; font-size: 20px;">Vouching & Verification Queries:</p>'
                    st.markdown(new_title, unsafe_allow_html=True)
                        #st.markdown('<style>p{color:red;}</style>"Total Transactions:"',unsafe_allow_html=True)
                    new_title = f'<p style="font-family:sans-serif; color:Red; font-size: 27px;">{totalvvqueries}</p>'
                    st.markdown(new_title, unsafe_allow_html=True)
                    
                with col2:
                    new_title = '<p style="font-family:sans-serif; color:Navy; font-size: 20px;">Analytical Review& Other Queries:</p>'
                    st.markdown(new_title, unsafe_allow_html=True)
                        #st.subheader("Transactions Audited:")
                    new_title = f'<p style="font-family:sans-serif;color:Red; font-size: 27px;">{totalarqueries}</p>'
                    st.markdown(new_title, unsafe_allow_html=True)
                #charts for V&V
                
                st.success("Vouching & Verification - Queries Summary by Dataset")
                #get DF for vouching & verification
                auditdf=get_Summary_audit_values_comp(int(st.session_state['AuditID']))
                col1, col2= st.columns(2)
                with col1:
                    st.bar_chart(auditdf,x='Data Set Name',y='Total Queries')
                with col2:
                    st.dataframe(auditdf)
                    #st.bar_chart(auditdf,x='Criteria',y='Total Queries')
                st.success("Vouching & Verification - Risk Based Audit Summary by Data Set")
                auditdf=get_Summary_audit_values_riskweight_comp(int(st.session_state['AuditID']))
                col1, col2= st.columns(2)
                with col1:
                
                    st.bar_chart(auditdf,x='Data Set Name',y='Total Risk Weight')
                with col2:
                    st.dataframe(auditdf,)
         #download word file report
            if st.button("Generate Report in Word",key="grw"):
                fname=f"{ds}{comp_name}{st.session_state['AuditID']}"
                #st.write(fname)
                # 2. Create a template Environment
                env = Environment(loader=FileSystemLoader('templates'))
                # 3. Load the template from the Environment
                template = env.get_template('template.html')
                # 4. Render the template with variables
                chart1=px.bar(
                        auditdf_1,
                        x="Criteria",
                        y="Total Queries",
                        #orientation="h",
                        title="<b>Total Queries by Criteria</b>",
                        color_discrete_sequence=["#0083B8"] * len(auditdf),
                        template="plotly_white",text_auto=True
                    )
                chart1.update_layout(
                        plot_bgcolor="rgba(0,0,0,0)")
                        #xaxis=(dict(showgrid=False)))
                fchart1=f"{fname}c1.png"
                pio.write_image(chart1,fchart1)
                #st.plotly_chart(chart1,use_container_width=True)
                
                #second chart
                chart2=px.bar(
                        auditdf_r,
                        x="Criteria",
                        y="Total Risk Weight",
                        #orientation="h",
                        title="<b>Risked Based Audit Summary</b>",
                        color_discrete_sequence=["#0083B8"] * len(auditdf),
                        template="plotly_white",text_auto=True
                    )
                chart2.update_layout(
                        plot_bgcolor="rgba(0,0,0,0)")
                        #xaxis=(dict(showgrid=False)))
                fchart2=f"{fname}c2.png"
                pio.write_image(chart1,fchart2)
                #st.plotly_chart(chart1,use_container_width=True)
                
                
                titler=f"Company:- {comp_name}| Audit:- {st.session_state['Audit']} | Data Set:- {ds}"
                html1 = template.render(logo='autoaudit_t.png',
                                        page_title_text=titler,
                                        title_text='Summary Observations',
                                        Total_tansactions=totalrecords,
                                        Transactions_Audited=totalaudit,
                                        Total_Queries=total_queries,
                                        TotalRiskScore=totalrisk,
                                        AuditedRiskScore=auditrisk,
                                        RiskPercentage=riskpercent,
                                        DF1_heading=f"Query Summary for: {ds}",
                                        dataurl1=fchart1,                                
                                        df1=auditdf_1.to_html(),
                                        DF2_heading=f"Risk Based Audit Summary for: {ds}",
                                        df2=auditdf_r.to_html(),
                                        dataurl2=fchart2)
                                        
                #docx to rport
                document = Document()
                new_parser = HtmlToDocx()
                document=new_parser.parse_html_string(html1)
                document.save(fname)
                #st.markdown(html1, unsafe_allow_html=True)
                #components.html(html1, width=800, height=400,scrolling=True)
                with open(fname,'rb') as f:
                    st.download_button('Download Reports',f,'report.docx')

             

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
                    show_report()    
            else:
                #st.title("Login")
                show_login_page()
        