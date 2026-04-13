import streamlit as st 
import pandas as pd 
import mysql.connector 
import sqlite3
import plotly.express as px 
from datetime import datetime 
 
# ───────────────────────────────────────────────────────────── 
# CUSTOM CSS FOR BETTER LOOK 
# ───────────────────────────────────────────────────────────── 
def local_css(file_name):
    with open(file_name) as f:
        st.markdown(f'<style>{f.read()}</style>', unsafe_allow_html=True)

# Load custom CSS if exists, else use inline
try:
    local_css("style.css")
except:
    st.markdown("""
    <style>
    .main-header {
        font-size: 3rem;
        color: #2E8B57;
        text-align: center;
        font-weight: bold;
        margin-bottom: 2rem;
    }
    .metric-card {
        background-color: #f0f8ff;
        padding: 1rem;
        border-radius: 10px;
        border: 2px solid #2E8B57;
        text-align: center;
        margin: 0.5rem;
    }
    .metric-value {
        font-size: 2rem;
        color: #FF6347;
        font-weight: bold;
    }
    .metric-label {
        font-size: 1rem;
        color: #2E8B57;
    }
    .sidebar .sidebar-content {
        background-color: #f5f5f5;
    }
    .stButton>button {
        background-color: #2E8B57;
        color: white;
        border-radius: 5px;
        border: none;
        padding: 0.5rem 1rem;
    }
    .stButton>button:hover {
        background-color: #228B22;
    }
    .stSelectbox, .stTextInput, .stNumberInput {
        margin-bottom: 1rem;
    }
    </style>
    """, unsafe_allow_html=True)

# ───────────────────────────────────────────────────────────── 
# DATABASE CONNECTION 
# ───────────────────────────────────────────────────────────── 
def get_connection():
    return sqlite3.connect('food_wastage.db', check_same_thread=False)

def run_query(query, params=None):
    conn = get_connection()
    df = pd.read_sql_query(query, conn, params=params)
    conn.close()
    return df

def run_command(query, params=None):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(query, params or [])
    conn.commit()
    conn.close()
 
# ───────────────────────────────────────────────────────────── 
# APP CONFIGURATION 
# ───────────────────────────────────────────────────────────── 
st.set_page_config( 
    page_title='Food Wastage Management System', 
    page_icon='🍱', 
    layout='wide' 
) 
 
# Custom Header
st.markdown('<h1 class="main-header">🍱 Local Food Wastage Management System</h1>', unsafe_allow_html=True)
st.markdown('<p style="text-align: center; font-size: 1.2rem; color: #666;">Reducing food waste, one meal at a time.</p>', unsafe_allow_html=True)
st.markdown('---') 
 
# ───────────────────────────────────────────────────────────── 
# SIDEBAR NAVIGATION 
# ───────────────────────────────────────────────────────────── 
st.sidebar.title('🍽️ Navigation')
st.sidebar.markdown('---')
page = st.sidebar.selectbox('📌 Choose a Section', [ 
    '🏠 Home / Dashboard', 
    '📊 SQL Query Results', 
    '🔍 Filter Food Listings', 
    '📋 CRUD Operations', 
    '📞 Contact Directory' 
])
st.sidebar.markdown('---')
st.sidebar.info('💡 Use this app to manage food donations and reduce wastage efficiently.') 
 
