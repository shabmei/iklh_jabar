import streamlit as st
import pandas as pd
import altair as alt
# from numerize import numerize

st.set_page_config(layout='centered')

from PIL import Image
import requests
from io import BytesIO

# st.title("Korelasi Indeks Kualitas Lingkungan Hidup (IKLH) dan Kepadatan Penduduk di Jawa Barat")
image = Image.open(requests.get('https://raw.githubusercontent.com/shabmei/iklh_jabar/main/dataset/iklh.jpg', stream=True).raw)
# left_co, cent_co,last_co = st.columns(3)
# with cent_co:
st.image(image, width=700)
st.caption("Oleh: Shabrina Ainimeiko")

with st.sidebar:
    st.title("Korelasi Indeks Kualitas Lingkungan Hidup (IKLH) dan Kepadatan Penduduk di Jawa Barat")
    analysis_option = st.radio("Pilih Halaman", ["Pendahuluan", "Tren per Tahun", "Perbandingan Tren Indikator", "Uji Korelasi", "Kesimpulan"])
    
if analysis_option == "Pendahuluan":
    st.header("Pendahuluan")
    st.write("Indeks Kualitas Lingkungan Hidup (IKLH) memiliki peran penting dalam mengukur kesehatan lingkungan suatu wilayah, sementara kepadatan penduduk dapat memengaruhi interaksi manusia dengan lingkungan.")
    st.write("IKLH dapat mencakup sejumlah indikator, seperti kualitas udara, kualitas air, kualitas tutupan lahan, yang merupakan faktor penting dalam menjaga kondisi lingkungan yang baik.")
    st.write("Analisis hubungan antara IKLH dan kepadatan penduduk dapat memberikan wawasan bagaimana perkembangan populasi mempengaruhi kualitas lingkungan, khususnya di Jawa Barat.")
    st.header("Sumber Data")
    st.write("Seluruh data bersumber dari [Open Data Jabar](https://opendata.jabarprov.go.id/id) dan dapat dipertanggungjawabkan.")

# Data indeks kualitas lingkungan hidup
df = pd.read_csv('https://raw.githubusercontent.com/shabmei/iklh_jabar/main/dataset/ilh_berdasarkan_indikator_data.csv')

filtered_df = df[df['tahun'].isin([2015, 2016, 2017, 2018, 2019, 2020, 2021, 2022])]

ilh = filtered_df.pivot(index="tahun", columns="indikator", values="indeks_lingkungan_hidup")

# Data kepadatan penduduk
data = pd.read_csv('https://raw.githubusercontent.com/shabmei/iklh_jabar/main/dataset/kepadatan_penduduk.csv')

fil_data = data[data['tahun'].isin([2015, 2016, 2017, 2018, 2019, 2020, 2021, 2022])]

total= fil_data.groupby('tahun')['kepadatan_penduduk'].sum().reset_index()

# Menyatukan kedua DataFrame berdasarkan kolom tahun
merged_df = pd.merge(ilh, total, on='tahun')

CURR_YEAR = max(merged_df['tahun'])
PREV_YEAR = CURR_YEAR - 1

