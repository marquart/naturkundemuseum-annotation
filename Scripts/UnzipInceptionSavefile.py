import os
from tempfile import TemporaryDirectory
from zipfile import ZipFile

def modification_time(filepath):
    stats = os.stat(filepath)
    return stats.st_mtime

if __name__ == "__main__":
    savedir = "C:/Users/Aron/Documents/Naturkundemuseum/naturkundemuseum-annotation/Data/INCEpTION/UIMA_CAS_XMI"
    project = "C:/Users/Aron/Documents/Naturkundemuseum/naturkundemuseum-annotation/Data/INCEpTION/Saved_Projects"
    
    last_save = sorted([os.path.join(project, file) for file in os.listdir(project)], key=modification_time, reverse=True)[0]
    print("Last Project File: ", last_save)
    

    with TemporaryDirectory() as tmp:
        print("Temporary Directory: ", tmp, '\n\nLog:')
        with ZipFile(last_save, 'r') as zip:
            for file in zip.namelist():
                if file.startswith("annotation/"):
                    zip.extract(file, path=tmp)
        os.mkdir(os.path.join(tmp, "XMI"))
        processed_files = set()
        
        for root, _, files in os.walk(os.path.join(tmp, "annotation")):
            #print("root", root)
            #print("files", files)
            
            for file in files:
                if file.endswith('.zip'):
                    name = os.path.basename(root).rstrip(".txt")
                    
                    with ZipFile(os.path.join(root, file), 'r') as zip:
                        zip.extract("admin.xmi", path=os.path.join(tmp, "XMI"))
                    
                    assert name not in processed_files
                    os.replace(os.path.join(tmp, "XMI", "admin.xmi"), os.path.join(savedir, f"{name}.xmi"))
                    
                    print("    Found", name)
                    processed_files.add(name)
            
            
        print("\nProccessed:\n   ", '\n    '.join(processed_files))
        print(f"\nSaved in '{savedir}' as:\n   ", '\n    '.join(os.listdir(savedir)))
