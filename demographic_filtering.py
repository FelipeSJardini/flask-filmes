import pandas as pd

df = pd.read_csv('final.csv')

# classificação de dataframe: em relação à coluna weighted_rating em ordem crescente
df = df.sort_values("weighted_rating", ascending=False)

output = df[['original_title', 'poster_link','runtime','release_date','weighted_rating']].head(20)