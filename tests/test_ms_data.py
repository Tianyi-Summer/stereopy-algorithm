import copy
import unittest

from stereo.core.ms_data import MSData
from stereo.io.reader import read_gef
from stereo.utils._download import _download


class MSDataTestCases(unittest.TestCase):

    DEMO_DATA_URL = 'https://pan.genomics.cn/ucdisk/api/2.0/share/link/download?' \
                    'shareEventId=share_2022928142945896_010df2aa7d344d97a610557de7bad81b&' \
                    'nodeId=8a80804a837dc46f018382c40ca51af0&code='

    def setUp(self, *args, **kwargs):
        super().setUp()

        self.file_path = _download(MSDataTestCases.DEMO_DATA_URL)

        self.ms_data = MSData()
        # TODO should download from net
        self.obj = read_gef(self.file_path)
        self.obj2 = copy.deepcopy(self.obj)

        self.ms_data.add_data(self.obj)
        self.ms_data.add_data(self.obj2, 'a')

    def test_length_match_init(self):
        ms_data = MSData(_data_list=[copy.deepcopy(self.obj), copy.deepcopy(self.obj2)], _names=['a', 'c'])
        self.assertEqual(len(ms_data.names), len(ms_data.data_list))
        self.assertIs(ms_data[0], ms_data['a'])
        self.assertIs(ms_data[1], ms_data['c'])

    def test_length_not_match_init(self):
        ms_data = MSData(_data_list=[copy.deepcopy(self.obj), copy.deepcopy(self.obj2)], _names=['a'])
        self.assertEqual(len(ms_data.names), len(ms_data.data_list))
        self.assertIs(ms_data[0], ms_data['a'])
        self.assertIs(ms_data[1], ms_data['0'])

    def test_add(self):
        self.assertEqual(len(self.ms_data), 2)
        self.assertIs(self.ms_data[0], self.obj)
        self.assertIs(self.ms_data[1], self.obj2)

        obj3 = read_gef(self.file_path)
        self.ms_data += obj3
        obj4 = read_gef(self.file_path)
        self.ms_data += obj4
        self.assertEqual(len(self.ms_data), 4)

        self.assertIs(self.ms_data[2], obj3)
        self.assertIs(self.ms_data[3], obj4)

    def test_add_path(self):
        self.ms_data.add_data(self.file_path)

    def test_multi_add(self):
        self.ms_data.add_data(copy.deepcopy(self.obj2), 'c')
        self.assertIs(self.ms_data['0'], self.ms_data[0])
        self.assertIs(self.ms_data['c'], self.ms_data[2])

    def test_multi_add_path(self):
        self.ms_data.add_data(
            [
                '/mnt/d/projects/stereopy_dev/demo_data/SS200000135TL_D1/SS200000135TL_D1.tissue.gef',
                '/mnt/d/projects/stereopy_dev/demo_data/SS200000135TL_D1/SS200000135TL_D1_script_res_gem.h5ad',
                '/mnt/d/projects/stereopy_dev/demo_data/SS200000135TL_D1/SS200000135TL_D1.tissue.gem'
            ],
            [
                'z',
                'x',
                'y'
            ],
            bin_size=[100, 100, 200],
            bin_type=['bins', 'cell_bins', 'bins'],
            spatial_key=[None, None, 'spatial']
        )

    def test_del_data(self):
        self.ms_data.del_data('0')
        self.assertNotIn('0', self.ms_data)
        self.assertEqual(len(self.ms_data), 1)

    def test_names(self):
        for idx, data_obj in enumerate(self.ms_data.data_list):
            self.assertIs(self.ms_data[self.ms_data._names[idx]], data_obj)

    def test_rename(self):
        # rename with a not existed key and three existed keys
        obj_0 = self.ms_data['0']
        obj_1 = self.ms_data['a']
        self.ms_data.rename({'0': '100', 'a': '101'})
        self.assertIs(obj_0, self.ms_data['100'])
        self.assertIs(obj_1, self.ms_data['101'])
        self.assertNotIn('cc', self.ms_data._names)

    def test_names_order(self):
        for idx, name in enumerate(self.ms_data._names):
            self.assertIs(self.ms_data[name], self.ms_data[idx])

    def test_reset_name(self):
        self.ms_data.reset_name()
        self.assertIs(self.ms_data['0'], self.obj)
        self.assertIs(self.ms_data['1'], self.obj2)

    def test_name_contain(self):
        self.assertIn('0', self.ms_data)
        self.assertIn(self.obj, self.ms_data)
        self.assertIn('a', self.ms_data)
        self.assertIn(self.obj2, self.ms_data)

    def test_tl_method(self):
        self.ms_data.tl.log1p()

    def test_tl_method_algorithm_base(self):
        self.ms_data.tl.log1p_fake()

    def test_tl_ms_data_method_algorithm_base(self):
        self.ms_data.tl.ms_log1p_fake()

    def test_plt(self):
        self.ms_data.tl.cal_qc()
        self.ms_data.plt.violin()
        self.ms_data.plt.violin(out_paths=['image_path/violin1.png', 'image_path/violin2.png'])

    def test_num_slice(self):
        self.assertEqual(len(self.ms_data), self.ms_data.num_slice, len(self.ms_data.data_list))

    def test_copy(self):
        self.assertIs(copy.deepcopy(self.ms_data), self.ms_data, copy.copy(self.ms_data))

    def test_slice(self):
        test_slice = self.ms_data[1:]
        self.assertEqual(len(test_slice._data_list), 1)
        self.assertIs(test_slice._data_list[0], self.ms_data[1])

        name_tuple = ('a', '0')
        test_slice = self.ms_data[name_tuple:]
        self.assertEqual(len(test_slice._data_list), len(name_tuple))
        self.assertIs(test_slice._data_list[0], self.ms_data['a'])
        self.assertIs(test_slice._data_list[1], self.ms_data['0'])

        name_list = ['a', '0']
        test_slice = self.ms_data[name_list:]
        self.assertEqual(len(test_slice._data_list), len(name_list))
        self.assertIs(test_slice._data_list[0], self.ms_data['a'])
        self.assertIs(test_slice._data_list[1], self.ms_data['0'])

        test_slice.tl.log1p()

    def test_clustering(self):
        self.ms_data.tl.cal_qc()
        self.ms_data.tl.filter_cells(min_gene=200, min_n_genes_by_counts=3, max_n_genes_by_counts=7000, pct_counts_mt=8,
                                     inplace=False)
        self.ms_data.tl.log1p()
        self.ms_data.tl.normalize_total(target_sum=1e4)
        self.ms_data.tl.pca(use_highly_genes=False, hvg_res_key='highly_variable_genes', n_pcs=20, res_key='pca',
                            svd_solver='arpack')
        self.ms_data.tl.neighbors(pca_res_key='pca', n_pcs=30, res_key='neighbors', n_jobs=8)
        self.ms_data.tl.umap(pca_res_key='pca', neighbors_res_key='neighbors', res_key='umap', init_pos='spectral')
        self.ms_data.tl.leiden(neighbors_res_key='neighbors', res_key='leiden')


if __name__ == "__main__":
    unittest.main()