# ───────────────────────────────────────────────────────────── 
# PAGE 1: HOME / DASHBOARD 
# ───────────────────────────────────────────────────────────── 
if page == '🏠 Home / Dashboard': 
    st.header('📈 Dashboard Overview') 
    st.markdown('Welcome to your food wastage management dashboard. Here you can see key metrics and visualizations.')
 
    # Metrics in styled cards
    col1, col2, col3, col4 = st.columns(4) 
    with col1: 
        total_providers = run_query('SELECT COUNT(*) AS cnt FROM providers').iloc[0]['cnt'] 
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-value">{total_providers}</div>
            <div class="metric-label">Total Providers</div>
        </div>
        """, unsafe_allow_html=True)
    with col2: 
        total_receivers = run_query('SELECT COUNT(*) AS cnt FROM receivers').iloc[0]['cnt'] 
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-value">{total_receivers}</div>
            <div class="metric-label">Total Receivers</div>
        </div>
        """, unsafe_allow_html=True)
    with col3: 
        total_food = run_query('SELECT SUM(Quantity) AS cnt FROM food_listings').iloc[0]['cnt'] 
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-value">{int(total_food) if total_food else 0}</div>
            <div class="metric-label">Total Food Available (qty)</div>
        </div>
        """, unsafe_allow_html=True)
    with col4: 
        total_claims = run_query('SELECT COUNT(*) AS cnt FROM claims').iloc[0]['cnt'] 
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-value">{total_claims}</div>
            <div class="metric-label">Total Claims Made</div>
        </div>
        """, unsafe_allow_html=True)
 
    st.markdown('---') 
 
    # Charts in containers
    with st.container():
        st.subheader('📊 Claims Status Distribution') 
        df_status = run_query('SELECT Status, COUNT(*) AS Count FROM claims GROUP BY Status') 
        if not df_status.empty:
            fig1 = px.pie(df_status, names='Status', values='Count', title='Claims by Status', 
                         color_discrete_sequence=px.colors.sequential.RdBu)
            st.plotly_chart(fig1, use_container_width=True)
        else:
            st.info('No claims data available.')
 
    with st.container():
        st.subheader('🏙️ Top 10 Cities by Food Listings') 
        df_city = run_query('SELECT Location, COUNT(*) AS Listings FROM food_listings GROUP BY Location ORDER BY Listings DESC LIMIT 10') 
        if not df_city.empty:
            fig2 = px.bar(df_city, x='Location', y='Listings', title='Food Listings by City', 
                         color='Listings', color_continuous_scale='Viridis')
            st.plotly_chart(fig2, use_container_width=True)
        else:
            st.info('No food listings data available.') 
 
