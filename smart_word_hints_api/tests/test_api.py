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
        json={"text": "A very big smile.", "options": {"difficulty": 600}},
    )
    expected_response = {
        "hints": [
            {
                "word": "smile",
                "start_position": 11,
                "end_position": 16,
                "ranking": 676,
                "definition": "a facial expression characterized by turning up the corners of the mouth",  # noqa: E501
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


def test_hints_endpoint__by_default_avoid_repetitions():
    response = client.post(
        "/api/get_hints",
        json={"text": "A tissue. A tissue.", "options": {"difficulty": 1000}},
    )
    assert response.status_code == 200
    assert len(response.json()["hints"]) == 1


def test_hints_endpoint__explicitely_avoid_repetitions():
    response = client.post(
        "/api/get_hints",
        json={
            "text": "A tissue. A tissue.",
            "options": {"difficulty": 1000, "avoid_repetitions": True},
        },
    )
    assert response.status_code == 200
    assert len(response.json()["hints"]) == 1


def test_hints_endpoint__without_avoiding_repetition():
    response = client.post(
        "/api/get_hints",
        json={
            "text": "A tissue. A tissue.",
            "options": {"difficulty": 1000, "avoid_repetitions": False},
        },
    )
    assert response.status_code == 200
    assert len(response.json()["hints"]) == 2
