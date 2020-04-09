import pandas as pd

def generate_csv(data, filename):
	df = pd.DataFrame(data)
	df.to_csv(filename, sep='\t')