# ───────────────────────────────────────────────────────────── 
# PAGE 2: SQL QUERY RESULTS 
# ───────────────────────────────────────────────────────────── 
elif page == '📊 SQL Query Results': 
    st.header('📊 SQL Query Results') 
    st.markdown('Select and run predefined queries to analyze your data.')
 
    queries = { 
        'Q1: Providers & Receivers per City': ''' 
            SELECT p.City, 
                   COUNT(DISTINCT p.Provider_ID) AS Total_Providers, 
                   COUNT(DISTINCT r.Receiver_ID) AS Total_Receivers 
            FROM providers p 
            LEFT JOIN receivers r ON p.City = r.City 
            GROUP BY p.City ORDER BY Total_Providers DESC''', 
 
        'Q2: Provider Type Contribution': ''' 
            SELECT p.Type AS Provider_Type, 
                   SUM(f.Quantity) AS Total_Quantity_Donated 
            FROM providers p 
            JOIN food_listings f ON p.Provider_ID = f.Provider_ID 
            GROUP BY p.Type ORDER BY Total_Quantity_Donated DESC''', 
 
        'Q3: Providers in Mumbai': ''' 
            SELECT Name, Type, Address, City, Contact 
            FROM providers WHERE City = 'Mumbai' ORDER BY Name''', 
 
        'Q4: Receivers with Most Claims': ''' 
            SELECT r.Name, r.Type, r.City, COUNT(c.Claim_ID) AS Total_Claims 
            FROM receivers r JOIN claims c ON r.Receiver_ID = c.Receiver_ID 
            GROUP BY r.Receiver_ID, r.Name, r.Type, r.City 
            ORDER BY Total_Claims DESC LIMIT 10''', 
 
        'Q5: Total Food Available': ''' 
            SELECT SUM(Quantity) AS Total_Available_Quantity FROM food_listings''', 
 
        'Q6: City with Most Food Listings': ''' 
            SELECT Location AS City, COUNT(Food_ID) AS Total_Listings, 
                   SUM(Quantity) AS Total_Quantity 
            FROM food_listings GROUP BY Location ORDER BY Total_Listings DESC''', 
 
        'Q7: Most Common Food Types': ''' 
            SELECT Food_Type, COUNT(Food_ID) AS Count, SUM(Quantity) AS Total_Quantity 
            FROM food_listings GROUP BY Food_Type ORDER BY Count DESC''', 
 
        'Q8: Claims per Food Item': ''' 
            SELECT f.Food_Name, f.Quantity, COUNT(c.Claim_ID) AS Total_Claims 
            FROM food_listings f LEFT JOIN claims c ON f.Food_ID = c.Food_ID 
            GROUP BY f.Food_ID, f.Food_Name, f.Quantity 
            ORDER BY Total_Claims DESC''', 
 
        'Q9: Provider with Most Successful Claims': ''' 
            SELECT p.Name, p.Type, p.City, COUNT(c.Claim_ID) AS Successful_Claims 
            FROM providers p 
            JOIN food_listings f ON p.Provider_ID = f.Provider_ID 
            JOIN claims c ON f.Food_ID = c.Food_ID 
            WHERE c.Status = 'Completed' 
            GROUP BY p.Provider_ID, p.Name, p.Type, p.City 
            ORDER BY Successful_Claims DESC LIMIT 10''', 
 
        'Q10: Claim Status Percentage': ''' 
            SELECT Status, COUNT(*) AS Count, 
                   ROUND(COUNT(*) * 100.0 / (SELECT COUNT(*) FROM claims), 2) AS Percentage 
            FROM claims GROUP BY Status ORDER BY Count DESC''', 
 
        'Q11: Avg Quantity per Receiver': ''' 
            SELECT r.Name, ROUND(AVG(f.Quantity), 2) AS Avg_Quantity_Per_Claim 
            FROM receivers r 
            JOIN claims c ON r.Receiver_ID = c.Receiver_ID 
            JOIN food_listings f ON c.Food_ID = f.Food_ID 
            GROUP BY r.Receiver_ID, r.Name 
            ORDER BY Avg_Quantity_Per_Claim DESC''', 
 
        'Q12: Meal Type Claimed Most': ''' 
            SELECT f.Meal_Type, COUNT(c.Claim_ID) AS Total_Claims, 
                   SUM(f.Quantity) AS Total_Quantity 
            FROM food_listings f JOIN claims c ON f.Food_ID = c.Food_ID 
            GROUP BY f.Meal_Type ORDER BY Total_Claims DESC''', 
 
        'Q13: Total Donation by Each Provider': ''' 
            SELECT p.Name, p.Type, p.City, SUM(f.Quantity) AS Total_Donated 
            FROM providers p JOIN food_listings f ON p.Provider_ID = f.Provider_ID 
            GROUP BY p.Provider_ID, p.Name, p.Type, p.City 
            ORDER BY Total_Donated DESC''', 
 
        # Replace CURDATE() and DATE_ADD with SQLite version
'Q14: Food Expiring in Next 7 Days': '''
    SELECT Food_Name, Quantity, Expiry_Date, Location, Food_Type, Meal_Type
    FROM food_listings
    WHERE Expiry_Date BETWEEN date('now') AND date('now', '+7 days')
    ORDER BY Expiry_Date ASC''',

# Replace DATE_FORMAT with SQLite version
'Q15: Monthly Trend of Claims': '''
    SELECT strftime('%Y-%m', Timestamp) AS Month,
           COUNT(c.Claim_ID) AS Total_Claims,
           SUM(f.Quantity) AS Total_Quantity_Claimed
    FROM claims c JOIN food_listings f ON c.Food_ID = f.Food_ID
    GROUP BY strftime('%Y-%m', Timestamp)
    ORDER BY Month ASC''', 
    } 
 
    selected_query = st.selectbox('📋 Select a Query to View', list(queries.keys())) 
    if st.button('🚀 Run Query', key='run_query'): 
        with st.spinner('Running query...'):
            df = run_query(queries[selected_query]) 
        if not df.empty:
            st.dataframe(df, use_container_width=True) 
            st.success(f'✅ Returned {len(df)} rows.')
        else:
            st.warning('⚠️ No data returned for this query.') 
 
