import streamlit as st 
import pandas as pd
import psycopg2

st.set_page_config(layout="wide")

st.header('Woordenboek [Optimized]')

if 'cursor' not in st.session_state:
    
    USER = st.secrets['db_user']
    PASSWORD = st.secrets['db_password']
    HOST = 'aws-0-eu-central-1.pooler.supabase.com'
    PORT = 5432
    DBNAME = 'postgres'
        
    connection = psycopg2.connect(
        user=USER,
        password=PASSWORD,
        host=HOST,
        port=PORT,
        dbname=DBNAME,
        connect_timeout=3,
    )
    
    cursor = connection.cursor()
    
    st.session_state['cursor'] = cursor
    
    
page = 1
page_size = 150
offset = page_size * (page - 1)







with st.sidebar:
    def get_slider(title, interval_naam):
        return st.slider(
            title,
            value=[0,1000], 
            min_value=0, max_value=1000)
    
    space_left, col1, space_mid, col2, space_right = st.columns([1, 6, 1, 6, 1])
        
    with col1:
        s_week =     get_slider('Week','week')
        s_maand =    get_slider('Maand', 'maand')
        s_kwartaal = get_slider('Kwartaal','kwartaal')
        s_jaar =     get_slider('Jaar','jaar')
    with col2:
        s_2weken =   get_slider('2 weken', '2weken')
        s_2maanden = get_slider('2 maanden', '2maanden')
        s_halfjaar = get_slider('Half jaar', 'halfjaar')
        s_2jaar =    get_slider('2 jaar', '2jaar')


    st.markdown('---')
    
    of_links, col, of_rechts = st.columns([1,13,1])
    
    with col:
    
        minimum, maximum = st.select_slider(
            'Aantal offers',
            options=[0,1,2,3,5,8,13,21,34,55,89,144,233,377,610,987,1597,2584,4181,6765,10946],
            value=(0, 10946)
            )
    
    st.markdown('---')

    of_links_2, col_2, of_rechts_2 = st.columns([1,13,1])
                
    with col_2:

        options_list = [x/10 for x in range(10)] + [x for x in range(1,10+1)] + [x*5 for x in range(3,20+1)] + [x*50 for x in range(2,16+1)]
        options_list = [str(x) for x in options_list]
        
        def ratio_slider(interval):
            
            minner = 0
            maxxer = 800
            
            return st.select_slider(
                f'Ratio {interval}', 
                options=options_list, 
                value=(
                    '0.0' if minner==0 else str(minner),
                    '0.0' if maxxer==0 else str(maxxer)
                )
            )

        s_r_maand_min, s_r_maand_max = ratio_slider('maand')
        s_r_kwartaal_min, s_r_kwartaal_max = ratio_slider('kwartaal')
        s_r_jaar_min,  s_r_jaar_max = ratio_slider('jaar')

        
        st.markdown('---')
        
    of_links_3, col_3, of_rechts_3 = st.columns([1,13,1])
        
    with col_3:
            
        def vol_slider(interval):
            minner = 0
            maxxer = 1048576
            
            return st.select_slider(
                f'Prijs x Volume ({interval})',
                options=[i**4 for i in range(33)],
                value=(minner, maxxer)
            )
        
        
        s_vol_maand_min, s_vol_maand_max = vol_slider('maand')
        s_vol_kwartaal_min, s_vol_kwartaal_max = vol_slider('kwartaal')
        s_vol_jaar_min,  s_vol_jaar_max = vol_slider('jaar')
    
        
        
        

        st.markdown('---')
        
    of_links_4, col_4, of_rechts_4 = st.columns([1,13,1])  
    
    with col_4:
        blacklisted = st.multiselect(
            "Blacklisted categories",
            st.session_state['possible_categories'],
        )  
        
        







placeholders = ','.join([f"'{x}'" for x in blacklisted]) # '%s,%s,%s'

category_filter = f'AND "category" NOT IN ({placeholders})'


st.session_state['cursor'].execute(
    f"""
    SELECT * 
    FROM db2 
    WHERE "week" BETWEEN {s_week[0]} AND {s_week[1]}
    AND "maand" BETWEEN {s_maand[0]} AND {s_maand[1]}
    AND "kwartaal" BETWEEN {s_kwartaal[0]} AND {s_kwartaal[1]}
    AND "jaar" BETWEEN {s_jaar[0]} AND {s_jaar[1]}
    
    
    AND "2_weken" BETWEEN {s_2weken[0]} AND {s_2weken[1]}
    AND "2_maanden" BETWEEN {s_2maanden[0]} AND {s_2maanden[1]}
    AND "half_jaar" BETWEEN {s_halfjaar[0]} AND {s_halfjaar[1]}
    AND "2_jaar" BETWEEN {s_2jaar[0]} AND {s_2jaar[1]}
    
    AND "offer_amount" BETWEEN {minimum} AND {maximum}
    
    AND "Ratio maand" BETWEEN {s_r_maand_min} AND {s_r_maand_max}
    AND "Ratio kwartaal" BETWEEN {s_r_kwartaal_min} AND {s_r_kwartaal_max}
    AND "Ratio jaar" BETWEEN {s_r_jaar_min} AND {s_r_jaar_max}
    
    AND "Prijs x Vol (maand)" BETWEEN {s_vol_maand_min} AND {s_vol_maand_max}
    AND "Prijs x Vol (kwartaal)" BETWEEN {s_vol_kwartaal_min} AND {s_vol_kwartaal_max}
    AND "Prijs x Vol (jaar)" BETWEEN {s_vol_jaar_min} AND {s_vol_jaar_max}
    
    {category_filter}
    
    ORDER BY maand
    LIMIT %s OFFSET %s 
    
    """,
    (page_size, offset)
)

columns = [desc[0] for desc in st.session_state['cursor'].description]

st.dataframe(pd.DataFrame(st.session_state['cursor'].fetchall(), columns=columns), height=800)



        
        
    