from . import lucene_codec
import ir_datasets
from ir_datasets.util import TarExtract, Cache
from ir_datasets.formats import BaseDocs, TrecDoc
from ir_datasets.indices import PickleLz4FullStore

_logger = ir_datasets.log.easy()

# A unique identifier for this dataset. To avoid name conflicts, consider prefixing
# identifiers with a person/org, as done here:
PREFIX = 'macavaney:anserini-'
NAME = f'{PREFIX}trec-robust04'

# where the content is cached
base_path = ir_datasets.util.home_path() / NAME


class AnseriniRobustDocs(BaseDocs):
    def __init__(self, dlc):
        super().__init__()
        self._dlc = dlc

    @ir_datasets.util.use_docstore
    def docs_iter(self):
        BeautifulSoup = ir_datasets.lazy_libs.bs4().BeautifulSoup
        it = lucene_codec.stored_fields_iter(self._dlc.path())
        for doc in _logger.pbar(it, desc='loading from lucene index'):
            doc_id = doc[0]
            doc_raw = doc[1]
            soup = BeautifulSoup(f'<OUTER>\n{doc_raw}\n</OUTER>', 'lxml')
            text = soup.get_text()
            yield TrecDoc(doc_id, text, doc_raw)

    def docs_cls(self):
        return TrecDoc

    def docs_store(self, field='doc_id'):
        return PickleLz4FullStore(
            path=f'{ir_datasets.util.home_path()/NAME}/docs.pklz4',
            init_iter_fn=self.docs_iter,
            data_cls=self.docs_cls(),
            lookup_field=field,
            index_fields=['doc_id'],
        )

    def docs_count(self):
        return self.docs_store().count()

    def docs_namespace(self):
        return 'trec-robust04'

    def docs_lang(self):
        return 'en'


DL_ANSERINI_ROBUST04 = ir_datasets.util.Download(
    [ir_datasets.util.RequestsDownload('https://git.uwaterloo.ca/jimmylin/anserini-indexes/raw/master/index-robust04-20191213.tar.gz')],
    expected_md5='15f3d001489c97849a010b0a4734d018')

DL_ANSERINI_ROBUST04 = Cache(TarExtract(DL_ANSERINI_ROBUST04, 'index-robust04-20191213/_h.fdt'), base_path/'lucene_source.fdt')

collection = AnseriniRobustDocs(DL_ANSERINI_ROBUST04)


for ds_name in ['trec-robust04', 'trec-robust04/fold1', 'trec-robust04/fold2', 'trec-robust04/fold3', 'trec-robust04/fold4', 'trec-robust04/fold5']:
    main_ds = ir_datasets.load(ds_name)
    dataset = ir_datasets.Dataset(
        collection,
        main_ds.queries_handler(),
        main_ds.qrels_handler(),
    )

    # Register the dataset with ir_datasets
    ir_datasets.registry.register(PREFIX + ds_name, dataset)
