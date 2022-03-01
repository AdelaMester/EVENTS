from application import app
'''
def test_index(self):
    assert True

def test_index_2(client):
    response=client.get("/", content_type="html/text")
    assert response.status_code == 200
'''

def test_index():
    response = app.test_client().get('/')
    assert response.status_code == 200
    assert response.data == b"Welcome to our Event Ticket Management page! "
