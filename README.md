# admx2oma
This script generates OMA-URI and possible config values on base of an windows admx file.
Ingest an admx file into Intune, copy the OMA-URI of the ingestion record and execute this script by supplying the admx file and the copyed OMA-URI.

## exec
```
python admx2oma.py chrome.admx ./Device/Vendor/MSFT/Policy/ConfigOperations/ADMXInstall/Chrome/Policy/ChromeAdmx
```

## install
You need to install python 3 and lxml
```
pip install lxml
```

## bugs
If the script fails to parse your admx file, please send me a copy of the admx.
