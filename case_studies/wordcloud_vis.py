from rdflib import Graph, Namespace
from wordcloud import WordCloud
import matplotlib.pyplot as plt
import os, nltk, string

nltk.download('stopwords')
from nltk.corpus import stopwords

#__TTL_FILENAME = '2025-04-14T20-50-36_CaseStudyPythonProgramming_provenance_traces.ttl'
__TTL_FILENAME = '2025-04-15T00-40-12_CaseStudyReadmeCreation_provenance_traces.ttl'

__TTL_FOLDER = '' 

script_dir = os.path.dirname(os.path.abspath(__file__))
ttl_path = os.path.join(script_dir, __TTL_FOLDER, __TTL_FILENAME)

g = Graph()
g.parse(ttl_path, format = 'turtle')

PTO = Namespace('https://github.com/PR0CK0/ProvTracer/tree/main/procko.provtracer/grapher/provtracer-o.ttl#')

texts = []
for s, p, o in g.triples((None, PTO.response, None)):
    if isinstance(o, str):
        texts.append(o)

full_text = ' '.join(texts).lower()

tokens = full_text.translate(str.maketrans('', '', string.punctuation)).split()
filtered = [word for word in tokens if word not in stopwords.words('english') and len(word) > 2]

processed_text = ' '.join(filtered)

wc = WordCloud(width = 2400, height = 1200, background_color = 'white').generate(processed_text)

plt.figure(figsize = (12, 6))
plt.imshow(wc, interpolation = 'bilinear')
plt.axis('off')
plt.title("Word Cloud of ProvTracer Responses", fontsize = 16)
plt.show()