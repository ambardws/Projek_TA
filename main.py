#!/usr/bin/env python
from flask import *
import jinja2.exceptions
import pandas as pd
import csv
from flask import Flask, render_template, request, redirect, url_for
import os
from modelKNN import modelKNN
from textprocessing import textprocessing
import matplotlib.pyplot as plt
from wordcloud import WordCloud

app = Flask(__name__)
app.secret_key  = '1f3a80e2ab97fec7fa12958d156261bf'


# Upload folder
UPLOAD_FOLDER = 'static/csv'
app.config['UPLOAD_FOLDER'] =  UPLOAD_FOLDER


@app.route('/')
def index():
    cek_file = os.path.isfile('static/csv/hasil_klasifikasi.csv')
    
    positif = 0
    negatif = 0
    netral = 0

    if(cek_file == True): 
        with open('static/csv/hasil_klasifikasi.csv', 'r') as f:
            data = [dict(item) for item in csv.DictReader(f)]
            items_per_page = int(len(data))
            index_from = 0;
            index_to = index_from + items_per_page
            jumlah_data = range(int(len(data)))

            positif = 0
            negatif = 0
            netral = 0

            for sentimen in data:
                if(sentimen['Hasil_Prediksi'] == 'Positif'):
                    positif += 1
                if(sentimen['Hasil_Prediksi'] == 'Negatif'):
                    negatif += 1
                if(sentimen['Hasil_Prediksi'] == 'Netral'):
                    netral += 1

            kesimpulan = ''
            
            if positif >= negatif and positif >= netral:
                kesimpulan = 'Positif'
            elif negatif >= positif and negatif >= netral:
                kesimpulan = 'Negatif'
            elif netral >= positif and netral >= negatif:
                kesimpulan = 'Netral/Berimbang'

            
            return render_template('index.html',data=data[index_from:index_to], jumlah_data=jumlah_data, positif=positif, negatif=negatif, netral=netral, kesimpulan=kesimpulan)
    return render_template('index.html', positif=positif, negatif=negatif, netral=netral)

# Get the uploaded files
@app.route("/hasil_crawling", methods=['POST'])
def uploadFiles():
      # get the uploaded file
      uploaded_file = request.files['file']
      if uploaded_file.filename != '':
           uploaded_file.filename = 'Hasil_Crawling_Berita.csv'
           file_path = os.path.join(app.config['UPLOAD_FOLDER'], uploaded_file.filename)
          # set and save the file path
           uploaded_file.save(file_path)

           with open('static/csv/Hasil_Crawling_Berita.csv', 'r') as f:
        # init dataset
            data = [dict(item) for item in csv.DictReader(f)]
            
            # display items per page
            items_per_page = int(len(data))
            
            # starting index
            index_from = 0;

            # ending index
            index_to = index_from + items_per_page

            flash('Upload CSV Berhasil','success')

            # render content
            return render_template('hasil_crawling.html', data=data[index_from:index_to])

      flash('Pilih CSV Terlebih Dahulu','warning')
      return redirect(request.url)
          

@app.route('/<pagename>')
def admin(pagename):
    if(pagename == 'hasil_labeling' and 'klasifikasi_berita'):
        cek_file = os.path.isfile('static/csv/Hasil_Crawling_Berita.csv')
        with open('static/csv/Hasil_Crawling_Berita.csv', 'r') as f:
            data = [dict(item) for item in csv.DictReader(f)]
            items_per_page = int(len(data))
            index_from = 0;
            index_to = index_from + items_per_page
            total_pages = range(int(len(data)))
        for sentimen in data:
                if(sentimen['Label'] == '1'):
                    sentimen['Label'] = 'Positif'
                if(sentimen['Label'] == '-1'):
                    sentimen['Label'] = 'Negatif'
                if(sentimen['Label'] == '0'):
                    sentimen['Label'] = 'Netral'

        return render_template(pagename+'.html', data=data[index_from:index_to], total_pages=total_pages)

    if(pagename == 'klasifikasi_berita'):
         cek_file = os.path.isfile('static/csv/Hasil_Crawling_Berita.csv')
         if(cek_file == True):
            with open('static/csv/Hasil_Crawling_Berita.csv', 'r') as f:
                data = [dict(item) for item in csv.DictReader(f)]
                items_per_page = int(len(data))
                index_from = 0;
                index_to = index_from + items_per_page
                total_pages = range(int(len(data)))
            for sentimen in data:
                    if(sentimen['Label'] == '1'):
                        sentimen['Label'] = 'Positif'
                    if(sentimen['Label'] == '-1'):
                        sentimen['Label'] = 'Negatif'
                    if(sentimen['Label'] == '0'):
                        sentimen['Label'] = 'Netral'

            return render_template(pagename+'.html', data=data[index_from:index_to], total_pages=total_pages)

    if(pagename == 'case_folding' or 'tokenizing' or 'filtering' or 'stemming'):
        cek_file = os.path.isfile('static/csv/text_processing.csv')
        if(cek_file == True):
            with open('static/csv/text_processing.csv', 'r') as f:
                data_hasil = [dict(item) for item in csv.DictReader(f)]
                items_per_page = int(len(data_hasil))
                index_from = 0;
                index_to = index_from + items_per_page

                return render_template(pagename+'.html', data=data_hasil[index_from:index_to])

    return render_template(pagename+'.html')


