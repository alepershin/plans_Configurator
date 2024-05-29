import random
import streamlit as st
import matplotlib.pyplot as plt
import json
import os
import math

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
    y_coordinates = y_coordinates = [vertex.get('y', 0) for vertex in vertices]

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

def add_sections(section1, section2):
    # Найти угол между векторами внутренних стен и повернуть на него вторую секцию


def choise_section(suitable_sections):
    section = random.choice(suitable_sections)
    if wall_count(section) == 0:
        return section
    else:
        new_section = rand_section_by_wall(section['interior_walls'][0])
        if new_section == None:
            return None
        else:
            section = add_sections(section, new_section)

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
        section = choise_section(suitable_sections)

    else:
        # Обрабатываем ситуацию, когда нет подходящих секций
        st.write("Нет секций, удовлетворяющих заданным размерам.")
