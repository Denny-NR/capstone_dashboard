import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
import streamlit as st
import altair as alt
from scipy.stats import mannwhitneyu
from statsmodels.stats.multicomp import pairwise_tukeyhsd

# Set page configuration
st.set_page_config(
    page_title="Anime Dashboard",
    layout="wide"
)
# Your Streamlit app code goes here
st.title("Anime Dashboard")
st.subheader('Apakah Anime yang Diadaptasi dari Sumber Eksternal Cenderung Mendapatkan Score lebih Tinggi dari pada Anime Original? Mari Lihat Datanya')
df = pd.read_csv("https://raw.githubusercontent.com/Denny-NR/capstone_dashboard/main/anime_series_dataset.csv")

st.dataframe(df)
# Menampilkan ringkasan statistik dengan .describe()
summary = df.describe()

# Menampilkan ringkasan statistik di Streamlit
st.write("Ringkasan Statistik DataFrame:")
st.dataframe(summary)

st.write('Sebaran Proporsi Anime untuk tiap Kategori')

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
    title="Proporsi Anime berdasarkan sumbernya",  # Add your desired title here
)
    # Display the chart in Streamlit
st.altair_chart(pie_chart, use_container_width=True)

#Menampilkan statistik pengecekan rata-rata secara umum
anime_original = df[df['source_category'] == 'Original']
anime_adaptasi = df[df['source_category'].isin(['Game', 'Manga', 'Novel','Other'])]

statistic, p_value = mannwhitneyu(anime_original['score'], anime_adaptasi['score'], alternative='two-sided')

# Tentukan tingkat signifikansi
alpha = 0.05

#Membuat kolom
col_ringkasan, col_barchart = st.columns(2)

with col_ringkasan:
    st.write('nilai p value dari hasil uji mannwhitneyu',p_value)
    summary_general_ori = anime_original['score'].describe()
    summary_general_eks = anime_adaptasi['score'].describe()
    st.write('Ringkasan Statistik Hasil Uji Mannwhitneyu:')
    col_original, col_adaptasi = st.columns(2)
    with col_original:
        st.write('Ringkasan Anime Original')
        st.dataframe(summary_general_ori)
    with col_adaptasi:
        st.write('Ringkasan Anime Adaptasi')
        st.dataframe(summary_general_eks)

with col_barchart:
# Hitung rata-rata untuk anime original dan external
    average_score_original = anime_original['score'].mean().round(2)
    average_score_external = anime_adaptasi['score'].mean().round(2)

    # Tampilkan ringkasan statistik
    st.write('Rata-rata Skor Anime Original:', average_score_original)
    st.write('Rata-rata Skor Anime Adaptasi:', average_score_external)

    # Membuat bar chart dengan Altair
    chart_data = pd.DataFrame({
        'Category': ['Original', 'Adaptasi'],
        'Average Score': [average_score_original, average_score_external]
    })

    chart = alt.Chart(chart_data).mark_bar().encode(
        alt.X('Category:N', title='Category', axis=alt.Axis(labelAngle=0)),
        alt.Y('Average Score:Q', title='Rata-rata Skor')
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
    # # Ambil informasi relevan dari hasil uji Tukey HSD
    # tukey_df = pd.DataFrame(data=tukey_results.meandiffs, columns=['Mean Difference'])
    # tukey_df['Lower CI'] = tukey_results.confint[:, 0]
    # tukey_df['Upper CI'] = tukey_results.confint[:, 1]
    # tukey_df['Reject Null Hypothesis'] = tukey_results.reject

    # # Tampilkan tabel hasil uji Tukey HSD di Streamlit
    # st.write('Hasil Uji Tukey HSD:')
    # st.dataframe(tukey_df)

    tukey_df = pd.DataFrame(data=tukey_results._results_table.data[1:], columns=tukey_results._results_table.data[0])

    # Menambahkan kolom 'group1' dan 'group2'
    tukey_df['Group 1'] = tukey_df['group1']
    tukey_df['Group 2'] = tukey_df['group2']
    tukey_df['Mean Difference'] = tukey_results.meandiffs
    tukey_df['Lower CI'] = tukey_results.confint[:, 0]
    tukey_df['Upper CI'] = tukey_results.confint[:, 1]
    tukey_df['Reject Null Hypothesis'] = tukey_results.reject

    # Menampilkan tabel hasil uji Tukey HSD di Streamlit
    st.write('Hasil Uji Tukey HSD:')
    st.dataframe(tukey_df.iloc[:, [7, 0, 9, 4, 5, 8,6]])
with col_box:
    df_altair = pd.concat([anime_original, anime_adaptasi])
    # Altair code for boxplot
    box = alt.Chart(df_altair).mark_boxplot().encode(
        x=alt.X('source_category:N', title='Kategori'),
        y=alt.Y('score:Q', title='Skor'),
        color=alt.Color('source_category:N', scale=alt.Scale(range=['blue', 'orange', 'green', 'red', 'yellow'])),
    ).properties(
        width=150,
        height=300,
        title='Distribusi Skor untuk Setiap Kategori'
    ) 
    st.altair_chart(box, use_container_width=True)

df['Year'] = pd.to_datetime(df['rilis;']).dt.year
# Filter berdasarkan sumber adaptasi
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
    title='Rata-rata Skor Berdasarkan Tahun Rilis dan Kategori Sumber Adaptasi'
)

# Tampilkan chart dalam Streamlit
st.altair_chart(line_chart, use_container_width=True)



#correlation matrix
correlation_matrix = df[['score','episodes', 'members', 'favorites']].corr()
corr_df = pd.DataFrame(correlation_matrix)

    # chart_heatmap = alt.Chart(corr_df).mark_rect(
    #     color='lightblue'
    # ).encode(
    #     x=alt.X('column:Q', title=None),
    #     y=alt.Y('row:Q', title=None),
    #     color=alt.Color('value:Q', scale=alt.Scale(scheme='reds'), title='Correlation')
    # ).properties(
    #     title='Heatmap: Correlation between Episodes, Score, Members, and Favorites',
    #     width=650,
    #     height=400
    # )

    # Display the chart
    # st.altair_chart(chart_heatmap, use_container_width=True)
st.write('Heatmap: Korelasi antara Episodes, Score, Members, and Favorites')
plt.rcParams.update({'font.size': 3})  # Ukuran teks
fig, ax = plt.subplots(figsize=(2, 1))  # Ukuran figure
plt.style.use('dark_background')  # Latar belakang hitam
    # Tampilkan heatmap dengan Matplotlib
sns.heatmap(correlation_matrix, annot=True, cmap='coolwarm', fmt='.2f', linewidths=.5, ax=ax)
ax.set_yticklabels(ax.get_yticklabels(), rotation=0)
    # Tampilkan plot menggunakan Streamlit
st.pyplot(fig)
