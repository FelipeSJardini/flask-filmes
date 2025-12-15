import pandas as pd
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.metrics.pairwise import cosine_similarity

# criando o dataframe
df = pd.read_csv('final.csv')

# a função notna mapeia elementos existentes como elementos verdadeiros e não existentes como falsos
# esta operação remove as linhas mapeadas para falso
df = df[df['soup'].notna()]

# criando a matriz / vetor
count = CountVectorizer(stop_words='english')
count_matrix = count.fit_transform(df['soup'])

# objeto de similaridade: classificador
cosine_sim2 = cosine_similarity(count_matrix, count_matrix)

# redefinindo o índice do dataframe
df = df.reset_index()
indices = pd.Series(df.index, index = df['original_title'])

def get_recommendations(title):
   idx = indices[title]
   sim_scores = list(enumerate(cosine_sim2[idx]))
   sim_scores = sorted(sim_scores, key=lambda x: x[1], reverse=True)
   sim_scores = sim_scores[1:11]
   movie_indices = [i[0] for i in sim_scores]

   return df[['original_title','poster_link','runtime','release_date','weighted_rating']].iloc[movie_indices]
