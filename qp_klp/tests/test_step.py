# -----------------------------------------------------------------------------
# Copyright (c) 2014--, The Qiita Development Team.
#
# Distributed under the terms of the BSD 3-clause License.
#
# The full license is in the file LICENSE, distributed with this software.
# -----------------------------------------------------------------------------
from unittest import TestCase
from qp_klp.Step import Step
from sequence_processing_pipeline.Pipeline import Pipeline
from os.path import join, abspath
from functools import partial
from os import makedirs, chmod, access, W_OK
from shutil import rmtree
from os import environ, remove, getcwd
from json import dumps


class FakeClient():
    def __init__(self):
        self.cwd = getcwd()
        self.base_path = join(self.cwd, 'qp_klp/tests/data/QDir')
        self.qdirs = {'Demultiplexed': 'Demultiplexed',
                      'beta_div_plots': 'analysis/beta_div_plots',
                      'rarefaction_curves': 'analysis/rarefaction_curves',
                      'taxa_summary': 'analysis/taxa_summary',
                      'q2_visualization': 'working_dir',
                      'distance_matrix': 'working_dir',
                      'ordination_results': 'working_dir',
                      'alpha_vector': 'working_dir',
                      'FASTQ': 'FASTQ',
                      'BIOM': 'BIOM',
                      'per_sample_FASTQ': 'per_sample_FASTQ',
                      'SFF': 'SFF',
                      'FASTA': 'FASTA',
                      'FASTA_Sanger': 'FASTA_Sanger',
                      'FeatureData': 'FeatureData',
                      'job-output-folder': 'job-output-folder',
                      'BAM': 'BAM',
                      'VCF': 'VCF',
                      'SampleData': 'SampleData',
                      'uploads': 'uploads'}

        self.samples_in_13059 = ['13059.SP331130A04', '13059.AP481403B02',
                                 '13059.LP127829A02', '13059.BLANK3.3B',
                                 '13059.EP529635B02', '13059.EP542578B04',
                                 '13059.EP446602B01', '13059.EP121011B01',
                                 '13059.EP636802A01', '13059.SP573843A04']

        # note these samples have known tids, but aren't in good-sample-sheet.
        self.samples_in_11661 = ['11661.1.24', '11661.1.57', '11661.1.86',
                                 '11661.10.17', '11661.10.41', '11661.10.64',
                                 '11661.11.18', '11661.11.43', '11661.11.64',
                                 '11661.12.15']

        self.samples_in_6123 = ['3A', '4A', '5B', '6A', 'BLANK_41_12G', '7A',
                                '8A', 'ISB', 'GFR', '6123']

        self.info_in_11661 = {'number-of-samples': 10,
                              'categories': ['sample_type', 'tube_id']}

        self.info_in_13059 = {'number-of-samples': 10,
                              'categories': ['anonymized_name',
                                             'collection_timestamp',
                                             'description',
                                             'dna_extracted',
                                             'elevation', 'empo_1',
                                             'empo_2', 'empo_3',
                                             'env_biome', 'env_feature',
                                             'env_material',
                                             'env_package',
                                             'geo_loc_name', 'host_age',
                                             'host_age_units',
                                             'host_body_habitat',
                                             'host_body_mass_index',
                                             'host_body_product',
                                             'host_body_site',
                                             'host_common_name',
                                             'host_height',
                                             'host_height_units',
                                             'host_life_stage',
                                             'host_scientific_name',
                                             'host_subject_id',
                                             'host_taxid', 'host_weight',
                                             'host_weight_units',
                                             'latitude', 'longitude',
                                             'nyuid',
                                             'physical_specimen_location',
                                             'physical_specimen_remaining',
                                             'predose_time',
                                             'sample_type',
                                             'scientific_name', 'sex',
                                             'subject_id', 'taxon_id',
                                             'title', 'tube_id']}

        # Study not in qiita-rc. Faking results.
        self.info_in_6123 = {'number-of-samples': 10,
                             'categories': ['sample_type', 'subject_id',
                                            'title']}

        self.tids_13059 = {"header": ["tube_id"],
                           "samples": {'13059.SP331130A04': ['SP331130A-4'],
                                       '13059.AP481403B02': ['AP481403B-2'],
                                       '13059.LP127829A02': ['LP127829A-2'],
                                       '13059.BLANK3.3B': ['BLANK3.3B'],
                                       '13059.EP529635B02': ['EP529635B02'],
                                       '13059.EP542578B04': ['EP542578B-4'],
                                       '13059.EP446602B01': ['EP446602B-1'],
                                       '13059.EP121011B01': ['EP121011B-1'],
                                       '13059.EP636802A01': ['EP636802A-1'],
                                       '13059.SP573843A04': ['SP573843A-4']}}

        self.tids_11661 = {"header": ["tube_id"],
                           "samples": {"11661.1.24": ["1.24"],
                                       "11661.1.57": ["1.57"],
                                       "11661.1.86": ["1.86"],
                                       "11661.10.17": ["10.17"],
                                       "11661.10.41": ["10.41"],
                                       "11661.10.64": ["10.64"],
                                       "11661.11.18": ["11.18"],
                                       "11661.11.43": ["11.43"],
                                       "11661.11.64": ["11.64"],
                                       "11661.12.15": ["12.15"]}}

        for key in self.qdirs:
            self.qdirs[key] = join(self.base_path, self.qdirs[key])

        for qdir in self.qdirs:
            makedirs(self.qdirs[qdir], exist_ok=True)

    def get(self, url):
        m = {'/api/v1/study/11661/samples': self.samples_in_11661,
             '/api/v1/study/11661/samples/categories=tube_id': self.tids_11661,
             '/api/v1/study/11661/samples/info': self.info_in_11661,
             '/api/v1/study/13059/samples': self.samples_in_13059,
             '/api/v1/study/13059/samples/categories=tube_id': self.tids_13059,
             '/api/v1/study/13059/samples/info': self.info_in_13059,
             '/api/v1/study/6123/samples': self.samples_in_6123,
             '/api/v1/study/6123/samples/info': self.info_in_6123,
             '/qiita_db/artifacts/types/': self.qdirs}

        if url in m:
            return m[url]

        return None


