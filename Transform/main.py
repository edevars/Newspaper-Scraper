import pandas as pd
from urllib.parse import urlparse
import argparse
import logging
import hashlib
import nltk

from nltk.corpus import stopwords

stop_words = set(stopwords.words('spanish'))

logging.basicConfig(level=logging.INFO)

logger = logging.getLogger(__name__)


def main(filename):
    logger.info('Starting cleaning process')

    df = _read_data(filename)
    newspaper_uid = _extract_newspaper_uid(filename)
    df = _add_newspaper_uid_column(df, newspaper_uid)
    df = _extract_host(df)
    df = _fill_missing_titles(df)
    df = _generate_uid_for_rows(df)
    df = _remove_new_lines_from_body(df)
    df = _tokenize_column(df, 'title')
    df = _tokenize_column(df, 'body')
    df = _removing_duplicated_entries(df, 'title')
    df = _drop_rows_with_missing_data(df)
    _save_data(df, filename)
    return df


def _read_data(filename):
    logger.info(f'Reading file {filename}')

    return pd.read_csv(filename)


def _extract_newspaper_uid(filename):
    logger.info('Extracting newspaper uid')
    newspaper_uid = filename.split('_')[0]

    logger.info(f'Newspaper uid detected: {newspaper_uid}')
    return newspaper_uid


def _add_newspaper_uid_column(df, newspaper_uid):
    logger.info(f'Filling newspaper_uid column with {newspaper_uid}')
    df['newspaper_uid'] = newspaper_uid

    return df


def _extract_host(df):
    logger.info('Extracting the host for each url')
    df['host'] = df['url'].apply(lambda url: urlparse(url).netloc)
    return df


def _fill_missing_titles(df):
    logger.info('Filling missing titles')
    missing_titles_mask = df['title'].isna()

    missing_titles = (df[missing_titles_mask]['url']
                      .str.extract(r'(?P<missing_titles>[^/]+)$')
                      .applymap(lambda title: title.split('-'))
                      .applymap(lambda title_word_list: ' '.join(title_word_list))
                      )

    df.loc[missing_titles_mask, 'title'] = missing_titles.loc[:, 'missing_titles']
    return df


def _generate_uid_for_rows(df):
    logger.info('Genereating uids')
    uids = (df
            .apply(lambda row: hashlib.md5(bytes(row['url'].encode())), axis=1)
            .apply(lambda hash_object: hash_object.hexdigest())
            )

    df['uid'] = uids

    df.set_index('uid', inplace=True)

    return df


def _remove_new_lines_from_body(df):
    logger.info('Removing new lines from body')
    stripped_body = (df
                     .apply(lambda row: row['body'], axis=1)
                     .apply(lambda body: list(body))
                     .apply(lambda letters: list(map(lambda letter: letter.replace('\n', ' '), letters)))
                     .apply(lambda letters: ''.join(letters))
                     )

    df['body'] = stripped_body

    return df


def _tokenize_column(df, column_name):
    logger.info(f'Tokenizing column {column_name}')
    df[f'n_tokens_{column_name}'] = (df
                                     .dropna()
                                     .apply(lambda row: nltk.word_tokenize(row[column_name]), axis=1)
                                     .apply(lambda tokens: list(filter(lambda token: token.isalpha(), tokens)))
                                     .apply(lambda tokens: list(map(lambda token: token.lower, tokens)))
                                     .apply(lambda word_list: list(filter(lambda word: word not in stop_words, word_list)))
                                     .apply(lambda valid_word_list: len(valid_word_list))
                                     )
    return df


def _removing_duplicated_entries(df, column_name):
    logger.info('Removing duplicated entrie')
    df.drop_duplicates(subset='title', keep='first', inplace=True)

    return df


def _drop_rows_with_missing_data(df):
    logger.info('Removing entries without data')
    return df.dropna()


def _save_data(df, filename):
    clean_filename = f'clean_{filename}'
    logger.info(f'Saving data at: {clean_filename}')
    df.to_csv(clean_filename)


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('filename',
                        help="The path to the dirty data",
                        type=str)

    arg = parser.parse_args()

    df = main(arg.filename)
    print(df)
