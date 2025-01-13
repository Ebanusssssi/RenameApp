import streamlit as st
import zipfile
import os
import tempfile
import shutil

# Функция для распаковки архива
def unpack_archive(archive_path, extract_to):
    """Распаковывает архив в указанную папку."""
    with zipfile.ZipFile(archive_path, 'r') as zip_ref:
        zip_ref.extractall(extract_to)
    st.success(f"Архив распакован в {extract_to}")

# Функция для переименования файлов в папке
def rename_files_in_folder(folder_path):
    """Переименовывает файлы в папке с учётом подкаталогов."""
    for root, dirs, files in os.walk(folder_path):
        # Фильтруем только изображения
        images = [f for f in files if f.lower().endswith(('.jpg', '.jpeg', '.png', '.gif', '.bmp', '.tiff'))]
        
        for idx, image_name in enumerate(sorted(images), start=1):
            # Составляем новый имя файла с сохранением расширения
            file_extension = os.path.splitext(image_name)[1]
            new_name = f"{idx}{file_extension}"
            
            # Путь к текущему файлу
            old_file_path = os.path.join(root, image_name)
            # Путь к новому файлу
            new_file_path = os.path.join(root, new_name)
            
            # Переименовываем
            os.rename(old_file_path, new_file_path)

# Функция для обработки архива
def process_zip(input_zip):
    try:
        # Создаем уникальную временную папку для каждого архива
        temp_folder = tempfile.mkdtemp()

        # Распаковываем архив во временную папку
        unpack_archive(input_zip, temp_folder)

        # Переименовываем файлы
        for root, dirs, files in os.walk(temp_folder):
            if any(f.lower().endswith(('.jpg', '.jpeg', '.png', '.gif', '.bmp', '.tiff')) for f in files):
                rename_files_in_folder(root)

        # Создаем новый архив для обработанных изображений
        output_zip = os.path.join(temp_folder, 'processed_images.zip')

        # Создаем архив с обработанными изображениями
        with zipfile.ZipFile(output_zip, 'w') as zip_ref:
            for root, dirs, files in os.walk(temp_folder):
                for filename in files:
                    file_path = os.path.join(root, filename)
                    if filename.startswith('__MACOSX') or filename.startswith('._'):
                        continue
                    zip_ref.write(file_path, os.path.relpath(file_path, temp_folder))

        return output_zip, temp_folder

    except Exception as e:
        return f"Ошибка при обработке архива: {e}", None
        

# Функция очистки временных файлов
def cleanup(temp_folder, uploaded_zip, output_zip):
    # Очищаем временную папку после обработки
    if os.path.exists(temp_folder):
        shutil.rmtree(temp_folder)
    # Удаляем загруженный архив
    if os.path.exists(uploaded_zip):
        os.remove(uploaded_zip)
    # Удаляем архив после скачивания
    if os.path.exists(output_zip):
        os.remove(output_zip)

# Основная часть программы для Streamlit
def main():
    st.title('Переименование изображений в архиве')
    
    # Загрузка архива
    uploaded_file = st.file_uploader("Загрузите архив с изображениями", type=['zip'])
    
    if uploaded_file is not None:
        # Сохраняем файл
        uploaded_zip = "uploaded.zip"
        with open(uploaded_zip, "wb") as f:
            f.write(uploaded_file.getbuffer())
        
        # Кнопка для запуска обработки
        if st.button('Запустить обработку'):
            st.write("Обработка началась...")

            # Запуск функции для обработки архива
            result, temp_folder = process_zip(uploaded_zip)
            
            if isinstance(result, str) and result.endswith(".zip"):
                st.success("Обработка завершена! Скачайте архив с переименованными изображениями:")
                with open(result, 'rb') as f:
                    download_button = st.download_button('Скачать архив', f, file_name='renamed_images.zip')
                    
                    # Очищаем файлы только после того, как пользователь скачает архив
                    if download_button:
                        cleanup(temp_folder, uploaded_zip, result)
            else:
                st.error(result)

if __name__ == "__main__":
    main()
