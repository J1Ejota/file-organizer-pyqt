#!/usr/bin/env python3

import os
import sys
import shutil
import logging
from typing import Dict, List
from mimetypes import guess_type
from datetime import datetime
import json

# Configuración de logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Archivos excluidos
EXCLUIDOS = ['Thumbs.db', 'desktop.ini', '.DS_Store']
EXTENSIONES_EXCLUIDAS = ['.lnk', '.ini', '.sys', '.dll', '.bat', '.cmd', '.reg']

def file_types(include_executables: bool) -> Dict[str, List[str]]:
    tipos = {
        'Documentos': ['.pdf', '.docx', '.txt', '.xlsx', '.pptx'],
        'Imágenes': ['.jpg', '.jpeg', '.png', '.gif'],
        'Vídeos': ['.mp4', '.avi', '.mov'],
        'Audio': ['.mp3', '.wav'],
        'Archivos comprimidos': ['.zip', '.rar'],
        'Otros': []
    }
    if include_executables:
        tipos['Ejecutables'] = ['.exe', '.msi']
    return tipos

def obtener_fecha_formateada(file_path: str) -> str:
    timestamp = os.path.getmtime(file_path)
    fecha = datetime.fromtimestamp(timestamp)
    return fecha.strftime("%d-%m-%Y")

def create_subdirectory(base_path: str, subdirectory: str) -> str:
    path = os.path.join(base_path, subdirectory)
    if not os.path.exists(path):
        os.makedirs(path)
        logger.info(f'Subdirectorio creado: {path}')
    return path

def move_file(file_path: str, destination: str) -> str:
    filename = os.path.basename(file_path)
    destination_path = os.path.join(destination, filename)

    if os.path.exists(destination_path):
        base, ext = os.path.splitext(filename)
        counter = 1
        while os.path.exists(destination_path):
            destination_path = os.path.join(destination, f"{base}_{counter}{ext}")
            counter += 1

    shutil.move(file_path, destination_path)
    logger.info(f'Archivo movido: {file_path} → {destination_path}')
    return destination_path

def organize_directory(
    directory: str,
    include_executables: bool = False,
    preview: bool = False,
    categorias_permitidas: List[str] = None
) -> Dict[str, Dict[str, List[str]]]:
    """
    Organiza archivos del directorio en subcarpetas según su tipo.
    Si preview==False, mueve los archivos y guarda el historial de movimientos en
    un fichero JSON (.organizer_historial.json) en el mismo directorio.
    Devuelve un diccionario resumen con la cantidad y lista de archivos movidos por cada categoría.
    """
    if not os.path.isdir(directory):
        logger.error(f'El directorio no existe: {directory}')
        raise FileNotFoundError(f'No se encontró el directorio: {directory}')

    directory = os.path.abspath(directory)
    files = [f for f in os.listdir(directory) if os.path.isfile(os.path.join(directory, f))]
    resumen: Dict[str, Dict[str, List[str]]] = {}
    movimientos = {}  # Para registrar los movimientos: { archivo_original: ruta_nueva }

    if categorias_permitidas is None:
        categorias_permitidas = list(file_types(include_executables).keys())

    for file in files:
        file_path = os.path.join(directory, file)

        # Excluir archivos
        if file in EXCLUIDOS or any(file.lower().endswith(ext) for ext in EXTENSIONES_EXCLUIDAS):
            logger.info(f'Archivo excluido: {file}')
            continue

        moved = False

        for folder, extensions in file_types(include_executables).items():
            if folder not in categorias_permitidas:
                continue

            if any(file.lower().endswith(ext) for ext in extensions):
                if folder in ['Imágenes', 'Vídeos']:
                    fecha = obtener_fecha_formateada(file_path)
                    fecha_subdir = os.path.join(directory, folder, fecha)
                    if not preview:
                        os.makedirs(fecha_subdir, exist_ok=True)
                        destination_path = move_file(file_path, fecha_subdir)
                        movimientos[file_path] = destination_path
                else:
                    if not preview:
                        subdirectory = create_subdirectory(directory, folder)
                        destination_path = move_file(file_path, subdirectory)
                        movimientos[file_path] = destination_path

                resumen.setdefault(folder, {"cuenta": 0, "archivos": []})
                resumen[folder]["cuenta"] += 1
                resumen[folder]["archivos"].append(file)
                moved = True
                break

        if not moved:
            if not preview:
                other_subdir = create_subdirectory(directory, 'Otros')
                destination_path = move_file(file_path, other_subdir)
                movimientos[file_path] = destination_path

            resumen.setdefault('Otros', {"cuenta": 0, "archivos": []})
            resumen['Otros']["cuenta"] += 1
            resumen['Otros']["archivos"].append(file)

    if not preview:
        historial_path = os.path.join(directory, ".organizer_historial.json")
        with open(historial_path, "w", encoding="utf-8") as f:
            json.dump(movimientos, f, ensure_ascii=False, indent=4)

    return resumen

HISTORIAL_JSON = ".organizer_historial.json"

def deshacer_ultimo_ordenamiento(directory: str) -> bool:
    """
    Lee el historial de movimientos (fichero .organizer_historial.json) y
    mueve cada archivo de su ubicación actual de vuelta a su ubicación original.
    Luego elimina el fichero de historial. Devuelve True si se deshizo correctamente.
    """
    historial_path = os.path.join(directory, HISTORIAL_JSON)

    if not os.path.exists(historial_path):
        return False

    try:
        with open(historial_path, "r", encoding="utf-8") as f:
            historial = json.load(f)

        # historial: { original_path: destination_path }
        for original_path, destino_path in historial.items():
            if os.path.exists(destino_path):
                os.makedirs(os.path.dirname(original_path), exist_ok=True)
                shutil.move(destino_path, original_path)

        os.remove(historial_path)
        return True
    except Exception as e:
        logger.error(f"Error al deshacer el ordenamiento: {e}")
        return False

__all__ = ["organize_directory", "deshacer_ultimo_ordenamiento"]