class BaseStepTests(TestCase):
    '''
    BaseStepTests contains all the configuration information and helper
    functions used by every child StepTests class. This class does not
    include any tests. All tests defined in this class will be inherited by
    every child and will consequently be run multiple times. Hence, general
    functionality is instead tested by BasicStepSteps class.
    '''
    CONFIGURATION = {
        "configuration": {
            "pipeline": {
                "archive_path": ("sequence_processing_pipeline/tests/data/"
                                 "sequencing/knight_lab_completed_runs"),
                "search_paths": ["/tmp", "qp_klp/tests/data"],
                "amplicon_search_paths": ["/tmp", "qp_klp/tests/data"]
            },
            "bcl2fastq": {
                "nodes": 1,
                "nprocs": 16,
                "queue": "qiita",
                "wallclock_time_in_hours": 36,
                "modules_to_load": ["bcl2fastq_2.20.0.422"],
                "executable_path": "bcl2fastq",
                "per_process_memory_limit": "10gb"
            },
            "bcl-convert": {
                "nodes": 1,
                "nprocs": 16,
                "queue": "qiita",
                "wallclock_time_in_hours": 36,
                "modules_to_load": ["bclconvert_3.7.5"],
                "executable_path": "bcl-convert",
                "per_process_memory_limit": "10gb"
            },
            "qc": {
                "nodes": 1,
                "nprocs": 16,
                "queue": "qiita",
                "wallclock_time_in_hours": 1,
                "minimap_databases": ["/databases/minimap2/human-phix-db.mmi"],
                "kraken2_database": "/databases/minimap2/hp_kraken-db.mmi",
                "modules_to_load": ["fastp_0.20.1", "samtools_1.12",
                                    " minimap2_2.18"],
                "fastp_executable_path": "fastp",
                "minimap2_executable_path": "minimap2",
                "samtools_executable_path": "samtools",
                "job_total_memory_limit": "20gb",
                "job_pool_size": 30,
                "job_max_array_length": 1000
            },
            "seqpro": {
                "seqpro_path": "seqpro",
                "modules_to_load": []
            },
            "fastqc": {
                "nodes": 1,
                "nprocs": 16,
                "queue": "qiita",
                "nthreads": 16,
                "wallclock_time_in_hours": 1,
                "modules_to_load": ["fastqc_0.11.5"],
                "fastqc_executable_path": "fastqc",
                "multiqc_executable_path": "multiqc",
                "multiqc_config_file_path": ("sequence_processing_pipeline/"
                                             "multiqc-bclconvert-config.yaml"),
                "job_total_memory_limit": "20gb",
                "job_pool_size": 30,
                "job_max_array_length": 1000
            }
        }
    }

    def setUp(self):
        package_root = abspath('./qp_klp')
        cc_path = partial(join, package_root, 'tests', 'data')
        self.good_config_file = join(package_root, 'configuration.json')
        self.good_run_id = '211021_A00000_0000_SAMPLE'
        self.good_sample_sheet_path = cc_path('good-sample-sheet.csv')
        self.good_mapping_file_path = cc_path('good-mapping-file.txt')
        self.good_transcript_sheet_path = cc_path('good-sample-sheet-'
                                                  'transcriptomics.csv')
        self.output_file_path = cc_path('output_dir')
        self.qiita_id = '077c4da8-74eb-4184-8860-0207f53623be'
        makedirs(self.output_file_path, exist_ok=True)

        self.pipeline = Pipeline(None, self.good_run_id,
                                 self.good_sample_sheet_path, None,
                                 self.output_file_path, self.qiita_id,
                                 Step.METAGENOMIC_TYPE,
                                 BaseStepTests.CONFIGURATION)

        self.config = BaseStepTests.CONFIGURATION['configuration']

        self.fake_bin_path = self._get_searchable_path()

        self.delete_these = []

    def _get_searchable_path(self):
        searchable_paths = []

        if 'CONDA_PREFIX' in environ:
            # create fake binaries in bin directory of Conda environment
            searchable_paths.append(environ['CONDA_PREFIX'] + '/bin')
        else:
            # if CONDA_PREFIX doesn't exist, select a path from a list of
            # searchable paths that contains 'env' and assume it's writable.
            tmp = environ['PATH']
            searchable_paths += tmp.split(':')

        for a_path in searchable_paths:
            if access(a_path, W_OK):
                return a_path

    def _create_fake_bin(self, name, content):
        tmp = join(self.fake_bin_path, name)
        with open(tmp, 'w') as f:
            f.write(f"#!/bin/sh\n{content}\n")
        chmod(tmp, 0o777)
        self.delete_these.append(tmp)
        return tmp

    def _create_test_input(self, stage):
        if stage >= 1:
            fake_path = join(self.output_file_path, 'ConvertJob', 'logs')
            makedirs(fake_path, exist_ok=True)

            self._create_fake_bin('sbatch', "echo 'Submitted "
                                            "batch job 9999999'")

            self._create_fake_bin('sacct', "echo '9999999|99999999-9999-9999"
                                           "-9999-999999999999.txt|COMPLETED"
                                           "|09:53:41|0:0'")

        if stage >= 2:
            fake_path = join(self.output_file_path, 'QCJob', 'logs')
            makedirs(fake_path, exist_ok=True)

            exp = {'Feist_11661': ['CDPH-SAL_Salmonella_Typhi_MDL-143',
                                   'CDPH-SAL_Salmonella_Typhi_MDL-144',
                                   'CDPH-SAL_Salmonella_Typhi_MDL-145',
                                   'CDPH-SAL_Salmonella_Typhi_MDL-146',
                                   'CDPH-SAL_Salmonella_Typhi_MDL-147'],
                   'Gerwick_6123': ['3A', '4A', '5B', '6A', '7A'],
                   'NYU_BMS_Melanoma_13059': ['AP581451B02', 'EP256645B01',
                                              'EP112567B02', 'EP337425B01',
                                              'LP127890A01']}
            for project in exp:
                fake_path = join(self.output_file_path, 'ConvertJob', project)
                makedirs(fake_path, exist_ok=True)

                for sample in exp[project]:
                    r1 = join(fake_path, f'{sample}_SXXX_L001_R1_001.fastq.gz')
                    r2 = join(fake_path, f'{sample}_SXXX_L001_R2_001.fastq.gz')

                    for file_path in [r1, r2]:
                        with open(file_path, 'w') as f:
                            f.write("This is a file.")

    def _delete_test_output(self):
        rmtree(self.output_file_path)
        for fake_bin in self.delete_these:
            remove(fake_bin)


