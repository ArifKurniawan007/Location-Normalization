# Location-Normalization
This script used to normalization an address in 3 section ie city, state, and coutry. 
Method was used is lookup an address in a file state/city/districts. 
Normalization was maked specifics to an address in Indonesia.
Example : input = "Jatimakmur, pondok gede"
          output = {"City": "Bekasi", "State":"Jawa Barat", "Country":"Indonesia"}

This is a API so that can be accessed with request in python or web browser.
How to run script (with ubuntu terminanator / commend line):
1. move to folder normalisasi.py
2. run with "python normalisasi.py"

How to get output:
1. Web Browser
   http://localhost:5000/normalisasi_v2/location=jatimakmur,%20pondok%20gede
2. Request Python
   import request
   request.get("http://localhost:5000/normalisasi_v2/location=jatimakmur,%20pondok%20gede")
