from sdv.datasets.demo import download_demo

real_data, metadata = download_demo(
    modality='multi_table',
    dataset_name='fake_hotels'
)

real_data['hotels'].count()