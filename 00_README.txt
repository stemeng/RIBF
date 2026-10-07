# Replication Package README

## Paper

The Structure and Evolution of Financial Research: Evidence from Embedding-Based Topic Modeling

## Purpose of the replication package

This replication package documents the data retrieval procedure, sample construction, topic-modeling pipeline, and output files used in the paper. The package is designed to provide a lawful reconstruction route for researchers with access to Scopus and to make available the author-written code, model settings, and topic dictionary used in the analysis.

Because the raw article abstracts were retrieved from Scopus and are subject to Elsevier licensing restrictions, the package does not redistribute the raw abstract text. Researchers with institutional access to Scopus can reconstruct the analytical corpus using the retrieval scripts, ISSN list, and documentation provided here.

## Package contents

| File | Description |
|------|-------------|
| 00_README.txt | This file. |
| 01_data_code_availability_statement.txt | Data and code availability statement. |
| 02_download_scopus.py | Scopus retrieval script. |
| 03_journal_issn_list.csv | Journal list and ISSNs. |
| 04_topic_dictionary.csv | Complete inventory of the 226 retained non-outlier topics. |
| 05_topic_model_parameters.txt | Topic-model specification and preprocessing choices. |
| 06_assignment_rates_and_topic_shares.csv | Annual assignment rates and topic shares under assigned-document and all-abstract denominators. |
| 07_assignment_rates_annual.csv | Annual assignment rates. |
| 08_assignment_rates_journal_year.csv | Assignment rates by journal and year. |

## Reconstruction route

Researchers with lawful access to Scopus can reconstruct the analytical corpus as follows:

1. Use `03_journal_issn_list.csv` to identify the journals and ISSNs/EISSNs included in the study.
2. Use `02_download_scopus.py` to retrieve article-level records from Scopus.
3. Apply the sample restrictions described in the paper, including publication years, document filters, duplicate removal procedures, and abstract availability requirements.
4. Generate Sentence-BERT embeddings using the configuration reported in `05_topic_model_parameters.txt`.
5. Estimate the BERTopic model using the documented UMAP, HDBSCAN, and c-TF-IDF settings.
6. Use `04_topic_dictionary.csv` to verify canonical topic IDs, labels, representative keywords, and topic sizes.

## Data restrictions

The raw abstract text is not redistributed because it is subject to Scopus licensing restrictions.

The replication package instead provides:

- retrieval scripts;
- journal and ISSN information;
- topic-model specifications;
- complete topic dictionary;
- documentation of preprocessing and modeling choices.

These materials allow researchers with Scopus access to reconstruct the analytical sample while respecting licensing restrictions on the redistribution of raw Scopus text.

## Topic identifiers and labels

The file `04_topic_dictionary.csv` provides the canonical topic identifiers used throughout the paper. The file reports all 226 retained non-outlier topics together with their labels, representative keywords, and topic sizes.

## Software and model configuration

The complete topic-model specification is documented in `05_topic_model_parameters.txt`, including:

- Sentence-BERT model;
- text preprocessing;
- maximum sequence length and truncation setting;
- UMAP parameters;
- HDBSCAN parameters;
- c-TF-IDF settings;
- topic-labeling procedure.

## Notes on reproducibility

Minor differences may arise if Scopus updates metadata or indexed records after the original retrieval date. The replication materials are intended to document the data collection and modeling procedures used in the study and to facilitate reconstruction by researchers with lawful access to Scopus.