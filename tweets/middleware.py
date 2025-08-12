import logging
from django.http import HttpResponseBadRequest
from django.contrib import messages
from django.shortcuts import redirect
from django.urls import reverse

logger = logging.getLogger(__name__)


class FileSizeMiddleware:
    """
    Middleware для перевірки розміру завантажуваних файлів
    """

    def __init__(self, get_response):
        self.get_response = get_response
        self.max_file_size = 5 * 1024 * 1024  # 5MB

    def __call__(self, request):
        # Перевіряємо розмір запиту тільки для POST запитів з файлами
        if (
            request.method == "POST"
            and request.content_type
            and "multipart/form-data" in request.content_type
        ):
            content_length = request.META.get("CONTENT_LENGTH", 0)

            if content_length and int(content_length) > self.max_file_size:
                logger.warning(
                    f"Request too large: {content_length} bytes from {request.META.get('REMOTE_ADDR', 'unknown')}"
                )

                # Додаємо повідомлення про помилку
                messages.error(
                    request,
                    "File too large! Maximum file size is 5MB. Please try uploading a smaller file.",
                )

                # Перенаправляємо користувача назад
                if "tweets" in request.path:
                    if "reply" in request.path:
                        # Для відповідей
                        tweet_id = request.path.split("/")[-2]  # Отримуємо ID твіту
                        return redirect("tweets:tweet_detail", pk=tweet_id)
                    elif "update" in request.path:
                        # Для оновлення
                        tweet_id = request.path.split("/")[-2]
                        return redirect("tweets:tweet_detail", pk=tweet_id)
                    else:
                        # Для створення нових твітів
                        return redirect("tweets:tweet_list")

                # Якщо не можемо визначити, куди перенаправити, повертаємо помилку
                return HttpResponseBadRequest(
                    "File too large! Maximum file size is 5MB."
                )

        response = self.get_response(request)
        return response
