# irds_robust_anserini

This is a version of the TREC Robust 2004 dataset for [ir_datasets](https://ir-datasets.com)
that's made available through the public Anserini index [here](https://git.uwaterloo.ca/jimmylin/anserini-indexes/raw/master/index-robust04-20191213.tar.gz).
Note that you should not use this without proper paperwork from TREC.

The dataset IDs mirror those for the original `trec-robust04` datasets that are
loaded from source files:

 - `macavaney:anserini-trec-robust04`
 - `macavaney:anserini-trec-robust04/fold1`
 - `macavaney:anserini-trec-robust04/fold2`
 - `macavaney:anserini-trec-robust04/fold3`
 - `macavaney:anserini-trec-robust04/fold4`
 - `macavaney:anserini-trec-robust04/fold5`

The query and qrels handlers are taken from the original `trec-robust04` dataset.
The only difference is the docs handler.

## Sample usage

First install:

```bash
pip install git+https://github.com/seanmacavaney/irds_robust_anserini.git
```

Using with the python API:

```python
import ir_datasets
import irds_robust_anserini

dataset = ir_datasets.load('macavaney:anserini-trec-robust04')
```

## Differences with original `trec-robust04` dataset

 1. The order that the documents appear are different.
 2. There are 125 fewer documents in this version. These are all empty documents from
    the Federal Register that Anserini presumably discarded when indexing.

## Citing

The dataset should be cited as:

```
@inproceedings{Voorhees2004OverviewRobust,
  title={Overview of the TREC 2004 Robust Retrieval Track},
  author={Ellen Voorhees},
  booktitle={TREC},
  year={2004}
}
```

You should also cite Anserini for providing the documents:

```
@article{Yang2017AnseriniET,
  title={Anserini: Enabling the Use of Lucene for Information Retrieval Research},
  author={Peilin Yang and Hui Fang and Jimmy Lin},
  journal={SIGIR},
  year={2017}
}
```