@app.route("/hasil_labeling", methods=['POST'])
def labeling():
    df = pd.read_csv("static/csv/Hasil_Crawling_Berita.csv")
    if request.method == 'POST':
        if request.form.get("Simpan"):
            idx = request.form["no"]
            title = request.form["title"]
            sumber = request.form["sumber"]
            label = request.form["label"]   
            if not idx: 
                new_row = pd.DataFrame({'Title':[title], 'Sumber':[sumber], 'Label':[label]},index =[0])
                df = pd.concat([new_row, df]).reset_index(drop = True)
                df = df.loc[:, ~df.columns.str.contains('^Unnamed')]
                flash('Data Berhasil Ditambahkan','success')
            else:
                idx = int(idx)
                if idx >= 1:
                    idx -= 1
                elif idx == 0:
                    idx = 0  
                df.at[idx,'Title']= title
                df.at[idx,'Sumber']= sumber  
                df.at[idx,'Label']= label
                flash('Data Berhasil DiUbah','success')    
        elif request.form.get("Hapus"):
            idx = request.form["index"]
            idx = int(idx)
            if idx >= 1:
                idx -= 1
            elif idx == 0:
                idx = 0 
            df = df.drop(index=idx)
            df = df.reset_index(drop=True)
            flash('Data Berhasil Dihapus','success')      
        elif request.form.get("Proses"):
            textprocessing()
            cek_file = os.path.isfile('static/csv/Hasil_Crawling_Berita.csv')
            if(cek_file == True):    
                with open('static/csv/text_processing.csv', 'r') as f:
                    # init dataset
                        data = [dict(item) for item in csv.DictReader(f)]
                        
                        # display items per page
                        items_per_page = int(len(data))
                        
                        # starting index
                        index_from = 0;
                        
                        # ending index
                        index_to = index_from + items_per_page
                        
                        # init total pages
                        total_pages = range(int(len(data)))

                        for sentimen in data:
                            if(sentimen['Label'] == '1'):
                                sentimen['Label'] = 'Positif'
                            if(sentimen['Label'] == '-1'):
                                sentimen['Label'] = 'Negatif'
                            if(sentimen['Label'] == '0'):
                                sentimen['Label'] = 'Netral'

                        flash('Text Preprocessing Selesai','success')

                        # render content
                return render_template('hasil_labeling.html',data=data[index_from:index_to])

            if(cek_file == False):
                flash('Upload CSV Terlebih Dahulu','warning')
    # return redirect(request.url)

    df.to_csv("static/csv/Hasil_Crawling_Berita.csv",index=False)
    return redirect(request.url)