if analysis_option == "Tren per Tahun":
    st.header("Tren per Tahun")
    st.write("Memahami tren dengan visualisasi data dari tahun ke tahun:")

    # helper function
    def format_big_number(num):
        if num >= 1e6:
            return f"{num / 1e6:.2f} Mio"
        elif num >= 1e3:
            return f"{num / 1e3:.2f} K"
        else:
            return f"{num:.2f}"

    kepadatan_penduduk, iklh = st.columns(2)

    with kepadatan_penduduk:
        curr_kepadatan = merged_df.loc[merged_df['tahun'] == CURR_YEAR, 'kepadatan_penduduk'].values[0]
        prev_kepadatan = merged_df.loc[merged_df['tahun'] == PREV_YEAR, 'kepadatan_penduduk'].values[0]
    
        kepadatan_diff_pct = 100.0 * (curr_kepadatan - prev_kepadatan) / prev_kepadatan

        st.metric("Kepadatan Penduduk", value=format_big_number(curr_kepadatan), delta=f'{kepadatan_diff_pct:.2f}%')

    with iklh:
        curr_iklh = merged_df.loc[merged_df['tahun'] == CURR_YEAR, 'Indeks Kualitas Lingkungan Hidup'].values[0]
        prev_iklh = merged_df.loc[merged_df['tahun'] == PREV_YEAR, 'Indeks Kualitas Lingkungan Hidup'].values[0]
    
        iklh_diff_pct = 100.0 * (curr_iklh - prev_iklh) / prev_iklh

        st.metric("Indeks Kualitas Lingkungan Hidup", value=curr_iklh, delta=f'{iklh_diff_pct:.2f}%')

    iklh = filtered_df[filtered_df['indikator'].isin(["Indeks Kualitas Lingkungan Hidup"])]

    jenis_data = st.selectbox ("Pilih Tren", ['Indeks Kualitas Lingkungan Hidup', 'Kepadatan Penduduk'])

    # Memilih DataFrame berdasarkan pilihan pengguna
    df_selected = iklh if jenis_data == 'Indeks Kualitas Lingkungan Hidup' else total

    # Menampilkan judul sesuai dengan jenis data yang dipilih
    st.write(f"**{jenis_data}**")

    # Membuat line chart 
    line_chart = alt.Chart(df_selected).mark_line().encode(
        alt.X('tahun:O', title='Tahun'),
        alt.Y('indeks_lingkungan_hidup:Q' if jenis_data == 'Indeks Kualitas Lingkungan Hidup' else 'kepadatan_penduduk:Q')
    ).configure_axis(
        labelAngle=0  
    )

    st.altair_chart(line_chart, use_container_width=True)

    st.write("#### **Insight:**")
    st.markdown("""
        1. Terlihat bahwa IKLH memiliki nilai fluktuatif pada tahun 2015-2018, tetapi terus meningkat setelah tahun 2018.
        2. Jumlah kepadatan penduduk terus mengalami peningkatan dari tahun 2015-2021, tetapi terjadi penurunan pada tahun 2022.
        3. Pada tahun 2022, terjadi penurunan kepadatan penduduk dari tahun sebelumnya, yang seiringan dengan peningkatan IKLH.
    """)

if analysis_option == "Perbandingan Tren Indikator":
    st.header("Perbandingan Tren Indikator")
    st.write("Membandingkan setiap indikator pada Indeks Lingkungan Hidup untuk mengetahui tren dan perubahan dari waktu ke waktu.")

    ika, iku, ikl = st.columns(3)

    with ika:
        curr_ika = merged_df.loc[merged_df['tahun'] == CURR_YEAR, 'Indeks Kualitas Air'].values[0]
        prev_ika = merged_df.loc[merged_df['tahun'] == PREV_YEAR, 'Indeks Kualitas Air'].values[0]
    
        ika_diff_pct = 100.0 * (curr_ika - prev_ika) / prev_ika

        st.metric("Indeks Kualitas Air", value=curr_ika, delta=f'{ika_diff_pct:.2f}%')

    with iku:
        curr_iku = merged_df.loc[merged_df['tahun'] == CURR_YEAR, 'Indeks Kualitas Udara'].values[0]
        prev_iku = merged_df.loc[merged_df['tahun'] == PREV_YEAR, 'Indeks Kualitas Udara'].values[0]
    
        iku_diff_pct = 100.0 * (curr_iku - prev_iku) / prev_iku

        st.metric("Indeks Kualitas Udara", value=curr_iku, delta=f'{iku_diff_pct:.2f}%')

    with ikl:
        curr_ikl = merged_df.loc[merged_df['tahun'] == CURR_YEAR, 'Indeks Kualitas Tutupan Lahan'].values[0]
        prev_ikl = merged_df.loc[merged_df['tahun'] == PREV_YEAR, 'Indeks Kualitas Tutupan Lahan'].values[0]
    
        ikl_diff_pct = 100.0 * (curr_ikl - prev_ikl) / prev_ikl

        st.metric("Indeks Kualitas Lahan", value=curr_ikl, delta=f'{ikl_diff_pct:.2f}%')

    df_ind = filtered_df[filtered_df['indikator'].isin(["Indeks Kualitas Air", "Indeks Kualitas Udara", "Indeks Kualitas Tutupan Lahan"])]

    # Membuat line plot tren setiap indikator 
    line_chart = alt.Chart(df_ind).mark_line().encode(
        x='tahun:O',
        y='indeks_lingkungan_hidup:Q',
        color=alt.Color('indikator:N', legend=alt.Legend(orient='bottom-right', title=None))
    ).properties(
        title='Perbandingan Indikator dari Tahun ke Tahun',
        width=200,
        height=450
    ).configure_axis(
        labelAngle=0  
    )

    st.altair_chart(line_chart, use_container_width=True)

    st.write("#### **Insight:**")
    st.write("Dari perbandingan IKA, IKU, dan IKL, terlihat bahwa ketiganya mengalami fluktuasi nilai dari tahun ke tahun, yang menunjukkan variasi dalam kondisi lingkungan seiring waktu. Meskipun belum dilakukan analisis lebih lanjut, observasi ini dapat menjadi dasar untuk pertimbangan lanjutan dalam pengelolaan lingkungan.")

