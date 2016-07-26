from operator import itemgetter


def test_get_collection(client):
    response = client.get('/people')
    assert response.status_code == 200
    assert response.json['pagination'] == {
        'count': 3,
        'page': 1,
        'pages': 1,
        'per_page': 20
    }
    sorted_resources = sorted(response.json['resources'], key=itemgetter('id'))
    assert sorted_resources == [
        {'id': 1, 'name': 'Tom', 'dob': '1980-02-26', 'number_of_pets': 0},
        {'id': 2, 'name': 'Dick', 'dob': '1982-03-14', 'number_of_pets': 3},
        {'id': 3, 'name': 'Harry', 'dob': '1972-11-24', 'number_of_pets': 2},
    ]


def test_sorting(client):
    response = client.get('/people?sort=number_of_pets')
    assert response.json['resources'] == [
        {'id': 1, 'name': 'Tom', 'dob': '1980-02-26', 'number_of_pets': 0},
        {'id': 3, 'name': 'Harry', 'dob': '1972-11-24', 'number_of_pets': 2},
        {'id': 2, 'name': 'Dick', 'dob': '1982-03-14', 'number_of_pets': 3},
    ]
    response = client.get('/people?sort=-number_of_pets')
    assert response.json['resources'] == [
        {'id': 2, 'name': 'Dick', 'dob': '1982-03-14', 'number_of_pets': 3},
        {'id': 3, 'name': 'Harry', 'dob': '1972-11-24', 'number_of_pets': 2},
        {'id': 1, 'name': 'Tom', 'dob': '1980-02-26', 'number_of_pets': 0},
    ]


def test_filtering(client):
    response = client.get('/people?name=Dick')
    assert response.status_code == 200
    assert response.json['pagination'] == {
        'count': 1,
        'page': 1,
        'pages': 1,
        'per_page': 20
    }
    assert response.json['resources'][0] == {
        'id': 2, 'name': 'Dick', 'dob': '1982-03-14', 'number_of_pets': 3
    }


def test_filtering_empty_results(client):
    response = client.get('/people?name=Frank')
    assert response.status_code == 200
    assert response.json['pagination'] == {
        'count': 0,
        'page': 1,
        'pages': 0,
        'per_page': 20
    }
    assert response.json['resources'] == []


def test_get_individual(client):
    response = client.get('/people/1')
    assert response.status_code == 200
    assert 'pagination' not in response.json

    assert response.json == {
        'id': 1, 'name': 'Tom', 'dob': '1980-02-26', 'number_of_pets': 0
    }


def test_get_individual_404(client):
    response = client.get('/people/99')
    assert response.status_code == 404


def test_put_not_allowed(client):
    response = client.put('/people/1')
    assert response.status_code == 405


def test_delete_not_allowed(client):
    response = client.delete('/people/1')
    assert response.status_code == 405


def test_post_not_allowed(client):
    response = client.post('/people')
    assert response.status_code == 405


def test_pagination(client):
    response = client.get('/people?per_page=2')
    assert response.status_code == 200
    assert response.json['pagination'] == {
        'count': 3,
        'page': 1,
        'pages': 2,
        'per_page': 2
    }

    response = client.get('/people?page=2&per_page=2')
    assert response.status_code == 200
    assert response.json['pagination'] == {
        'count': 3,
        'page': 2,
        'pages': 2,
        'per_page': 2
    }
