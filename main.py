import random
import streamlit as st
import matplotlib.pyplot as plt
import json
import os
import math
import numpy as np

st.header('Размеры пятна застройки')

# Виджеты для ввода длины и ширины участка с использованием сохраненных значений
# Формат '%.2f' обеспечивает вывод с точностью до двух знаков после запятой
length = st.number_input('Длина (м):', min_value=0.0, format='%.2f', value=77.0, step=0.1)
width = st.number_input('Ширина (м):', min_value=0.0, format='%.2f', value=61.0, step=0.1)

tolerance = st.number_input('Допустимая погрешность стыковки стен (м):', min_value=0.0, format='%.2f', value=0.50, step=0.01)

# Устанавливаем ключи для различения виджетов ввода
keys = ['one', 'two', 'three', 'studio']

st.header('Целевое распределение')

# Функция-обработчик изменения значений, которая обновляет поля ввода
def on_change():
    total = 100.0
    # Вычисляем сумму всех полей кроме последнего
    current_total = sum(st.session_state[key] for key in keys[:-1])
    # Обновляем последнее поле значением оставшегося процента
    st.session_state[keys[-1]] = total - current_total

def will_fit(vertices, length, width):
    # Вычисление координат ограничивающего прямоугольника
    x_coordinates = [vertex['x'] for vertex in vertices]
    y_coordinates = [vertex['y'] for vertex in vertices]

    min_x = min(x_coordinates)
    max_x = max(x_coordinates)
    min_y = min(y_coordinates)
    max_y = max(y_coordinates)

    # Вычисление ширины и длины ограничивающего прямоугольника
    bounding_box_length = max_x - min_x
    bounding_box_width = max_y - min_y

    # Сравнение размеров ограничивающего прямоугольника с заданными размерами
    if (bounding_box_length <= length and bounding_box_width <= width) or (bounding_box_length <= width and bounding_box_width <= length):
        return True
    else:
        return False

# Сгруппируем виджеты в строку
cols = st.columns(4)  # Создаем 4 колонки

with cols[0]:
    st.number_input('Однокомнатные (%)', min_value=0.0, max_value=100.0, key=keys[0], value=52.0, step=0.1, on_change=on_change)
with cols[1]:
    st.number_input('Двухкомнатные (%)', min_value=0.0, max_value=100.0, key=keys[1], value=32.0, step=0.1, on_change=on_change)
with cols[2]:
    st.number_input('Трехкомнатные (%)', min_value=0.0, max_value=100.0, key=keys[2], value=4.0, step=0.1, on_change=on_change)
with cols[3]:
    st.number_input('Студии (%)', min_value=0.0, max_value=100.0, key=keys[3], value=12.0, step=0.1)

# Путь к файлу sections.json
file_path = "sections.json"

# Проверьте, существует ли файл
if os.path.exists(file_path):
    with open(file_path, 'r', encoding='utf-8') as f:
        # Преобразуйте содержимое файла в массив
        data = json.load(f)

def wall_count(section):
    return len(section['interior_walls'])


# Отбор секций с внутренними стенами заданной длины
def filter_sections_by_wall_length(sections, target_length, tolerance):
    # Массив для секций, которые удовлетворяют условиям
    filtered_sections = []

    # Проверка каждой секции
    for section in sections:
        has_wall_of_target_length = False

        # Проверка каждой внутренней стены внутри секции
        for wall in section['interior_walls']:
            length = wall_length(wall)
            # Сравниваем длину стены с заданной длиной с учетом погрешности
            if abs(length - target_length) <= tolerance:
                has_wall_of_target_length = True
                break  # Переходим к следующей секции, если условие удовлетворено

        # Если секция содержит стену заданной длины, добавляем ее в массив
        if has_wall_of_target_length:
            filtered_sections.append(section)

    return filtered_sections

# Функция, которая вычисляет длину стены
def wall_length(wall):
    return math.sqrt((wall['x2'] - wall['x1'])**2 + (wall['y2'] - wall['y1'])**2)

def rand_section_by_wall(wall):
    filtered = filter_sections_by_wall_length(sections, wall_length(wall), tolerance)
    if len(filtered) == 0:
        return None
    else:
        return random.choice(filtered)

# Функция для вычисления скалярного произведения двух векторов
def dot_product(vector_a, vector_b):
    return sum(a * b for a, b in zip(vector_a, vector_b))

