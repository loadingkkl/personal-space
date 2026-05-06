class PublicFrameOptionsMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        response = self.get_response(request)

        if request.path.startswith('/admin/'):
            response['X-Frame-Options'] = 'DENY'
            return response

        if 'X-Frame-Options' in response:
            del response['X-Frame-Options']
        response['Content-Security-Policy'] = (
            "frame-ancestors 'self' https://vercel.com https://*.vercel.com"
        )
        return response
