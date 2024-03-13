import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
import streamlit as st
import altair as alt
from scipy.stats import mannwhitneyu
from statsmodels.stats.multicomp import pairwise_tukeyhsd
from streamlit_option_menu import option_menu

# Set page configuration
st.set_page_config(
    page_title="Anime Dashboard",
    layout="wide"
)

st.title('Apakah Anime yang Diadaptasi dari Sumber Eksternal Cenderung Mendapatkan Score lebih Tinggi dari pada Anime Original? Mari Lihat Datanya')

df = pd.read_csv("https://raw.githubusercontent.com/Denny-NR/capstone_dashboard/main/anime_series_dataset.csv")

#Navbar

selected = option_menu(
    menu_title=None, #required
    options=['Dashboard','Ringkasan Statistik', 'Dataset'],
    icons=['file-earmark-bar-graph-fill','graph-up-arrow','database-fill'],
    menu_icon='cast',
    default_index=0,
    orientation='horizontal',
    styles={
        "container": {"padding": "0!important", "background-color": "#C9D7DD"},
        "icon": {"color": "orange", "font-size": "15px"}, 
        "nav-link": {"font-size": "15px", "text-align": "center", "margin":"0px", "--hover-color": "#9195F6"},
        "nav-link-selected": {"background-color": "blue"},
    }
)
    
