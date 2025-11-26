import os
import hmac
import hashlib
from django.http import JsonResponse, HttpResponse, HttpResponseBadRequest, HttpResponseForbidden
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
import json

APP_SECRET = os.environ.get("2948976321969254", "2d84e197603cbb0cc071812939253e21")
TOKEN = os.environ.get("TOKEN", "token")

received_updates = []

def index(request):
    return HttpResponse("<pre>{}</pre>".format(json.dumps(received_updates, indent=2)))

@csrf_exempt
@require_http_methods(["GET", "POST"])
def webhook(request, platform):
    if request.method == "GET":
        mode = request.GET.get("hub.mode")
        verify_token = request.GET.get("hub.verify_token")
        challenge = request.GET.get("hub.challenge")
        if mode == "subscribe" and verify_token == TOKEN:
            return HttpResponse(challenge)
        return HttpResponseBadRequest("Verification failed")

    elif request.method == "POST":
        body_bytes = request.body
        try:
            body_json = json.loads(body_bytes)
        except json.JSONDecodeError:
            return HttpResponseBadRequest("Invalid JSON")

        if platform == "facebook":
            signature = request.headers.get("X-Hub-Signature")
            if not signature:
                print("Warning - X-Hub-Signature missing")
                return HttpResponseForbidden("Unauthorized")

            hash_method, hash_val = signature.split("=")
            expected_hash = hmac.new(APP_SECRET.encode(), body_bytes, hashlib.sha1).hexdigest()
            if not hmac.compare_digest(expected_hash, hash_val):
                print("Warning - X-Hub-Signature invalid")
                return HttpResponseForbidden("Unauthorized")

            print("Facebook request body:", body_json)

        elif platform == "instagram":
            print("Instagram request body:", body_json)

        elif platform == "threads":
            print("Threads request body:", body_json)


        received_updates.insert(0, body_json)
        return HttpResponse(status=200)