@app.route("/klasifikasi_berita", methods=['POST'])
def metodeKNN():

    if request.method == 'POST': 
            value = request.form["jumlah"]
            k = request.form["k"]

    evaluasi = modelKNN(value,k)
   
    session['my_var'] = evaluasi

    with open('static/csv/hasil_klasifikasi.csv', 'r') as f:
        # init dataset
        data = [dict(item) for item in csv.DictReader(f)]

        wc_positif = pd.DataFrame()
        wc_negatif = pd.DataFrame()
        wc_netral = pd.DataFrame()

        kata_positif = []
        kata_negatif = []
        kata_netral = []
        for item in data:
            if(item['Hasil_Prediksi'] == 'Positif'):
                kata_positif.append(item['Title_Join'])
            if(item['Hasil_Prediksi'] == 'Negatif'):
                kata_negatif.append(item['Title_Join'])
            if(item['Hasil_Prediksi'] == 'Netral'):
                kata_netral.append(item['Title_Join'])

        wc_positif["Title_Join"] = kata_positif
        wc_positif.to_csv("static/csv/positif.csv")
        
        wc_negatif["Title_Join"] = kata_negatif
        wc_negatif.to_csv("static/csv/negatif.csv")

        wc_netral["Title_Join"] = kata_netral
        wc_netral.to_csv("static/csv/netral.csv")

        df_positif = pd.read_csv("static/csv/positif.csv")
        df_negatif = pd.read_csv("static/csv/negatif.csv")
        df_netral = pd.read_csv("static/csv/netral.csv")

        def word_cloud(word,nama):
            df = word
            nama_file = nama
            allWords = ' '.join([twts for twts in df['Title_Join']])
            wordCloud = WordCloud(colormap="Blues", width=1600, height=800, random_state=30, max_font_size=200, min_font_size=20).generate(allWords)   

            plt.figure( figsize=(20,10), facecolor='k')
            plt.imshow(wordCloud, interpolation="bilinear")
            plt.axis('off')
            plt.savefig('static/img/'+nama_file+'.png', facecolor='k', bbox_inches='tight')

        if df_negatif.empty:
            new_row = {'Title_Join':'NaN'}
            df_negatif = df_negatif.append(new_row, ignore_index=True)
        elif df_positif.empty:
            new_row = {'Title_Join':'NaN'}
            df_positif = df_positif.append(new_row, ignore_index=True)
        elif df_netral.empty:
            new_row = {'Title_Join':'NaN'}
            df_netral = df_netral.append(new_row, ignore_index=True)

        word_cloud(df_positif,'wc_positif')
        word_cloud(df_negatif,'wc_negatif')
        word_cloud(df_netral,'wc_netral')

        # display items per page
        items_per_page = int(len(data))
        
        # starting index
        index_from = 0;
        
        # ending index
        index_to = index_from + items_per_page
        
        flash('Hasil Prediksi '+ value +' Data Testing Dengan Nilai K '+ k +' Selesai','success')

    with open('static/csv/Hasil_Crawling_Berita.csv', 'r') as g:
        data_slider = [dict(item) for item in csv.DictReader(g)]
        total_pages = range(int(len(data_slider)))

    return render_template('klasifikasi_berita.html',data=data[index_from:index_to], total_pages=total_pages)

@app.route("/visualisasi")
def visualisasi():

    cek_file = os.path.isfile('static/csv/hasil_klasifikasi.csv')
    if(cek_file == True):
        my_var = session.get('my_var', None)
        with open('static/csv/hasil_klasifikasi.csv', 'r') as f:
            # init dataset
            data = [dict(item) for item in csv.DictReader(f)]
            items_per_page = int(len(data))
            index_from = 0;
            index_to = index_from + items_per_page
            jumlah_data = range(int(len(data)))

            positif = 0
            negatif = 0
            netral = 0

            for sentimen in data:
                if(sentimen['Hasil_Prediksi'] == 'Positif'):
                    positif += 1
                if(sentimen['Hasil_Prediksi'] == 'Negatif'):
                    negatif += 1
                if(sentimen['Hasil_Prediksi'] == 'Netral'):
                    netral += 1
            
            if(my_var == None):
                return render_template('404.html')

        return render_template('visualisasi.html',data=data[index_from:index_to], jumlah_data=jumlah_data, positif=positif, negatif=negatif, netral=netral, my_var=my_var)        
    
    return render_template('404.html')


@app.errorhandler(jinja2.exceptions.TemplateNotFound)
def template_not_found(e):
    return not_found(e)

@app.errorhandler(404)
def not_found(e):
    return render_template('404.html')


if __name__ == '__main__':
    app.run(debug=True)
