# Readme distsupvis_adr

This project contains the code for the bachelor thesis: "Extraktion von Medikamentennebenwirkungen aus Texten: Ein Ansatz mit Distant-Supervision". It is a collection of scripts to run a distant supervised learning algorithm for adversed drug reactions. Some parts of downloading and preparing data take a longer time. Because of this, the project does not contain a `makefile`, but some jupiter notebook scripts for data preparation and the learning algorithm. This has to be done in a certain row:

1. Execute code in `project_preparation.ipynb`. Be aware that some steps can take many hours if you want to use many data files
2. Execute code in `data_revision_proto.ipynb`
3. Now you can train and evaluate the classifier in `train_0-200_sample_rate_0p1.ipynb` and `train_0-200_sample_rate_0p5.ipynb`