class BasicStepTests(BaseStepTests):
    def setUp(self):
        super().setUp()

    def test_creation(self):
        # Test base-class creation method, even though base-class will never
        # be instantiated by itself in normal usage.
        self._delete_test_output()

        with self.assertRaisesRegex(ValueError, "A pipeline object is needed"
                                                " to initialize Step"):
            Step(None, self.qiita_id, None)

        with self.assertRaisesRegex(ValueError, "A Qiita job-id is needed to "
                                                "initialize Step"):
            Step(self.pipeline, None, None)

        step = Step(self.pipeline, self.qiita_id, None)

        self.assertIsNotNone(step)

    def test_convert_bcl_to_fastq(self):
        self._delete_test_output()
        self._create_test_input(1)

        step = Step(self.pipeline, self.qiita_id, None)

        fake_path = join(self.output_file_path, 'ConvertJob', 'logs')
        makedirs(fake_path, exist_ok=True)

        step._convert_bcl_to_fastq(self.config['bcl-convert'],
                                   self.good_sample_sheet_path)

    def test_quality_control(self):
        self._delete_test_output()
        self._create_test_input(2)

        fake_path = join(self.output_file_path, 'QCJob', 'logs')
        makedirs(fake_path, exist_ok=True)

        exp = {'Feist_11661': ['CDPH-SAL_Salmonella_Typhi_MDL-143',
                               'CDPH-SAL_Salmonella_Typhi_MDL-144',
                               'CDPH-SAL_Salmonella_Typhi_MDL-145',
                               'CDPH-SAL_Salmonella_Typhi_MDL-146',
                               'CDPH-SAL_Salmonella_Typhi_MDL-147'],
               'Gerwick_6123': ['3A', '4A', '5B', '6A', '7A'],
               'NYU_BMS_Melanoma_13059': ['AP581451B02', 'EP256645B01',
                                          'EP112567B02', 'EP337425B01',
                                          'LP127890A01']}
        for project in exp:
            fake_path = join(self.output_file_path, 'ConvertJob', project)
            makedirs(fake_path, exist_ok=True)

            for sample in exp[project]:
                r1 = join(fake_path, f'{sample}_SXXX_L001_R1_001.fastq.gz')
                r2 = join(fake_path, f'{sample}_SXXX_L001_R2_001.fastq.gz')

                for file_path in [r1, r2]:
                    with open(file_path, 'w') as f:
                        f.write("This is a file.")

        step = Step(self.pipeline, self.qiita_id, None)
        step._quality_control(self.config['qc'], self.good_sample_sheet_path)

    def create_config_file(self):
        tmp_path = join('.', 'tmp.config')
        with open(tmp_path, 'w') as f:
            f.write(dumps(BaseStepTests.CONFIGURATION, indent=2))

        self.delete_these.append(tmp_path)
        return tmp_path

    def test_generate_pipeline(self):
        config_file_path = self.create_config_file()

        pipeline = Step.generate_pipeline(Step.METAGENOMIC_TYPE,
                                          self.good_sample_sheet_path,
                                          1,
                                          config_file_path,
                                          self.good_run_id,
                                          self.output_file_path,
                                          self.qiita_id)

        self.assertIsNotNone(pipeline)

        pipeline = Step.generate_pipeline(Step.AMPLICON_TYPE,
                                          self.good_mapping_file_path,
                                          1,
                                          config_file_path,
                                          self.good_run_id,
                                          self.output_file_path,
                                          self.qiita_id)

        self.assertIsNotNone(pipeline)

        pipeline = Step.generate_pipeline(Step.METATRANSCRIPTOMIC_TYPE,
                                          self.good_transcript_sheet_path,
                                          1,
                                          config_file_path,
                                          self.good_run_id,
                                          self.output_file_path,
                                          self.qiita_id)

        self.assertIsNotNone(pipeline)

    def test_get_project_info(self):
        obs = self.pipeline.get_project_info()

        exp = [{'project_name': 'NYU_BMS_Melanoma_13059', 'qiita_id': '13059'},
               {'project_name': 'Feist_11661', 'qiita_id': '11661'},
               {'project_name': 'Gerwick_6123', 'qiita_id': '6123'}]

        self.assertEqual(obs, exp)

    def test_parse_prep_file(self):
        good_prep_file = join('qp_klp', 'tests', 'good-prep-file-small.txt')

        obs = Step.parse_prep_file(good_prep_file)

        # assert that prep-files that begin with sample-names of the form
        # '363192526', '1e-3', and '123.000' are parsed as strings instead of
        # numeric values.
        exp = {'363192526': {'experiment_design_description': 'sample project',
                             'library_construction_protocol': ('Knight Lab Kap'
                                                               'a HyperPlus'),
                             'platform': 'Illumina', 'run_center': 'KLM',
                             'run_date': '2022-04-18',
                             'run_prefix': '363192526_S9_L001',
                             'sequencing_meth': 'sequencing by synthesis',
                             'center_name': 'UCSD',
                             'center_project_name': 'Sample_Project',
                             'instrument_model': 'Illumina iSeq',
                             'runid': '20220101_FS10001776_07_ABC12345-4567',
                             'lane': '1', 'sample project': 'Sample_Project',
                             'well_description': ('Sample_Project_99999_1-'
                                                  '4.363192526.A3'),
                             'i5_index_id': 'iTru5_09_A',
                             'sample_plate': 'Sample_Project_99999_1-4',
                             'index2': 'TCTGAGAG', 'index': 'CATCTACG',
                             'sample_well': 'A3',
                             'i7_index_id': 'iTru7_114_05',
                             'raw_reads': '10749',
                             'quality_filtered_reads': '1',
                             'non_host_reads': '4'},
               '363192073': {'experiment_design_description': 'sample project',
                             'library_construction_protocol': ('Knight Lab Ka'
                                                               'pa HyperPlus'),
                             'platform': 'Illumina', 'run_center': 'KLM',
                             'run_date': '2022-04-18',
                             'run_prefix': '363192073_S195_L001',
                             'sequencing_meth': 'sequencing by synthesis',
                             'center_name': 'UCSD',
                             'center_project_name': 'Sample_Project',
                             'instrument_model': 'Illumina iSeq',
                             'runid': '20220101_FS10001776_07_ABC12345-4567',
                             'lane': '1', 'sample project': 'Sample_Project',
                             'well_description': ('Sample_Project_99999_1-'
                                                  '4.363192073.F1'),
                             'i5_index_id': 'iTru5_103_A',
                             'sample_plate': 'Sample_Project_99999_1-4',
                             'index2': 'TGGTCCTT', 'index': 'GCAATTCG',
                             'sample_well': 'F1',
                             'i7_index_id': 'iTru7_305_11',
                             'raw_reads': '16435',
                             'quality_filtered_reads': '2',
                             'non_host_reads': '5'},
               '363193755': {'experiment_design_description': 'sample project',
                             'library_construction_protocol': ('Knight Lab Ka'
                                                               'pa HyperPlus'),
                             'platform': 'Illumina', 'run_center': 'KLM',
                             'run_date': '2022-04-18',
                             'run_prefix': '363193755_S7_L001',
                             'sequencing_meth': 'sequencing by synthesis',
                             'center_name': 'UCSD',
                             'center_project_name': 'Sample_Project',
                             'instrument_model': 'Illumina iSeq',
                             'runid': '20220101_FS10001776_07_ABC12345-4567',
                             'lane': '1', 'sample project': 'Sample_Project',
                             'well_description': ('Sample_Project_99999_1-'
                                                  '4.363193755.M1'),
                             'i5_index_id': 'iTru5_07_A',
                             'sample_plate': 'Sample_Project_99999_1-4',
                             'index2': 'GGTGTCTT', 'index': 'GATTGCTC',
                             'sample_well': 'M1',
                             'i7_index_id': 'iTru7_114_03',
                             'raw_reads': '14303',
                             'quality_filtered_reads': '3',
                             'non_host_reads': '6'},
               '1e-3': {'experiment_design_description': 'sample project',
                        'library_construction_protocol': ('Knight Lab Kapa '
                                                          'HyperPlus'),
                        'platform': 'Illumina', 'run_center': 'KLM',
                        'run_date': '2022-04-18',
                        'run_prefix': '363192073_S195_L001',
                        'sequencing_meth': 'sequencing by synthesis',
                        'center_name': 'UCSD',
                        'center_project_name': 'Sample_Project',
                        'instrument_model': 'Illumina iSeq',
                        'runid': '20220101_FS10001776_07_ABC12345-4567',
                        'lane': '1', 'sample project': 'Sample_Project',
                        'well_description': ('Sample_Project_99999_1-'
                                             '4.363192073.F1'),
                        'i5_index_id': 'iTru5_103_A',
                        'sample_plate': 'Sample_Project_99999_1-4',
                        'index2': 'TGGTCCTT', 'index': 'GCAATTCG',
                        'sample_well': 'F1', 'i7_index_id': 'iTru7_305_11',
                        'raw_reads': '16435', 'quality_filtered_reads': '11',
                        'non_host_reads': '13'},
               '123.000': {'experiment_design_description': 'sample project',
                           'library_construction_protocol': ('Knight Lab Kapa'
                                                             ' HyperPlus'),
                           'platform': 'Illumina', 'run_center': 'KLM',
                           'run_date': '2022-04-18',
                           'run_prefix': '363193755_S7_L001',
                           'sequencing_meth': 'sequencing by synthesis',
                           'center_name': 'UCSD',
                           'center_project_name': 'Sample_Project',
                           'instrument_model': 'Illumina iSeq',
                           'runid': '20220101_FS10001776_07_ABC12345-4567',
                           'lane': '1', 'sample project': 'Sample_Project',
                           'well_description': ('Sample_Project_99999_1-'
                                                '4.363193755.M1'),
                           'i5_index_id': 'iTru5_07_A',
                           'sample_plate': 'Sample_Project_99999_1-4',
                           'index2': 'GGTGTCTT', 'index': 'GATTGCTC',
                           'sample_well': 'M1', 'i7_index_id': 'iTru7_114_03',
                           'raw_reads': '14303',
                           'quality_filtered_reads': '12',
                           'non_host_reads': '14'}}

        self.assertDictEqual(obs, exp)

    def test_generate_special_map(self):
        fake_client = FakeClient()
        step = Step(self.pipeline, self.qiita_id, None)
        step.generate_special_map(fake_client)
        obs = step.special_map

        exp = [('NYU_BMS_Melanoma_13059',
                join(fake_client.base_path, 'uploads/13059'), '13059'),
               ('Feist_11661',
                join(fake_client.base_path, 'uploads/11661'), '11661'),
               ('Gerwick_6123',
                join(fake_client.base_path, 'uploads/6123'), '6123')]

        self.assertEquals(obs, exp)

    def test_get_samples_in_qiita(self):
        fake_client = FakeClient()
        step = Step(self.pipeline, self.qiita_id, None)
        obs_samples, obs_tids = step.get_samples_in_qiita(fake_client, '13059')

        exp_samples = {'EP121011B01', 'EP529635B02', 'EP542578B04',
                       'SP573843A04', 'SP331130A04', 'EP446602B01',
                       'BLANK3.3B', 'AP481403B02', 'LP127829A02',
                       'EP636802A01'}

        exp_tids = {'13059.SP331130A04': ['SP331130A-4'],
                    '13059.AP481403B02': ['AP481403B-2'],
                    '13059.LP127829A02': ['LP127829A-2'],
                    '13059.BLANK3.3B': ['BLANK3.3B'],
                    '13059.EP529635B02': ['EP529635B02'],
                    '13059.EP542578B04': ['EP542578B-4'],
                    '13059.EP446602B01': ['EP446602B-1'],
                    '13059.EP121011B01': ['EP121011B-1'],
                    '13059.EP636802A01': ['EP636802A-1'],
                    '13059.SP573843A04': ['SP573843A-4']}

        self.assertEqual(obs_samples, exp_samples)
        self.assertDictEqual(obs_tids, exp_tids)

    def test_get_tube_ids_from_qiita(self):
        fake_client = FakeClient()
        step = Step(self.pipeline, self.qiita_id, None)
        step.get_tube_ids_from_qiita(fake_client)
        obs = step.tube_id_map

        exp = {'13059': {'SP331130A04': 'SP331130A-4',
                         'AP481403B02': 'AP481403B-2',
                         'LP127829A02': 'LP127829A-2',
                         'BLANK3.3B': 'BLANK3.3B',
                         'EP529635B02': 'EP529635B02',
                         'EP542578B04': 'EP542578B-4',
                         'EP446602B01': 'EP446602B-1',
                         'EP121011B01': 'EP121011B-1',
                         'EP636802A01': 'EP636802A-1',
                         'SP573843A04': 'SP573843A-4'},
               '11661': {'1.24': '1.24', '1.57': '1.57', '1.86': '1.86',
                         '10.17': '10.17', '10.41': '10.41', '10.64': '10.64',
                         '11.18': '11.18', '11.43': '11.43', '11.64': '11.64',
                         '12.15': '12.15'}}

        self.assertDictEqual(obs, exp)
