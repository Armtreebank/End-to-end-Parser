# End-to-end Parser for Eastern Armenian

This repository contains necessary tools to parse raw Eastern Armenian text. It has a script, `run.sh`, which takes raw text as an input and produces a CoNLL-U file with lemmas, morphological features, part-of-speech tags and dependency trees.

* The parser segments the text into sentences and tokenizes them using ArmTreeBank's [Tokenizer module](https://github.com/Armtreebank/Tokenizer).
* Lemmatization, POS tagging and dependency parsing is performed by a neural network called [COMBO](https://github.com/360er0/COMBO), which is developed and open-sourced by Piotr Rybak and Alina Wroblewska from Institute of Computer Science, Polish Academy of Sciences. If you use this network, please cite [their paper](https://aclanthology.coli.uni-saarland.de/papers/K18-2004/k18-2004).
* We have trained COMBO on the training set of the [ArmTDP treebank](https://github.com/UniversalDependencies/UD_Armenian-ArmTDP) from UD v2.3. 
* The accuracy of the parser is far from perfect. It has been trained only on ~500 sentences. The table below shows the accuracy on the test set of the same treebank.

| Metric | Accuracy |
| ------ | -------- |
| Lemmatization | 88.05% |
| Part-of-speech tagging | 85.07% |
| Morphological features | 70.21% |
| Dependency parsing (Labelled attachment score) | 55.25% |


### Visualization of the current parser
The model is hosted on the AWS Elastic Beanstalk: <br />
http://end-to-end-parser-env.xthmm3wv2n.us-west-2.elasticbeanstalk.com/
![alt text](https://i.imgur.com/EPs4x14.png "Visualization")



### Instructions (for End to end parsing)

* Make sure you have all the requirements installed
```commandline
pip install -r requirements.txt
```

* Clone the repo (to get the submodules don't forget to include the `--recursive` flag)
```commandline
git clone --recursive https://github.com/Armtreebank/End-to-end-Parser.git
```

* Run the following command to get the `.conllu` file with predictions for every sentence of the input
```commandline
python3 predict.py --model_path path_to_model.pkl --input_path sample.txt --output_path sample.conllu
```


### Instructions (for COMBO training)
```commandline
cd COMBO
python3 -m src.main --mode autotrain --train train_data_path.conllu --valid valid_data_path.conllu --model model.pkl --force_trees
```

### Acknowledgements

This project is supported by [ANSEF](http://ansef.org/) grant Lingu-5008 and [ISTC](https://istc.am/?page_id=18534) Research Grant.
