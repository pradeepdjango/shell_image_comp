# getting files with starting letters


          import os
          import shutil
          import zipfile
          
          def copy_files_by_name(level, name, path):
              
              hierarchy_dirs = []
          
              
              for root, dirs, files in os.walk(path):
                  if name in dirs:
                  
                      hierarchy_dirs.append(os.path.join(root, name))
          
              
              if hierarchy_dirs:
                  print("Hierarchy directories found:", hierarchy_dirs)
                  
                  
                  new_dir = os.path.join(os.getcwd(), 'copied_files')
                  os.makedirs(new_dir, exist_ok=True)
                  
                  
                  for directory in hierarchy_dirs:
                   
                      files = os.listdir(directory)
                      
                     
                      for file in files:
                          if file.startswith(str(level)):
                              file_path = os.path.join(directory, file)
                              shutil.copy(file_path, new_dir)
                              print("Copied file:", file)  
                      
                  
                  zip_file_path = os.path.join(os.getcwd(), 'copied_files.zip')
                  with zipfile.ZipFile(zip_file_path, 'w') as zipf:
                      for directory in hierarchy_dirs:
                          for root, dirs, files in os.walk(directory):
                              for file in files:
                                  if file.startswith(str(level)):
                                      file_path = os.path.join(root, file)
                                      zipf.write(file_path, os.path.relpath(file_path, path))
                      
                  print("Files copied and zipped successfully.")
              else:
                  print("No hierarchy directories found.")
          
          
          copy_files_by_name(1098, 'Snacks', '/home/pradeepsimba/Downloads/OneDrive_2024-02-05/')
