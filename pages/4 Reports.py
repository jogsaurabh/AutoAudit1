#from turtle import color
from re import X
from PIL import Image

image = Image.open('autoaudit_t.png')
import pandas as pd  # pip install pandas openpyxl
import plotly.express as px  # pip install plotly-express
import streamlit as st  # pip install streamlit
from st_aggrid import AgGrid,DataReturnMode, GridUpdateMode, GridOptionsBuilder, JsCode, grid_options_builder
from functions import get_queries,get_ar,get_pending_queries
from functions import get_user_rights,get_active_users,add_datato_ds,get_verification,get_audit
from functions import create_user,check_login,assign_user_rights,create_company,get_company_names
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
        
        #Get entire audit data set including Verification= yes
        df_queries=get_queries(int(st.session_state['AuditID']))
        #Remove verification= Yes & keep only No
        df_queries=df_queries[(df_queries['Audit_Verification']=='No') | (df_queries['Audit_Value'].notnull() )]
        
        ds_names=get_dsname(int(st.session_state['AuditID']))
        # ---- SIDEBAR ----
        st.title("Audit Reports")
        audit_id=int(st.session_state['AuditID'])
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
            st.warning("Select Data Set ")
        else:
            #df=get_dataset(ds_name)
            tab1,tab2 =st.tabs(["Queries by Data Set ","   All Queries  "])
            with tab1:
                st.header(f"Audit Summary for {ds}")
                #get queries for selected Dataset
                df_selection = df_queries.query(
                    "DataSetName == @ds and Audit_id==@audit_id"
                    )
                df_pending_ds=df_selection.query('Status=="Pending"')
                df_DS=get_entire_dataset(f"{comp_name}_{st.session_state['AuditID']}_{ds}")
                #get only Audited DS
                df_DS_Audited=df_DS.query("Status=='Audited'")
                #merge DS with Queries to get Querysheet
                df_DS_querysheet=pd.merge(df_DS_Audited,df_selection,how="left",left_on="index",right_on="Data_Id")
                #QuerySheet for Vouching
                df_DS_querysheet_Vouching=df_DS_querysheet.drop(['Verification','Audit_Verification'],axis=1)
                df_DS_querysheet_Vouching=df_DS_querysheet_Vouching.dropna(subset=['Field'])
                #QuerySheet for Verification
                df_DS_querysheet_Verification=df_DS_querysheet.drop(['Field','Audit_Value'],axis=1)
                df_DS_querysheet_Verification=df_DS_querysheet_Verification.dropna(subset=['Verification'])
                # TOP KPI's
                total_transactions = int(df_DS[df_DS.columns[0]].count())
                audited_transactions = int(df_DS_Audited[df_DS_Audited.columns[0]].count())
                total_queries = int(df_selection[df_selection.columns[0]].count())
                pending_queries=int(df_pending_ds[df_pending_ds.columns[0]].count())
                #show KPIs
                left_column, middle_column, right_column ,last= st.columns(4)
                with left_column:
                    st.subheader("Total Transactions:",)
                    st.subheader(f"{total_transactions}")
                with middle_column:
                    st.subheader("Transactions Audited:")
                    st.subheader(f"{audited_transactions}")
                with right_column:
                    st.subheader("Total Queries:")
                    st.subheader(f"{total_queries}")
                with last:
                    st.subheader("Pending Queries:")
                    st.subheader(f"{pending_queries}")

                st.markdown("""---""")
                #Chart for Vouching Queries by Type

                vouching_queries = (
                    df_selection.groupby(by=["Field"]).count()
                )

                fig_vouching_queries = px.bar(
                    vouching_queries,
                    x="Audit_Value",
                    y=vouching_queries.index,
                    orientation="h",
                    title="<b>Vouching Queries by Mismatch Type</b>",
                    #color_discrete_sequence=["#0083B8"] * len(vouching_queries),
                    template="plotly_white",text_auto=True
                )
                fig_vouching_queries.update_layout(
                    plot_bgcolor="rgba(0,0,0,0)",
                    xaxis=(dict(showgrid=False))
                )

                #Chart for Verification Queries by Type

                verification_queries = (
                    df_selection.groupby(by=["Verification"]).count()
                )

                fig_verification_queries = px.bar(
                    verification_queries,
                    x="Audit_Verification",
                    y=verification_queries.index,
                    orientation="h",
                    title="<b>Verification Queries by Mismatch Type</b>",
                    color_discrete_sequence=["#0083B8"] * len(verification_queries),
                    template="plotly_white",text_auto=True
                )
                fig_verification_queries.update_layout(
                    plot_bgcolor="rgba(0,0,0,0)",
                    xaxis=(dict(showgrid=False))
                )
                #show charts
                col1, col2 = st.columns(2)
                with col1:
                    st.plotly_chart(fig_vouching_queries,use_container_width=True)
                    st.markdown("""---""")
                    st.subheader("List of Vouching Queries")
                    
                    #st.dataframe(df_DS_querysheet_Vouching.style.set_properties(**{'color':'red'},subset=['Field','Audit_Value'])
                    #)
                    csv=df_DS_querysheet_Vouching.to_csv().encode('utf-8')
                    
                    builder = GridOptionsBuilder.from_dataframe(df_DS_querysheet_Vouching)
                    builder.configure_column('Field',cellStyle={'color': 'red'})
                    builder.configure_column('Audit_Value',cellStyle={'color': 'red'})
                    builder.configure_column('Verification',cellStyle={'color': 'red'})
                    builder.configure_column('Audit_Verification',cellStyle={'color': 'red'})
                    builder.configure_column('Remarks',cellStyle={'color': 'red'})
                    go = builder.build()
                    #uses the gridOptions dictionary to configure AgGrid behavior.
                    grid_response=AgGrid(df_DS_querysheet_Vouching, gridOptions=go)
                    st.download_button("Download csv file",csv,f"{ds}.csv")
                    
                with col2:
                    st.plotly_chart(fig_verification_queries,use_container_width=True)
                    st.markdown("""---""")
                    st.subheader("List of Verification Queries")
                
                    #st.dataframe(df_DS_querysheet_Verification.style.set_properties(**{'color':'red'},subset=['Verification','Audit_Verification'])
                    #)
                    csv=df_DS_querysheet_Verification.to_csv().encode('utf-8')
                    builder = GridOptionsBuilder.from_dataframe(df_DS_querysheet_Verification)
                    builder.configure_column('Field',cellStyle={'color': 'red'})
                    builder.configure_column('Audit_Value',cellStyle={'color': 'red'})
                    builder.configure_column('Verification',cellStyle={'color': 'red'})
                    builder.configure_column('Audit_Verification',cellStyle={'color': 'red'})
                    builder.configure_column('Remarks',cellStyle={'color': 'red'})
                    go = builder.build()
                    #uses the gridOptions dictionary to configure AgGrid behavior.
                    grid_response=AgGrid(df_DS_querysheet_Verification, gridOptions=go)
                    st.download_button("Download csv file",csv,f"{ds}.csv")
                    
                #left_column.plotly_chart(fig_vouching_queries,use_container_width=True)
                #right_column.plotly_chart(fig_verification_queries,use_container_width=True)
                #st.dataframe(df_queries)
                #st.dataframe(df_selection)
                #st.dataframe(df_DS_Audited)
                #st.dataframe(df_DS_querysheet)


            with tab2:
                st.header(f"Audit Summary for {comp_name}")
                
                df_queries.rename(columns={'Field':'Vouching'},inplace=True)
                df_queries_groupby=df_queries.groupby(['DataSetName'])['Vouching','Verification','Id'].count().rename(columns={'Status':'Pending','Id':'Total'})
                
                df_pending_queries=get_pending_queries(audit_id)
                df_pending_queries.rename(columns={'Field':'Vouching'},inplace=True)
                df_pending_queries_groupby=df_pending_queries.groupby(['DataSetName'])['Vouching','Verification','Id'].count().rename(columns={'Status':'Pending','Id':'Total'})
                rep1,rep2 =st.columns(2)
                with rep1:
                    st.header("Audit Queries- Total")
                    st.dataframe(df_queries_groupby.style.set_properties(**{'color':'red'},subset=['Vouching','Verification','Total']))
                    st.bar_chart(df_queries_groupby)
                with rep2:
                    st.header("Audit Queries- Pending")
                    st.dataframe(df_pending_queries_groupby.style.set_properties(**{'color':'red'},subset=['Vouching','Verification','Total']))
                    st.bar_chart(df_pending_queries_groupby)
                
                st.markdown("""---""")
                st.header('Pending Audit Query List')
                #df_DS_querysheet
                #df_queries=pd.merge(df_queries,df_selection,how="left",left_on="Data_Id",right_on="index")
                builder = GridOptionsBuilder.from_dataframe(df_pending_queries)
                builder.configure_column('Field',cellStyle={'color': 'red'})
                builder.configure_column('Audit_Value',cellStyle={'color': 'red'})
                builder.configure_column('Verification',cellStyle={'color': 'red'})
                builder.configure_column('Audit_Verification',cellStyle={'color': 'red'})
                builder.configure_column('Remarks',cellStyle={'color': 'red'})
                builder.configure_pagination(enabled=True,paginationAutoPageSize=False,paginationPageSize=15)
                go = builder.build()
                #uses the gridOptions dictionary to configure AgGrid behavior.
                grid_response=AgGrid(df_pending_queries, gridOptions=go)
                csv=df_pending_queries.to_csv().encode('utf-8')
                st.download_button("Download csv file",csv,f"{ds}.csv")
                #list of AReview
                st.header('Analytical Review- Comments')
                ds_ar=get_ar(comp_name)
                builder = GridOptionsBuilder.from_dataframe(ds_ar)
                
                builder.configure_column('Review',cellStyle={'color': 'red'})
                go = builder.build()
                #uses the gridOptions dictionary to configure AgGrid behavior.
                grid_response=AgGrid(ds_ar, gridOptions=go)
                csv=ds_ar.to_csv().encode('utf-8')
                st.download_button("Download csv file",csv,f"{ds}.csv")
                

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
        