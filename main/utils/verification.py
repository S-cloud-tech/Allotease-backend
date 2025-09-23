import requests

def verify_document_with_third_party(document_path):
    # Mock third-party document verification
    # Replace with actual API call to a document verification provider
    response = requests.post("https://thirdparty.verification.api/verify", files={"document": open(document_path, "rb")})
    return response.status_code == 200