# ───────────────────────────────────────────────────────────── 
# PAGE 3: FILTER FOOD LISTINGS 
# ───────────────────────────────────────────────────────────── 
elif page == '🔍 Filter Food Listings': 
    st.header('🔍 Filter Food Listings') 
    st.markdown('Use the filters below to find specific food listings.')
 
    cities = run_query('SELECT DISTINCT Location FROM food_listings ORDER BY Location')['Location'].tolist() 
    food_types = run_query('SELECT DISTINCT Food_Type FROM food_listings ORDER BY Food_Type')['Food_Type'].tolist() 
    meal_types = run_query('SELECT DISTINCT Meal_Type FROM food_listings ORDER BY Meal_Type')['Meal_Type'].tolist() 
 
    with st.expander('🔧 Filter Options', expanded=True):
        col1, col2, col3 = st.columns(3) 
        with col1: 
            selected_city = st.selectbox('🏙️ Select City', ['All'] + cities) 
        with col2: 
            selected_food_type = st.selectbox('🍽️ Food Type', ['All'] + food_types) 
        with col3: 
            selected_meal_type = st.selectbox('🍲 Meal Type', ['All'] + meal_types) 
 
    query = '''SELECT f.Food_ID, f.Food_Name, f.Quantity, f.Expiry_Date, 
                      f.Location, f.Food_Type, f.Meal_Type, p.Name AS Provider, 
                      p.Contact AS Provider_Contact 
               FROM food_listings f 
               JOIN providers p ON f.Provider_ID = p.Provider_ID 
               WHERE 1=1''' 
 
    if selected_city != 'All': 
        query += f" AND f.Location = '{selected_city}'" 
    if selected_food_type != 'All': 
        query += f" AND f.Food_Type = '{selected_food_type}'" 
    if selected_meal_type != 'All': 
        query += f" AND f.Meal_Type = '{selected_meal_type}'" 
 
    df = run_query(query) 
    if not df.empty:
        st.dataframe(df, use_container_width=True) 
        st.info(f'📊 Showing {len(df)} food listings.')
    else:
        st.warning('⚠️ No food listings match the selected filters.') 
 
