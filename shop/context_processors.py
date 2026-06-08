from .models import Category

def categories(request):
    categories = Category.objects.filter(is_active=True)
    return {'all_categories': categories}