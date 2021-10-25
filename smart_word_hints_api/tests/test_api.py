from fastapi.testclient import TestClient

from smart_word_hints_api.app.main import app

client = TestClient(app)


def test_only_english_to_english_is_returned_as_supported():
    response = client.get("/api/available_languages")
    assert response.status_code == 200
    assert response.json() == [["english", "english"]]


def test_hints_endpoint__simple_sentence():
    response = client.post(
        "/api/get_hints",
        json={"text": "A very big pie.", "options": {"difficulty": 1000}},
    )
    expected_response = {
        "hints": [
            {
                "word": "pie",
                "start_position": 11,
                "end_position": 14,
                "ranking": 4524,
                "definition": "dish baked in pastry-lined pan often with a pastry top",
                "part_of_speech": "NN",
            }
        ]
    }
    assert response.status_code == 200
    assert response.json() == expected_response


def test_hints_endpoint__gibberish_returns_empty_list_of_hints():
    response = client.post(
        "/api/get_hints",
        json={"text": "Ajod fhis tuy benght ratingo.", "options": {"difficulty": 1000}},
    )
    assert response.status_code == 200
    assert response.json() == {"hints": []}