# ───────────────────────────────────────────────────────────── 
# PAGE 4: CRUD OPERATIONS 
# ───────────────────────────────────────────────────────────── 
elif page == '📋 CRUD Operations': 
    st.header('📋 CRUD Operations') 
    st.markdown('Manage your food listings with Create, Read, Update, and Delete operations.')
 
    operation = st.radio('Select Operation', ['➕ Add Food Listing', '✏️ Update Listing', '🗑️ Delete Listing', '📖 View All Listings'], 
                        horizontal=True)
 
    if operation == '➕ Add Food Listing': 
        with st.container():
            st.subheader('➕ Add New Food Listing') 
            with st.form('add_form'): 
                col1, col2 = st.columns(2)
                with col1:
                    food_name = st.text_input('🍽️ Food Name') 
                    quantity = st.number_input('📦 Quantity', min_value=1) 
                    expiry_date = st.date_input('📅 Expiry Date') 
                with col2:
                    provider_id = st.number_input('🏢 Provider ID', min_value=1) 
                    provider_type = st.text_input('🏷️ Provider Type') 
                    location = st.text_input('🏙️ Location (City)') 
                food_type = st.selectbox('🥗 Food Type', ['Vegetarian', 'Non-Vegetarian', 'Vegan']) 
                meal_type = st.selectbox('🍲 Meal Type', ['Breakfast', 'Lunch', 'Dinner', 'Snacks']) 
                submitted = st.form_submit_button('✅ Add Listing') 
 
            if submitted and food_name: 
                q = '''INSERT INTO food_listings 
                       (Food_Name, Quantity, Expiry_Date, Provider_ID, Provider_Type, Location, Food_Type, Meal_Type) 
                       VALUES (%s, %s, %s, %s, %s, %s, %s, %s)''' 
                run_command(q, (food_name, quantity, expiry_date, provider_id, provider_type, location, food_type, meal_type)) 
                st.success('🎉 Food listing added successfully!') 
 
    elif operation == '✏️ Update Listing': 
        with st.container():
            st.subheader('✏️ Update Food Listing Quantity') 
            col1, col2 = st.columns(2)
            with col1:
                food_id = st.number_input('🆔 Enter Food ID to Update', min_value=1) 
            with col2:
                new_quantity = st.number_input('📦 New Quantity', min_value=0) 
            if st.button('🔄 Update', key='update_btn'): 
                run_command('UPDATE food_listings SET Quantity = %s WHERE Food_ID = %s', (new_quantity, food_id)) 
                st.success(f'✅ Food ID {food_id} updated to quantity {new_quantity}.') 
 
    elif operation == '🗑️ Delete Listing': 
        with st.container():
            st.subheader('🗑️ Delete a Food Listing') 
            food_id = st.number_input('🆔 Enter Food ID to Delete', min_value=1) 
            if st.button('🗑️ Delete', key='delete_btn'): 
                run_command('DELETE FROM claims WHERE Food_ID = %s', (food_id,)) 
                run_command('DELETE FROM food_listings WHERE Food_ID = %s', (food_id,)) 
                st.success(f'✅ Food ID {food_id} deleted successfully.') 
 
    elif operation == '📖 View All Listings': 
        with st.container():
            st.subheader('📖 All Food Listings') 
            df = run_query('SELECT * FROM food_listings ORDER BY Food_ID') 
            if not df.empty:
                st.dataframe(df, use_container_width=True) 
            else:
                st.info('📭 No food listings available.') 
 
# ───────────────────────────────────────────────────────────── 
# PAGE 5: CONTACT DIRECTORY 
# ───────────────────────────────────────────────────────────── 
elif page == '📞 Contact Directory': 
    st.header('📞 Contact Directory') 
    st.markdown('Find and connect with food providers and receivers in your area.')
 
    tab1, tab2 = st.tabs(['🏢 Food Providers', '🏠 Food Receivers']) 
 
    with tab1: 
        st.subheader('🏢 All Food Providers') 
        cities_p = run_query('SELECT DISTINCT City FROM providers ORDER BY City')['City'].tolist() 
        sel_city = st.selectbox('🏙️ Filter by City', ['All'] + cities_p, key='provider_city') 
        query_p = 'SELECT * FROM providers' 
        if sel_city != 'All': 
            query_p += f" WHERE City = '{sel_city}'" 
        df_p = run_query(query_p)
        if not df_p.empty:
            st.dataframe(df_p, use_container_width=True) 
            st.info(f'📊 Showing {len(df_p)} providers.')
        else:
            st.warning('⚠️ No providers found for the selected city.')
 
    with tab2: 
        st.subheader('🏠 All Food Receivers') 
        cities_r = run_query('SELECT DISTINCT City FROM receivers ORDER BY City')['City'].tolist() 
        sel_city_r = st.selectbox('🏙️ Filter by City', ['All'] + cities_r, key='receiver_city') 
        query_r = 'SELECT * FROM receivers' 
        if sel_city_r != 'All': 
            query_r += f" WHERE City = '{sel_city_r}'"         
        df_r = run_query(query_r)
        if not df_r.empty:
            st.dataframe(df_r, use_container_width=True) 
            st.info(f'📊 Showing {len(df_r)} receivers.')
        else:
            st.warning('⚠️ No receivers found for the selected city.')
