from config import settings


class ComparedProductsService:

    def __init__(self, request):
        """инициализировать список сравнения"""
        self.session = request.session
        compare_list = self.session.get(settings.COMPARE_LIST_SESSION_ID)
        if not compare_list:
            # сохранить пустой список в сеансе
            compare_list = self.session[settings.COMPARE_LIST_SESSION_ID] = []
        self.compare_list = compare_list

    def get_compared_products(self, max_items=3):
        """
        получение списка сравниваемых товаров
        (с возможностью ограничить количество, по умолчанию максимум ― три первых добавленных)
        """
        return self.compare_list[:max_items]

    def add_to_compared_products(self, product):
        """
        добавление товара в список сравниваемых
        """
        if product not in self.compare_list:
            self.compare_list.append(product)
        self.save()

    def remove_from_compared_products(self, product):
        """
        удаление товара из списка сравниваемых
        """
        if product in self.compare_list:
            self.compare_list.remove(product)
        self.save()

    def clear(self):
        """
        очистить список сравниваемых товаров
        """
        self.compare_list.clear()
        self.save()

    def get_count_of_compared_products(self, user_id):
        """
        получение количество товаров в списке сравнения
        """
        return len(self.compare_list)

    def save(self):
        """
        пометить сеанс как "измененный", чтобы обеспечить его сохранение
        """
        self.session.modified = True