if analysis_option == "Uji Korelasi":
    st.header("Uji Korelasi")
    st.write("Hubungan statistik antara Indeks Kualitas Lingkungan Hidup (IKLH) dengan kepadatan penduduk dapat dicari dengan menggunakan Heatmap untuk uji korelasi")

    merged_df = merged_df.drop(columns=['tahun'])

    # Membuat heatmap 
    heatmap_chart = alt.Chart(merged_df.corr().reset_index().melt('index')).mark_rect().encode(
        x=alt.X('index:O', axis=alt.Axis(title=None, labelFontSize=15)),  
        y=alt.Y('variable:O', axis=alt.Axis(title=None, labelFontSize=15)),
        color=alt.Color('value:Q', scale=alt.Scale(scheme='blues'), title=None),
        tooltip=['index:N', 'variable:N', 'value:Q']
    ).properties(
        title='Heatmap Korelasi',
        width=alt.Step(100),  # Lebar setiap kolom atau baris dalam heatmap
        height=alt.Step(85)
    )

    # Membuat mark text
    text_chart = alt.Chart(merged_df.corr().reset_index().melt('index')).mark_text(
        size=15,
        baseline='middle'
    ).encode(
        x='index:O',
        y='variable:O',
        text=alt.Text('value:Q', format=".2f"),
        color=alt.condition(
            alt.datum.value >= 0,
            alt.value('white'),
            alt.value('black')
        )
    )

    # Menggabungkan kedua chart
    combined_chart = alt.layer(heatmap_chart, text_chart)

    # Menambahkan CSS untuk menyesuaikan panjang teks pada sumbu x dan y
    combined_chart = combined_chart.configure_axis(
        labelLimit=220 
    )

    # Menambahkan CSS untuk menyesuaikan panjang color scale
    combined_chart = combined_chart.configure_legend(
        gradientLength=410,  
        gradientThickness=15  
    )

    st.altair_chart(combined_chart, use_container_width=True)

    st.write("#### **Insight:**")
    st.markdown("""
        1. Korelasi antara Indeks Kualitas Tutupan Lahan (IKTL) dengan Kepadatan Penduduk menunjukkan korelasi negatif.
        2. Korelasi positif antara Indeks Kualitas Air (IKA) dan Indeks Kualitas Udara (IKU) dengan kepadatan penduduk dapat memberikan perubahan positif dalam kualitas air dan udara, namun perlu diwaspadai potensi risiko pencemaran.
    """)

if analysis_option == "Kesimpulan":
    st.header("Kesimpulan")
    st.markdown("""
        1. Adanya tren peningkatan signifikan dalam Indeks Kualitas Lingkungan Hidup (IKLH) sejak 2018 menunjukkan kemungkinan perbaikan kondisi lingkungan.
        2. Tren peningkatan signifikan dalam Indeks Kualitas Lingkungan Hidup (IKLH) setelah tahun 2018 menandakan kemungkinan perbaikan kondisi lingkungan, sementara penurunan kepadatan penduduk pada tahun 2022 menunjukkan adanya dinamika yang berpotensi mempengaruhi kondisi sosial-lingkungan.
        3. Penting untuk diingat bahwa korelasi tidak selalu menunjukkan hubungan sebab-akibat yang langsung. Ini menegaskan bahwa meskipun terdapat korelasi positif antara Indeks Kualitas Air (IKA) dan Indeks Kualitas Udara (IKU) dengan kepadatan penduduk, serta korelasi negatif antara Indeks Kualitas Lingkungan Hidup (IKLH) dan kepadatan penduduk, tidak dapat disimpulkan secara langsung bahwa satu variabel menyebabkan perubahan pada variabel lainnya.
    """)
