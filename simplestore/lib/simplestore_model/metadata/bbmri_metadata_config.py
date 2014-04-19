from invenio.sqlalchemyutils import db
import json

domain = 'BBMRI'
# display_name = 'Biobanking and BioMolecular Resources Research Infrastructure'
display_name = 'Biomedical Research'
table_name = 'BBMRI'
image = 'domain-bbmri.png'
kind = 'project'


fields = [
    {
        'name': 'study_id',
        'col_type': db.String(256),
        'display_text': 'Study ID',
        'description': 'The unique ID or acronym for the study',
        'required': False
    },
    {
        'name': 'study_name',
        'col_type': db.String(256),
        'display_text': 'Study name',
        'description': 'The name of the study in English',
        'required': False
    },
    {
        'name': 'study_description',
        'col_type': db.String(256),
        'display_text': 'Study Description',
        'description': 'A description of the study aim',
        'required': False
    },
    {
        'name': 'principal_investigator',
        'col_type': db.String(256),
        'display_text': 'Principal Investigator',
        'description': 'The name of the person responsible for the study or the principal investigator',
        'required': False
    },
    {
        'name': 'study_design',
        'col_type': db.String(256),
        'display_text': 'Study design',
        'data_provide': 'select',
        'cardinality': 'n',
        'description': 'The type of study. Can be one or several of the following values.',
        'data_source': ['Case-control', 'Cohort', 'Cross-sectional', 'Longitudinal',
                        'Twin-study', 'Quality control', 'Population-based', 'Other'],
        'required': False
    },
    {
        'name': 'disease',
        'col_type': db.String(256),
        'display_text': 'Disease',
        'description': 'The disease of main interest in the sample collection, if any. Can be several values MIABIS-38',
        'required': False
    },
    {
        'name': 'categories_of_data_collected',
        'col_type': db.String(256),
        'display_text': 'Categories of data collected',
        'description': 'The type of data collected in the study, and if biological samples are part of the study. '
                       'Can be one or several of the following values: '
                       'Biological samples, Register data, Survey data, '
                       'Physiological measurements, Imaging data, Medical records, Other',
        'data_provide': 'select',
        'cardinality': 'n',
        'data_source': ['Biological samples', 'Register data', 'Survey data',
                        'Physiological measurements', 'Imaging data', 
                        'Medical records', 'Other'],
        'required': False
    },
    {
        'name': 'planned_sampled_individuals',
        'col_type': db.Integer(),
        'display_text': 'Planned sampled individuals',
        'description': 'Number of individuals with biological samples planned for the study',
        'required': False
    },
    {
        'name': 'planned_total_individuals',
        'col_type': db.Integer(),
        'display_text': 'Planned total individuals',
        'description': 'Total number of individuals planned for the study with or without biological samples',
        'required': False
    },
    {
        'name': 'sex',
        'col_type': db.String(256),
        'display_text': 'Sex',
        'description': 'The sex of the study participants. Can be several of the following values: Female, Male, Other',
        'data_provide': 'select',
        'cardinality': 'n',
        'data_source': ['Female', 'Male', 'Other'],
        'required': False
    },
    {
        'name': 'age_interval',
        'col_type': db.String(256),
        'display_text': 'Age interval',
        'description': 'Age interval of youngest to oldest study participant, for example 40-80',
        'required': False
    },
    {
        'name': 'material_type',
        'col_type': db.String(256),
        'display_text': 'Material type',
        'description': 'The nature of the biological samples that are included in the study, if any. '
                       'Can be one or several of the following values: '
                       'Whole blood, Plasma, Serum, Urine, Saliva, CSF, DNA, RNA, Tissue, Faeces, Other',
        'data_provide': 'select',
        'cardinality': 'n',
        'data_source': ['Whole blood', 'Plasma', 'Serum', 'Urine', 'Saliva',
                        'CSF', 'DNA', 'RNA', 'Tissue', 'Faeces', 'Other'],
        'required': False
    },
]
