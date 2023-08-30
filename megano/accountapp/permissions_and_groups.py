from django.contrib.auth.models import Group, Permission
from django.contrib.contenttypes.models import ContentType
CODENAME='codename'
NAME='name'
GROUP_SUPERUSER = 'superuser'
GROUP_MODERATOR = 'moderator'
GROUP_SELLER = 'seller'

PRM_VIEW_PAGE = {CODENAME: 'can_view_page', NAME: 'Просмотр страниц'}
PRM_EDIT_CARD_PRODUCT = {CODENAME: 'can_edit_card_product', NAME: 'Создание и изменение карточек товара'}

group_names = {
    GROUP_MODERATOR: [
        PRM_VIEW_PAGE,
    ],
    GROUP_SELLER: [
        PRM_VIEW_PAGE,
    ],
}


def create_groups_and_permissions(apps, schema_editor):
    # Создание группы
    for group_name in group_names:
        group, created = Group.objects.get_or_create(name=group_name)

    # Создание или чтение разрешения и присвоение к группе
        for permission_item in group_names[group_name]:
            permission_item[CODENAME] = permission_item[CODENAME].lower()
            content_type, created2 = ContentType.objects.get_or_create(
                app_label='accountapp',  # Replace with your app's label
                model='accountapp_user'  # Replace with your model's name
            )
            permission, created = Permission.objects.get_or_create(codename=permission_item[CODENAME],
                                                                   name=permission_item[NAME],
                                                                    content_type=content_type)
            group.permissions.add(permission)


def set_group_user(user, group_name):
    """
    Установить пользователю группу
    """
    group = Group.objects.get(name=group_name)
    group.user_set.add(user)