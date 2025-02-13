import unittest
from typing import Any, Union

from stereo.core import StereoExpData
from stereo.core.ms_data import MSData
from stereo.io import read_gem
from stereo.utils._download import _download
from stereo.utils.data_helper import merge


class TestBatchIntegration(unittest.TestCase):
    DATA_A1: Union[StereoExpData, Any]
    DATA_A2: Union[StereoExpData, Any]

    DEMO_132BR_A1_URL = 'https://pan.genomics.cn/ucdisk/api/2.0/share/link/download?' \
                        'shareEventId=share_2022928142945896_010df2aa7d344d97a610557de7bad81b&' \
                        'nodeId=8a80804a837dc46f01838302491a21e0&code='

    DEMO_132BR_A2_URL = 'https://pan.genomics.cn/ucdisk/api/2.0/share/link/download?' \
                        'shareEventId=share_2022928142945896_010df2aa7d344d97a610557de7bad81b&' \
                        'nodeId=8a80804a837dc46f01838302df5b21e2&code='

    @classmethod
    def setUpClass(cls) -> None:
        input_file_1 = _download(TestBatchIntegration.DEMO_132BR_A1_URL)
        input_file_2 = _download(TestBatchIntegration.DEMO_132BR_A2_URL)
        data_a1 = read_gem(input_file_1)
        data_a1.tl.cal_qc()
        data_a1.tl.filter_cells(max_n_genes_by_counts=4000, pct_counts_mt=5, inplace=True)

        data_a2 = read_gem(input_file_2)
        data_a2.tl.cal_qc()
        data_a2.tl.filter_cells(max_n_genes_by_counts=4500, pct_counts_mt=7, inplace=True)

        cls.MS_DATA = MSData(_data_list=[data_a1, data_a2], _names=['a1', 'a2'])

        cls.DATA = merge(data_a1, data_a2)
        cls.DATA.tl.normalize_total()
        cls.DATA.tl.log1p()
        cls.DATA.tl.pca(use_highly_genes=False, n_pcs=50, res_key='pca')

    def test_batches_integrate(self):
        self.DATA.tl.batches_integrate(pca_res_key='pca', res_key='pca_integrated')

        self.DATA.tl.neighbors(pca_res_key='pca_integrated', n_pcs=50, res_key='neighbors_integrated')
        self.DATA.tl.umap(pca_res_key='pca_integrated', neighbors_res_key='neighbors_integrated',
                          res_key='umap_integrated')

        self.DATA.tl.leiden(neighbors_res_key='neighbors_integrated', res_key='leiden')
        self.DATA.plt.cluster_scatter(res_key='leiden', out_path="./image_path/batch_integrated_leiden.png")

    def test_ms_batches_integrate(self):
        self.MS_DATA.merge_for_batching_integrate()
        self.MS_DATA.merged_data.tl.normalize_total()
        self.MS_DATA.merged_data.tl.log1p()
        self.MS_DATA.merged_data.tl.pca(use_highly_genes=False, n_pcs=50, res_key='pca')
        self.MS_DATA.tl.batches_integrate(pca_res_key='pca', res_key='pca_integrated')
