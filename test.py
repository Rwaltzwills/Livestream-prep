import transcript_preprocessor
import os
import json


def test(func, *args, expected):
    res = func(*args)
    if res != expected:
        print(f"Test failed: {func.__name__} returned {res}, expected {expected}")
        return 0, res
    else:
        print(f"Test passed: {func.__name__}.")
        return 1, res
    
def asserttest(func, *args, expected):
    res = func(*args)
    assert res == expected

    print(f"Test passed: {func.__name__}.")
    return 1

if __name__ == "__main__":
    test_url = os.environ["TEST_URL"]
    # TEST_URL is an env pointing to a playlist with the following two videos:
    # https://www.youtube.com/watch?v=hk9zDlLl7UM
    # https://www.youtube.com/watch?v=9Q61OFFkyKA
    
    test_csv_path = "Test/csv.csv"
    test_zip_path = "Test/zip.zip"
    tp = transcript_preprocessor.Transcript_Preprocessor(test_url, test_zip_path, test_csv_path)

    expected_json = {}
    with open("Test/test_expected.txt", "r") as f:
        expected_json = json.loads(f.read())
    
    test_json = test(tp.download_audio, test_url, expected=expected_json)
    print(type(test_json))

    csv_expected = '''"title","url","upload date"
"I Played 100 Hours of Lord of the Rings Online","https://www.youtube.com/watch?v=hk9zDlLl7UM","20250724"'''
    test(tp.process_json, test_json, test_csv_path, expected=csv_expected)

