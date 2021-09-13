def modelKNN(val,k):
  import ast
  import pandas as pd 

  hasil_preprocces = pd.read_csv("static/csv/text_processing.csv", usecols=["Title","Hasil_Stemming","Label"])

  hasil_preprocces = hasil_preprocces[['Title','Hasil_Stemming','Label']]
  hasil_preprocces.columns = ["Title","News_Title", "Label"]

  label = []
  for index, row in hasil_preprocces.iterrows():
      if row["Label"] == 1:
          label.append('Positif')
      if row["Label"] == -1:
          label.append('Negatif')
      if row["Label"] == 0:
          label.append('Netral')

  hasil_preprocces["Label"] = label

  def convert_text_list(texts):
      texts = ast.literal_eval(texts)
      return [text for text in texts]

  hasil_preprocces["News_Title_List"] = hasil_preprocces["News_Title"].apply(convert_text_list)

  def join_text_list(texts):
      texts = ast.literal_eval(texts)
      return ' '.join([text for text in texts])
  hasil_preprocces["Title_Join"] = hasil_preprocces["News_Title"].apply(join_text_list)

  x = hasil_preprocces['Title_Join']
  y = hasil_preprocces['Label']

  from sklearn.model_selection import train_test_split

  data_tes = int(val)/1000
  nilai_k = int(k)

  X_train, X_test, y_train, y_test = train_test_split(x, y, test_size=data_tes, random_state=42, shuffle=True)
  
  from sklearn.feature_extraction.text import TfidfVectorizer

  tf_idf = TfidfVectorizer()

  tf_idf_train = tf_idf.fit_transform(X_train)
  tf_idf_test = tf_idf.transform(X_test)
  
  from sklearn.neighbors import KNeighborsClassifier

  knn = KNeighborsClassifier(n_neighbors=nilai_k, metric='euclidean')
  clf = knn.fit(tf_idf_train,y_train)
  predicted = clf.predict(tf_idf_test)

  hasil_klasifikasi = pd.DataFrame()  

  hasil_klasifikasi['Label'] = y_test
  hasil_klasifikasi['Hasil_Prediksi'] = predicted

  hasil_klasifikasi = hasil_klasifikasi.join(hasil_preprocces['Title'], lsuffix='_caller', rsuffix='_other')
  hasil_klasifikasi = hasil_klasifikasi.join(hasil_preprocces['Title_Join'], lsuffix='_caller', rsuffix='_other')

  hasil_klasifikasi = hasil_klasifikasi[['Title','Title_Join', 'Label', 'Hasil_Prediksi']]

  # import library evaluation
  from sklearn.metrics import f1_score, recall_score, precision_score, confusion_matrix, accuracy_score

  # accuracy score
  akurasi = round(accuracy_score(y_test, predicted),4)*100

  # precision score
  presisi = round(precision_score(y_test, predicted,average='macro'),4)*100

  # recall score
  recall = round(recall_score(y_test, predicted,average='macro'),4)*100

  cf = pd.DataFrame(columns=['k','akurasi', 'presisi', 'recall'])
  k_range = range(1,51)  #1-50
  for k in k_range:
    knn_iterated=KNeighborsClassifier(n_neighbors=k, metric='euclidean')
    clf_iterated = knn_iterated.fit(tf_idf_train,y_train)
    predicted_iterated = clf_iterated.predict(tf_idf_test)

    # cf
    akurasi_iterated = round(accuracy_score(y_test, predicted_iterated),4)*100
    presisi_iterated = round(precision_score(y_test, predicted_iterated,average='macro'),4)*100
    recall_iterated = round(recall_score(y_test, predicted_iterated,average='macro'),4)*100

    cf.loc[k] = [k, akurasi_iterated, presisi_iterated, recall_iterated]

  cf.to_csv("static/csv/cf.csv")
  cf.to_excel("static/csv/cf.xlsx")

  evaluasi = []
  objek_evaluasi = {"akurasi" : akurasi, "presisi" : presisi, "recall" : recall, "data_tes" : val, "nilai_k" : nilai_k}
  evaluasi_copy = objek_evaluasi.copy()
  evaluasi.append(evaluasi_copy)

  hasil_klasifikasi.to_csv("static/csv/hasil_klasifikasi.csv")
  hasil_klasifikasi.to_excel("static/csv/hasil_klasifikasi.xlsx")

  return evaluasi