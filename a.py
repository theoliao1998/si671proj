import metapy

with open('msg/tutorial.toml', 'w') as f:
    f.write('type = "line-corpus"\n')
    f.write('store-full-text = true\n')

config = """prefix = "." # tells MeTA where to search for datasets

dataset = "msg" # a subfolder under the prefix directory
corpus = "tutorial.toml" # a configuration file for the corpus specifying its format & additional args

index = "msg-idx" # subfolder of the current working directory to place index files

query-judgements = "msg/msg-qrels.txt" # file containing the relevance judgments for this dataset

stop-words = "lemur-stopwords.txt"

[[analyzers]]
method = "ngram-word"
ngram = 1
filter = "default-unigram-chain"
"""
with open('msg_ir-config.toml', 'w') as f:
    f.write(config)

inv_idx = metapy.index.make_inverted_index('msg_ir-config.toml')





