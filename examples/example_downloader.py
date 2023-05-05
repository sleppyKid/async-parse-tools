from async_parse_tools import AsyncDownloader

if __name__ == '__main__':
    images_num = 20
    urls_list = ['https://loremflickr.com/320/240'] * (images_num - 10)
    # bad strings
    urls_list.extend(['kpkpk', 'sdad', 'asdascc', 'zxcae2ed', 'asdczx', 'ads1', '12345'])
    # bad urls
    urls_list.extend(
        ['https://loremflickr.com/asdaczxczcz', 'https://loremflickr.com/2312dasd', 'https://loremflickr.com/lol'])
    names = [str(x) + '.jpg' for x in range(images_num)]

    _, e = (
        AsyncDownloader(connections_limit=20, allow_redirects=True)
        .error_settings(max_tries=2, return_errors=True)
        .set_filenames(names)
        .set_download_folder('./download')
        .set_check_folder('./download2', any_extension=True)
        # .set_headers({})
        # .add_headers({})
        # .set_user_agent('')
        .run(urls=urls_list)
    )

    print(e)
