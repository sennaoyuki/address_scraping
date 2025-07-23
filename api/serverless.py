"""
Vercel Serverless Function エントリーポイント
"""
from index import app

# Vercelのハンドラーとして公開
def handler(request, context):
    with app.test_request_context(
        path=request.path,
        method=request.method,
        headers=request.headers,
        data=request.body
    ):
        response = app.full_dispatch_request()
        return {
            'statusCode': response.status_code,
            'headers': dict(response.headers),
            'body': response.get_data(as_text=True)
        }