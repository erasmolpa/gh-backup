import unittest
import os
import tempfile
import shutil

from github_tool.gh_repo_restore.restore import create_local_path_from_backup_zip_file, find_git_folder

class TestRestore(unittest.TestCase):

    def setUp(self):
        self.temp_dir = tempfile.mkdtemp()

    def tearDown(self):
        shutil.rmtree(self.temp_dir)

    def test_create_local_path_from_backup_zip_file(self):
        # Crear un archivo de prueba ZIP
        zip_file_path = os.path.join(self.temp_dir, 'repo-test.zip')
        with open(zip_file_path, 'w'):
            pass  # Aquí deberías añadir contenido al archivo ZIP, como las carpetas y archivos esperados

        # Ejecutar la función bajo prueba
        local_path = create_local_path_from_backup_zip_file(zip_file_path)

        # Verificar si la carpeta local se creó correctamente
        expected_local_path = os.path.join(self.temp_dir, 'temp_restore')
        self.assertEqual(local_path, expected_local_path)
        self.assertTrue(os.path.exists(local_path))
        self.assertTrue(os.path.isdir(local_path))

        # También podrías verificar si los archivos esperados están presentes en la carpeta local

    def test_find_git_folder(self):
        # Crear una estructura de carpeta con una carpeta .git de prueba
        test_repo_path = os.path.join(self.temp_dir, 'test_repo')
        os.makedirs(os.path.join(test_repo_path, '.git'))

        # Ejecutar la función bajo prueba
        git_folder = find_git_folder(test_repo_path)

        # Verificar si la carpeta .git se encuentra correctamente
        expected_git_folder = os.path.join(test_repo_path, '.git')
        self.assertEqual(git_folder, expected_git_folder)
        self.assertTrue(os.path.exists(git_folder))
        self.assertTrue(os.path.isdir(git_folder))

if __name__ == '__main__':
    unittest.main()
