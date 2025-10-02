
import zipfile

jungle_zip = zipfile.ZipFile('jungle.zip', 'w')
jungle_zip.write('_02_ZipFile.py', compress_type=zipfile.ZIP_DEFLATED)
jungle_zip.close()
print('writing done.')
