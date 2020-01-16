import subprocess
import logging
logging.basicConfig(level=logging.INFO)

logger = logging.getLogger(__name__)

news_sites_uids = ['eluniversal', 'elpais']


def main():
    _extract()
    _transform()
    _load()


def _extract():
    logger.info('Starting extract process')
    for news_sites_uid in news_sites_uids:
        subprocess.run(['python', 'main.py', news_sites_uid], cwd='./Extract')
        subprocess.run(['find', '.', '-name', f'{news_sites_uid}*',
                        '-exec', 'mv', '{}', f'../Transform/{news_sites_uid}_.csv',
                        ';'], cwd='./Extract')


def _transform():
    logger.info('Starting transform process')
    for news_sites_uid in news_sites_uids:
        dirty_data_filename = f'{news_sites_uid}_.csv'
        clean_data_filename = f'clean_{dirty_data_filename}'
        subprocess.run(
            ['python', 'main.py', dirty_data_filename], cwd='./Transform')
        subprocess.run(['rm', dirty_data_filename], cwd='./Transform')
        subprocess.run(['mv', clean_data_filename,
                        f'../Load/{news_sites_uid}.csv'], cwd='./Transform')


def _load():
    logger.info('Starting load process')
    for news_sites_uid in news_sites_uids:
        clean_data_filename = f'{news_sites_uid}.csv'
        subprocess.run(
            ['python', 'main.py', clean_data_filename], cwd='./Load')
        subprocess.run(['rm', clean_data_filename], cwd='./Load')

if __name__ == '__main__':
    main()