# Функция для вычисления длины вектора
def magnitude(vector):
    return math.sqrt(dot_product(vector, vector))

# Функция для нахождения угла между двумя векторами
def angle_between_vectors_clockwise(vector_a, vector_b):
    unit_vector_a = vector_a / np.linalg.norm(vector_a)
    unit_vector_b = vector_b / np.linalg.norm(vector_b)
    dot_product = np.dot(unit_vector_a, unit_vector_b)
    angle_radians = np.arccos(dot_product)

    # Определяем направление поворота (по часовой или против)
    # используя перекрестное произведение
    direction = np.cross(unit_vector_a, unit_vector_b)

    # Если результат перекрестного произведения положительный, поворот идет по часовой стрелке
    if direction > 0:
        rotation_angle_degrees = np.degrees(angle_radians)
    else:
        rotation_angle_degrees = 360 - np.degrees(angle_radians)

    return rotation_angle_degrees
def rotate_point(x, y, angle_degrees, origin=(0, 0)):
    angle_radians = math.radians(angle_degrees)
    # Сдвигаем точку так, чтобы центр вращения был в начале координат
    x -= origin[0]
    y -= origin[1]
    # Применяем матрицу поворота
    x_new = x * math.cos(angle_radians) + y * math.sin(angle_radians)
    y_new = -x * math.sin(angle_radians) + y * math.cos(angle_radians)
    # Сдвигаем обратно
    x_new += origin[0]
    y_new += origin[1]
    return x_new, y_new

def rotate_section(vertices, interior_walls, angle_degrees):
    # Находим центр секции
    center_x = sum(vertex['x'] for vertex in vertices) / len(vertices)
    center_y = sum(vertex['y'] for vertex in vertices) / len(vertices)
    origin = (center_x, center_y)

    # Поворачиваем вершины
    new_vertices = [
        {'x': rotate_point(vertex['x'], vertex['y'], angle_degrees, origin)[0],
         'y': rotate_point(vertex['x'], vertex['y'], angle_degrees, origin)[1]}
        for vertex in vertices
    ]

    # Поворачиваем внутренние стены
    new_interior_walls = [
        {'x1': rotate_point(wall['x1'], wall['y1'], angle_degrees, origin)[0],
         'y1': rotate_point(wall['x1'], wall['y1'], angle_degrees, origin)[1],
         'x2': rotate_point(wall['x2'], wall['y2'], angle_degrees, origin)[0],
         'y2': rotate_point(wall['x2'], wall['y2'], angle_degrees, origin)[1]}
        for wall in interior_walls
    ]

    return new_vertices, new_interior_walls

def move_section(vertices, interior_walls, vector):
    dx, dy = vector  # Разбиваем вектор перемещения на компоненты x и y

    # Перемещаем вершины
    new_vertices = [
        {'x': vertex['x'] + dx, 'y': vertex['y'] + dy}
        for vertex in vertices
    ]

    # Перемещаем внутренние стены
    new_interior_walls = [
        {'x1': wall['x1'] + dx, 'y1': wall['y1'] + dy,
         'x2': wall['x2'] + dx, 'y2': wall['y2'] + dy}
        for wall in interior_walls
    ]

    return new_vertices, new_interior_walls


def combine_sections(section1, section2):
    # Нахождение крайних точек для новой секции
    min_x = min(min(vertex['x'] for vertex in section1['vertices']),
                min(vertex['x'] for vertex in section2['vertices']))
    max_x = max(max(vertex['x'] for vertex in section1['vertices']),
                max(vertex['x'] for vertex in section2['vertices']))
    min_y = min(min(vertex['y'] for vertex in section1['vertices']),
                min(vertex['y'] for vertex in section2['vertices']))
    max_y = max(max(vertex['y'] for vertex in section1['vertices']),
                max(vertex['y'] for vertex in section2['vertices']))

    # Создание новых вершин по обнаруженным крайним точкам
    new_vertices = [
        {'x': min_x, 'y': min_y},
        {'x': max_x, 'y': min_y},
        {'x': max_x, 'y': max_y},
        {'x': min_x, 'y': max_y}
    ]

    # Объединение внутренних стен двух секций
    new_interior_walls = section1['interior_walls'] + section2['interior_walls']

    # Создание и возврат новой секции
    new_section = {
        'building': section1['building'] + " c: " + str(section1['number']) + " " + section2['building'] + " c: " + str(section2['number']),
        'number': 0,
        'vertices': new_vertices,
        'interior_walls': new_interior_walls
    }
    return new_section

