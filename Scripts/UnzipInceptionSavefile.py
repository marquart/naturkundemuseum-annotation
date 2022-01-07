import os
from tempfile import TemporaryDirectory
from zipfile import ZipFile

def modification_time(filepath):
    stats = os.stat(filepath)
    return stats.st_mtime


def extractXMI(project_dir, target_dir):
    '''Extracts all individual annotated XMI-Files of the latest INCEpTION-Project-Savefile in project_dir to target_dir
    '''
    if project_dir.endswith(".zip"): last_save = project_dir
    else: last_save = sorted([os.path.join(project_dir, file) for file in os.listdir(project_dir)], key=modification_time, reverse=True)[0]
    print("Last saved Project File: ", last_save)
    
    processed_files = set()
    with TemporaryDirectory() as tmp:
        print("Temporary Directory: ", tmp, '\n\nLog:')
        with ZipFile(last_save, 'r') as zip:
            for file in zip.namelist():
                if file.startswith("annotation/"):
                    zip.extract(file, path=tmp)
        os.mkdir(os.path.join(tmp, "XMI"))
        
        for root, _, files in os.walk(os.path.join(tmp, "annotation")):
            #print("root", root)
            #print("files", files)
            
            for file in files:
                if file.endswith('.zip'):
                    name = os.path.basename(root).rstrip(".txt")
                    
                    with ZipFile(os.path.join(root, file), 'r') as zip:
                        zip.extract("admin.xmi", path=os.path.join(tmp, "XMI"))
                    
                    assert name not in processed_files
                    os.replace(os.path.join(tmp, "XMI", "admin.xmi"), os.path.join(target_dir, f"{name}.xmi"))
                    
                    print("    Found", name)
                    processed_files.add(name)
            
            
    print("\nProccessed:\n   ", '\n    '.join(processed_files))
    print(f"\nSaved in '{target_dir}' as:\n   ", '\n    '.join(os.listdir(target_dir)))
    

if __name__ == "__main__":
    target_dir = "C:/Users/Aron/Documents/Naturkundemuseum/naturkundemuseum-annotation/Data/INCEpTION/UIMA_CAS_XMI"
    project_dir = "C:/Users/Aron/Documents/Naturkundemuseum/naturkundemuseum-annotation/Data/INCEpTION/Saved_projects"
    extractXMI(project_dir, target_dir)
