from services.dnk_media.src.service import process_data

def test_process_data():
    assert process_data("hello") == "Processed: hello"