def add_sections(section1, section2):
    wall1 = section1['interior_walls'][0]
    AB = [wall1['x2'] - wall1['x1'], wall1['y2'] - wall1['y1']]
    wall2 = section2['interior_walls'][0]
    CD = [wall2['x2'] - wall2['x1'], wall2['y2'] - wall2['y1']]
    angle = angle_between_vectors_clockwise(AB, CD)

    new_vertices, new_interior_walls = rotate_section(section2['vertices'], section2['interior_walls'], 180 - angle)
    move_vector = [wall1['x2'] - new_interior_walls[0]['x1'],  wall1['y2'] - new_interior_walls[0]['y1']]
    new_vertices, new_interior_walls = move_section(new_vertices, new_interior_walls, move_vector)

    section2['vertices'] = new_vertices
    section2['interior_walls'] = new_interior_walls

    return section2

# Функция для отрисовки полигона по заданным вершинам
def draw_polygon(section, length, width):

    s = section['building']
    if section['number'] > 0:
        s = s + " Секция: " + str(section['number'])
    st.header(s)

    # Преобразование каждого элемента массива в кортеж
    vertices = [tuple(vertex.values()) for vertex in section['vertices']]

    fig, ax = plt.subplots()
    polygon = plt.Polygon(vertices, closed=True, fill=False, linewidth=2)
    ax.add_patch(polygon)

    for wall in section['interior_walls']:
        x1, y1, x2, y2 = wall['x1'], wall['y1'], wall['x2'], wall['y2']
        ax.plot([x1, x2], [y1, y2], color='red', linewidth=2)

    # Настраиваем пределы осей согласно размерам участка
    ax.set_xlim([0, length])
    ax.set_ylim([0, width])

    # Устанавливаем одинаковый масштаб для обеих осей
    ax.set_aspect('equal')

    # Дополнительная настройка графика
    plt.tight_layout()
    plt.close()
    return fig

def move_section_to_origin(section):

    vertices = section['vertices']
    interior_walls = section['interior_walls']

    # Находим минимальные x и y среди всех вершин
    min_x = min(vertex['x'] for vertex in vertices)
    min_y = min(vertex['y'] for vertex in vertices)

    # Сдвиг всех вершин
    new_vertices = [
        {'x': vertex['x'] - min_x, 'y': vertex['y'] - min_y}
        for vertex in vertices
    ]

    # Находим максимальные x и y среди всех вершин
    max_x = max(vertex['x'] for vertex in new_vertices)
    max_y = max(vertex['y'] for vertex in new_vertices)


    # Сдвиг всех внутренних стен
    new_interior_walls = [
        {'x1': wall['x1'] - min_x, 'y1': wall['y1'] - min_y,
         'x2': wall['x2'] - min_x, 'y2': wall['y2'] - min_y}
        for wall in interior_walls
    ]

    section['vertices']  = new_vertices
    section['interior_walls']  = new_interior_walls

    return section

if st.button('Запустить поиск планировок'):
    one_bedroom_percentage = st.session_state['one']
    two_bedroom_percentage = st.session_state['two']
    three_bedroom_percentage = st.session_state['three']
    studio_percentage = st.session_state['studio']

    sections = data['sections']

    # Фильтруем секции, чтобы найти только те, которые подходят по размеру
    suitable_sections = [section for section in sections if will_fit(section['vertices'], length, width)]

    # Если есть хотя бы одна подходящая секция, выбираем из них случайную
    if suitable_sections:
        section = random.choice(suitable_sections)
        if wall_count(section) == 0:
            image = draw_polygon(section, length, width)
            st.pyplot(image)
        else:
            new_section = rand_section_by_wall(section['interior_walls'][0])
            image = draw_polygon(section, length, width)
            st.pyplot(image)
            add_section = add_sections(section, new_section)
            image = draw_polygon(add_section, length, width)
            st.pyplot(image)
            merging = combine_sections(section, add_section)
            rez = move_section_to_origin(merging)
            image = draw_polygon(rez, length, width)

            st.pyplot(image)

    else:
        # Обрабатываем ситуацию, когда нет подходящих секций
        st.write("Нет секций, удовлетворяющих заданным размерам.")
