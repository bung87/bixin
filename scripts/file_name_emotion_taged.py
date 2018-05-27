# https://github.com/godbmw/various-codes/tree/master/DictEmotionAlgorithm
# https://github.com/AimeeLee77/senti_analysis/tree/master/data/ChnSentiCorp_htl_ba_2000
# https://github.com/godbmw/news-emotion/tree/master/data/trainset
import os
import io
DIR = os.path.join(os.path.dirname(__file__), "../unprepared_test_data")


def get_files(input_dir):
    files = []
    for (dirpath, dirnames, filenames) in os.walk(input_dir):
        files.extend([os.path.join(dirpath, x)
                      for x in filenames if x.endswith(".txt")])
    return files


def predict_encoding(file_path, n_lines=20):
    '''Predict a file's encoding using chardet'''
    import chardet

    # Open the file as binary data
    with open(file_path, 'rb') as f:
        # Join binary lines for specified number of lines
        rawdata = b''.join([f.readline() for _ in range(n_lines)])

    return chardet.detect(rawdata)['encoding']


def loop_files(input_dir, output):
    files = get_files(input_dir)
    with open(output, "w") as output:
        for file in files:

            encoding = predict_encoding(file)
            print(file, encoding)
            basename = os.path.basename(file)
            mark = ""
            if basename.startswith("neg"):
                mark = "n"
            elif basename.startswith("pos"):
                mark = "p"
            else:
                continue
            if not encoding:
                encoding = "gb2312"
            try:
                with io.open(file, encoding=encoding) as f:
                    content = f.read().strip().replace("\n", "")
                    output.write(content + "\t" + mark+"\n")
            except Exception:
                continue


input_dir = os.path.join(DIR, "DictEmotionAlgorithm")
output = os.path.join(DIR, "../test_data/DictEmotionAlgorithm.txt")

loop_files(input_dir, output)


input_dir = os.path.join(DIR, "ChnSentiCorp_htl_ba_2000")
output = os.path.join(DIR, "../test_data/ChnSentiCorp_htl_ba_2000.txt")

loop_files(input_dir, output)


input_dir = os.path.join(DIR, "trainset")
output = os.path.join(DIR, "../test_data/trainset.txt")

loop_files(input_dir, output)
