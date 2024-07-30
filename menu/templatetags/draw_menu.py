from django import template
from django.utils.datastructures import MultiValueDictKeyError

from menu.models import MenuItem


register = template.Library()


@register.inclusion_tag('menu/draw_menu.html', takes_context=True)# параметр указывает что мы принимаем контекст шаблона)
def draw_menu(context, menu):
    """
    Формирует контекстный словарь для передачи в шаблон 'draw_menu.html'.

     - Если пользователь активирует какой-либо пункт меню, то в словарь
    включается вся ветка дочерних пунктов.
    """
    items = MenuItem.objects.filter(menu__title=menu) # получаем элементы меню, единственный запрос к БД
    item_values = items.values()
    super_parents = [item for item in item_values.filter(parent=None)] # Находим самый первый айтем менюшки

    try:
        selected_item = items.get(id=context['request'].GET[menu]) # Получаем запрашиваемый айтем, иначе обрабатываем ошибку
        expanded_items_id_list = get_expanded_items_id_list(selected_item)  # получаем id всех развёрнутых меню
        for parent in super_parents:
            if parent['id'] in expanded_items_id_list: # Если id родительского элемента есть в списке
                parent['child_items'] = get_child_items( # Получаем дочерние элементы и записываем в словарь
                    item_values, parent['id'], expanded_items_id_list
                )
        result_dict = {'items': super_parents}  # формируем словарь, который будет передан в шаблон
    except MultiValueDictKeyError: # Если не передаётся элементов (пустой url без параметров)
        result_dict = {'items': super_parents}

    result_dict['menu'] = menu # Добавляем название меню в словарь
    return result_dict


def get_expanded_items_id_list(parent):
    """
    Формирует список id всех развернутых пунктов меню.
    """
    expanded_items_id_list = []
    while parent:
        expanded_items_id_list.append(parent.id) # добавляем id родительского элемента в список
        parent = parent.parent # переходим к родительскому элементу, если его нет вернёт None и выйдет из цикла
    return expanded_items_id_list


def get_child_items(item_values, current_parent_id, expanded_items_id_list):
    """
    Для переданного в аргументе текущего родителя рекурсивно
    формирует список дочерних элементов.
    """
    current_parent_child_list = [   # создаём список дочерних элементов текущего родителя
        item for item in item_values.filter(parent_id=current_parent_id)
    ]
    for child in current_parent_child_list:
        if child['id'] in expanded_items_id_list: # Проверка есть ли id дочернего элемента в списке развернутых элементов
            child['child_items'] = get_child_items( # Если да, рекурсивно находим его дочерние элементы и записываем как child_items
                item_values, child['id'], expanded_items_id_list
            )
    return current_parent_child_list