if selected == 'Dashboard':
    st.header("Dashboard")
    title_pie, title_chart = st.columns(2)
    with title_pie:
        st.subheader("Proporsi Anime berdasarkan sumber Adaptasinya")

    with title_chart:
        st.subheader("Perbandingan Statistik Antara Anime Original dan Adaptasi Secara Umum")

    col_pie, col_barchart = st.columns(2)
    with col_pie:  
        category_counts = df['source_category'].value_counts().reset_index()
        category_counts.columns = ['source_category', 'count']
        category_counts['percentage'] = (category_counts['count'] / category_counts['count'].sum())

        #Membuat piechart
        pie_chart = alt.Chart(category_counts).mark_arc().encode(
        alt.Theta('count:Q', stack=True),
        alt.Color("source_category:N"),
        text=alt.Text('percentage:Q', format='.1%'),  # Display percentage as whole numbers
        tooltip=[
            alt.Tooltip('source_category:N', title='Kategori'),
            alt.Tooltip('count:Q', title='Jumlah'),
            alt.Tooltip('percentage:Q', title='Persentase', format='.1%')
        ]
        ).properties(
            width=300,
            height=300,
        )
            # Display the chart in Streamlit
        st.altair_chart(pie_chart, use_container_width=True)

    #Menampilkan statistik pengecekan rata-rata secara umum
    anime_original = df[df['source_category'] == 'Original']
    anime_adaptasi = df[df['source_category'].isin(['Game', 'Manga', 'Novel','Other'])]

    statistic, p_value = mannwhitneyu(anime_original['score'], anime_adaptasi['score'], alternative='two-sided')

    # Tentukan tingkat signifikansi
    alpha = 0.05

    #colom tambahan
    col_chart, col_checkbox = col_barchart.columns([2, 1])
        # Hitung rata-rata untuk anime original dan external
    average_score_original = anime_original['score'].mean().round(2)
    average_score_external = anime_adaptasi['score'].mean().round(2)
        #Hitung standart deviasi:
    std_score_original = anime_original['score'].std()
    std_score_external = anime_adaptasi['score'].std()
        #hitung jumlah:
    count_score_original = anime_original['score'].count()
    count_score_external = anime_adaptasi['score'].count()
        #min
    min_score_original = anime_original['score'].min()
    min_score_external = anime_adaptasi['score'].min()
        #max
    max_score_original = anime_original['score'].max()
    max_score_external = anime_adaptasi['score'].max()

        # Membuat bar chart dengan Altair
    chart_data = pd.DataFrame({
        'Category': ['Original', 'Adaptasi'],
        'Average_Score': [average_score_original, average_score_external],
        'std_score' : [std_score_original, std_score_external],
        'count_score':[count_score_original, count_score_external],
        'min_score':[min_score_original, min_score_external],
        'max_score':[max_score_original, max_score_external]
    })

    with col_checkbox :
        selected_option = st.radio("Pilih opsi:", ["Rata-rata", "Minimum", "Maksimum", "Jumlah Data", "Standar Deviasi"], index=0)
        if selected_option == "Rata-rata":
            selected_options = [alt.Y('Average_Score:Q', title='Rata-rata Skor')]
        elif selected_option == "Minimum":
            selected_options = [alt.Y('min_score:Q', title='Skor Minimum')]
        elif selected_option == "Maksimum":
            selected_options = [alt.Y('max_score:Q', title='Skor Maksimal')]
        elif selected_option == "Jumlah Data":
            selected_options = [alt.Y('count_score:Q', title='Jumlah Data')]
        elif selected_option == "Standar Deviasi":
            selected_options = [alt.Y('std_score:Q', title='Standar Deviasi')] 
        
        st.write('nilai p value dari hasil uji mannwhitneyu',p_value)

    with col_chart:
        chart = alt.Chart(chart_data).mark_bar().encode(
            alt.X('Category:N', title='Category', axis=alt.Axis(labelAngle=0)),
            *selected_options
            ).properties(
            width=400
        )

        # Tampilkan chart dalam Streamlit
        st.altair_chart(chart, use_container_width=True)

    col_tukey, col_box = st.columns(2)
    #Secara Spesifik
    with col_tukey:
        # Melakukan uji Tukey HSD
        tukey_results = pairwise_tukeyhsd(df['log_score'], df['source_category'], alpha=0.05)
        tukey_df = pd.DataFrame(data=tukey_results._results_table.data[1:], columns=tukey_results._results_table.data[0])

        # Menambahkan kolom 'group1' dan 'group2'
        tukey_df['Group 1'] = tukey_df['group1']
        tukey_df['Group 2'] = tukey_df['group2']
        tukey_df['Mean Difference'] = tukey_results.meandiffs
        tukey_df['Lower CI'] = tukey_results.confint[:, 0]
        tukey_df['Upper CI'] = tukey_results.confint[:, 1]
        tukey_df['Reject Null Hypothesis'] = tukey_results.reject

        # Menampilkan tabel hasil uji Tukey HSD di Streamlit
        st.subheader('Hasil Uji Tukey HSD:')
        st.dataframe(tukey_df.iloc[:, [7, 8, 9, 4, 5,6]])
    with col_box:
        st.subheader('Distribusi Skor untuk Setiap Kategori')
        df_altair = pd.concat([anime_original, anime_adaptasi])
        # Altair code for boxplot
        box = alt.Chart(df_altair).mark_boxplot().encode(
            x=alt.X('source_category:N', title='Kategori'),
            y=alt.Y('score:Q', title='Skor'),
            color=alt.Color('source_category:N', scale=alt.Scale(range=['blue', 'orange', 'green', 'red', 'yellow'])),
        ).properties(
            width=150,
            height=300,
        ) 
        st.altair_chart(box, use_container_width=True)

    df['Year'] = pd.to_datetime(df['rilis;']).dt.year
    # Filter berdasarkan sumber adaptasi
    st.subheader('Rata-rata Skor Berdasarkan Tahun Rilis dan Kategori Sumber Adaptasi')
    source_filter_options = ['Manga', 'Novel', 'Game', 'Original', 'Other']
    source_filter = st.multiselect('Pilih Sumber Adaptasi', source_filter_options, default=source_filter_options)

    # Filter DataFrame
    filtered_df = df[df['source_category'].isin(source_filter)]

    # Hitung rata-rata skor setiap tahun berdasarkan kategori
    average_score_by_category = filtered_df.groupby(['Year', 'source_category']).agg({'score': 'mean'}).reset_index()

    # Altair Line Chart
    line_chart = alt.Chart(average_score_by_category).mark_line().encode(
        x='Year:O',  # Sumbu x sebagai tahun rilis (ordinal)
        y=alt.Y('mean(score):Q', title='Rata-rata Skor'),  # Sumbu y sebagai rata-rata skor
        color='source_category:N',  # Warna garis berdasarkan kategori sumber
        tooltip=['Year:O', alt.Tooltip('mean(score):Q', title='Rata-rata Skor')]
    ).properties(
        width=600,
        height=400,
    )

    # Tampilkan chart dalam Streamlit
    st.altair_chart(line_chart, use_container_width=True)

    heatmap_col, insight_col = st.columns(2)

    with heatmap_col:
        #correlation matrix
        correlation_matrix = df[['score','episodes', 'members', 'favorites']].corr()
        corr_df = pd.DataFrame(correlation_matrix)
        st.subheader('Korelasi antara Episodes, Favorites, Members dan Score')
        plt.rcParams.update({'font.size': 3})  # Ukuran teks
        fig, ax = plt.subplots(figsize=(2, 1))  # Ukuran figure
        plt.style.use('dark_background')  # Latar belakang hitam
        # Tampilkan heatmap dengan seaborn
        sns.heatmap(correlation_matrix, annot=True, cmap='coolwarm', fmt='.2f', linewidths=.5, ax=ax)
        ax.set_yticklabels(ax.get_yticklabels(), rotation=0)
            # Tampilkan plot menggunakan Streamlit
        st.pyplot(fig)
    
    with insight_col:
        st.subheader('Insight:')
        st.subheader(' ')
        st.write("""
            1. Anime yang diadaptasi dari manga memiliki populasi yang lebih besar dari pada anime original dan adaptasi dari sumber lainnya.
            2. Secara umum, anime adaptasi memiliki nilai statistik yang lebih tinggi, dari pada anime original kecuali pada nilai minimum.
            3. Anime original memiliki rerata skor yang cenderung lebih tinggi daripada anime yang diadaptasi dari game dan others, namun lebih rendah daripada anime yang diadaptasi dari novel dan manga.
            4. Jumlah episode, favorites, dan members memiliki pengaruh yang rendah terhadap skor anime, tetapi ada hubungan yang kuat antara jumlah members dan favorites.
            """)
    st.subheader("Kesimpulan")
    st.write("adaptasi dari manga menjadi salah satu faktor yang signifikan dalam menentukan populasi dan skor anime, sementara anime original memiliki potensi untuk mencapai skor yang lebih tinggi dengan konten yang unik. Selain itu, meskipun faktor seperti jumlah episode, favorites, dan members memiliki pengaruh yang lebih rendah terhadap skor anime, ada hubungan yang kuat antara jumlah members dan favorites, yang mungkin berkontribusi pada peningkatan skor.")

if selected == 'Ringkasan Statistik': 
    summary = df.describe()
    st.header("Ringkasan Statistik Data:")
    st.dataframe(summary)

if selected == 'Dataset':
    st.header('Dataset:')
    st.dataframe(df)
    url = "https://myanimelist.net/"
    st.markdown("Sumber Data: [MyAnimeList](%s)" % url)
