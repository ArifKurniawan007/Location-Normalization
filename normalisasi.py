from flask import Flask, jsonify
import pandas as pd
import random
import re

data_kota = pd.read_csv("data/data_kota2.csv")
path='data/data lokasi/'
df_kecamatan=pd.read_csv(path+'kecamatan.csv') #distrik
df_kelurahan=pd.read_csv(path+'kelurahan.csv') #village
df_kotakab=pd.read_csv(path+'kotakab.csv') #regensi
df_provinsi=pd.read_csv(path+'provinsi.csv') #provinsi
data_kota_malaysia = pd.read_excel("data/data_kota_malaysia.xlsx","Sheet1")
data_kota_bangladesh = pd.read_excel("data/data_kota_bangladesh.xlsx","Sheet1")

def predict_kota_in(alamat,data_kota):
    kt = {"City":'Undefined',"State":"Undefined","Country":"Undefined"}
    nama_kota = []
    nama_state = []
    for j in range(len(data_kota)):
        if "yogyakarta" not in alamat.strip().lower() and "bandung" not in alamat.strip().lower() and \
        "malang" not in alamat.strip().lower() and "kediri" not in alamat.strip().lower() and\
        "pekalongan" not in alamat.strip().lower() and "bogor" not in alamat.strip().lower() and\
        "cirebon" not in alamat.strip().lower() and "semarang" not in alamat.strip().lower() and\
        "bekasi" not in alamat.strip().lower():
            if data_kota["kota"][j].lower() in alamat.strip().lower() or \
            data_kota["kota"][j].lower().replace(" ","") in alamat.strip().lower() or \
            data_kota["kota english"][j].lower() in alamat.strip().lower() or \
            data_kota["kota"][j].lower().replace("kota ","") in alamat.strip().lower():
                state = data_kota[data_kota["kota"]==data_kota["kota"][j]].reset_index(drop=True)
                nama_kota.append(data_kota["kota"][j])
                nama_state.append(state["provinsi"][0])

        else:
            if data_kota["kota"][j].lower() in alamat.strip().lower() or \
            data_kota["kota"][j].lower().replace(" ","") in alamat.strip().lower() or \
            data_kota["kota english"][j].lower() in alamat.strip().lower():
                state = data_kota[data_kota["kota"]==data_kota["kota"][j]].reset_index(drop=True)
                nama_kota.append(data_kota["kota"][j])
                nama_state.append(state["provinsi"][0])

    count_word = [len(l.split(' ')) for l in nama_kota]
    count_huruf = [len(l) for l in nama_kota]
    for i in range(len(nama_kota)):
        if len(set(count_word)) > 1:
            if len(nama_kota[i].split(" ")) == max(count_word):
                kt = {"City":nama_kota[i],"State":nama_state[i],"Country":"Indonesia"}
                break
        else:
            if max(count_huruf) > 4:
                if len(nama_kota[i]) == max(count_huruf):
                    kt = {"City":nama_kota[i],"State":nama_state[i],"Country":"Indonesia"}
                    break
    return kt

def predict_provinsi_in(alamat,data_kota, df_provinsi):
    kt = {"City":'Undefined',"State":"Undefined","Country":"Undefined"}
    code_prov = pd.DataFrame({})

    # lists = ["jatim","jateng","jabar"]
    if "jatim" in alamat.lower():
        a = re.findall(r"jati\w+",alamat.lower())
        for k in a:
            if k == "jatim":
                code_prov = df_provinsi[df_provinsi["provinsi"] == "JAWA TIMUR"].reset_index(drop=True)
                pr = list(code_prov.index)[0]
                break
    else:
        for pr in range(len(data_kota)):
            if data_kota["provinsi"][pr].lower() in alamat.strip().lower() or \
            data_kota["singkatan_provinsi"][pr].lower() in alamat.strip().lower():
                prov = data_kota["singkatan_provinsi"][pr]
                # if prov=='jatim' or prov=="jabar" or prov=="jateng":
                if len(alamat)==alamat.find(prov)+len(prov) and alamat.find(prov)!=0 and alamat[alamat.find(prov)-1]==' ':
                    code_prov = df_provinsi[df_provinsi["provinsi"]==data_kota["provinsi"][pr].upper()].reset_index(drop=True)
                    break
                elif prov.lower()!='jatim' and prov.lower()!="jabar" and prov.lower()!="jateng" and prov.lower()!="bali":
                    code_prov = df_provinsi[df_provinsi["provinsi"] == data_kota["provinsi"][pr].upper()].reset_index(
                        drop=True)
                    break


    if len(code_prov) > 0:
        code_kotakab = "zero"
        if data_kota["singkatan_provinsi"][pr].lower() != "jakarta":
            alamat = alamat.replace(data_kota["provinsi"][pr].lower(), "")
            alamat = alamat.replace(data_kota["singkatan_provinsi"][pr].lower(),"")
        code_prov = code_prov["code_provinsi"][0]

        cek_kota = data_kota[data_kota["provinsi"]==data_kota["provinsi"][pr]]
        nama_cek_kota = []
        for ck in set(cek_kota["kota"]):
            if ck.lower() in alamat.strip().lower():
                nama_cek_kota.append(ck)
        limit_nama_cek_kota = [len(i) for i in nama_cek_kota]
        for nck in nama_cek_kota:
            if len(nck) == max(limit_nama_cek_kota):
                kt = {"City":nck,"State":data_kota["provinsi"][pr],"Country":"Indonesia"}

        if kt["State"]=="Undefined":
            kec = [i for i in df_kecamatan["code_kecamatan"] if str(i)[:2]==str(code_prov)]
            kec = pd.DataFrame({"code_kecamatan":kec})
            kec = df_kecamatan.merge(kec,how="inner",on="code_kecamatan")
            for k in range(len(kec)):
                if kec["kecamatan"][k].lower() in alamat.lower() or kec["name_kecamatan"][k].lower() in alamat.lower():
                    code_kotakab = kec["code_kotakab"][k]
                    break
            if code_kotakab != "zero":
                kotakab = df_kotakab[df_kotakab["code_kotakab"]==code_kotakab].reset_index(drop=True)
                for cek in data_kota["kota"]:
                    if cek.upper() in kotakab["kotakab"][0]:
                        new = data_kota[data_kota["kota"]==cek].reset_index(drop=True)
                        kt = {"City":cek,"State":new["provinsi"][0],"Country":"Indonesia"}
                        break
        if kt["State"]=="Undefined":
            kec = [i for i in df_kelurahan["code_kecamatan"] if str(i)[:2] == str(code_prov)]
            kec = pd.DataFrame({"code_kecamatan": kec})
            kec = df_kelurahan.merge(kec, how="inner", on="code_kecamatan")
            for k in range(len(kec)):
                if kec["kelurahan"][k].lower() in alamat.lower() or kec["name_kelurahan"][k].lower() in alamat.lower():
                    code_kotakab = int(str(kec["code_kecamatan"][k])[:4])
                    break
            if code_kotakab != "zero":
                kotakab = df_kotakab[df_kotakab["code_kotakab"] == code_kotakab].reset_index(drop=True)
                for cek in data_kota["kota"]:
                    if cek.upper() in kotakab["kotakab"][0]:
                        new = data_kota[data_kota["kota"] == cek].reset_index(drop=True)
                        kt = {"City": new["kota"][0], "State": new["provinsi"][0],"Country":"Indonesia"}
                        break
    return kt

def predict_only_kec_kel_in(alamat,data_kota):
    alamat = alamat.replace(" ","")
    kt = {"City":'Undefined',"State":"Undefined","Country":"Undefined"}
    code_kotakab = "zero"
    code_lurah = []
    lurah = []

    code_camat = []
    camat = []
    for k in range(len(df_kecamatan)):
        if df_kecamatan["kecamatan"][k].lower() in alamat.lower() or \
        df_kecamatan["name_kecamatan"][k].lower() in alamat.lower():
            code_kotakab = df_kecamatan["code_kotakab"][k]
            code_camat.append(code_kotakab)
            camat.append(df_kecamatan["kecamatan"][k])


    limit_lurah = [len(l) for l in lurah]
    limit_camat = [len(l) for l in camat]

    if len(limit_camat) > 0 and len(limit_lurah) == 0:
        if len(set(limit_camat)) > 1:
            for num in range(len(camat)):
                if len(camat[num]) == max(limit_camat):
                    code_kotakab = code_camat[num]
        else:
            code_kotakab = code_camat[0]
        if code_kotakab != "zero":
            kotakab = df_kotakab[df_kotakab["code_kotakab"]==code_kotakab].reset_index(drop=True)
            for cek in range(len(data_kota["kota"])):
                if data_kota["kota"][cek].upper() in kotakab["kotakab"][0]:
                    kt = {"City":data_kota["kota"][cek],"State":data_kota["provinsi"][cek],"Country":"Indonesia"}
                    break

    return kt

def predict_kota(alamat, data_kota):
    alamat = alamat.lower().replace("indonesia", "")
    alamat = re.findall(r"[A-z]\w+", alamat.lower())
    alamat = " ".join(alamat)
    alamat = alamat.replace("jaksel", "jakarta selatan").replace("jakpus", "jakarta pusat")
    alamat = alamat.replace("jakbar", "jakarta barat").replace("jakut", "jakarta utara")
    alamat = alamat.replace("jaktim","jakarta timur")


    kt = {"City": 'Undefined', "State": "Undefined","Country":"Undefined"}

    # jika provinsi ada dalam alamat
    if kt["State"] == "Undefined":
        kt = predict_provinsi_in(alamat, data_kota, df_provinsi)

    # jika kota ada di alamat
    if kt["State"] == "Undefined":
        kt = predict_kota_in(alamat, data_kota)

    # jika jakarta ada dalam alamat
    if kt["State"] == "Undefined":
        if "jakarta" in alamat.lower():
            kt = {"City": "Undefined", "State": "DKI Jakarta","Country":"Indonesia"}
        elif "yogyakarta" in alamat.lower():
            kt = {"City": "Undefined", "State": "DI Yogyakarta","Country":"Indonesia"}
        else:
            for p in range(len(data_kota)):
                if data_kota["provinsi"][p].lower() in alamat.strip().lower() or \
                                data_kota["singkatan_provinsi"][p].lower() in alamat.strip().lower():
                    kt = {"City":"Undefined","State":data_kota["provinsi"][p],"Country":"Indonesia"}

    # jika provinsi tidak ada dan kota tidak ada
    if kt["Country"] == "Undefined":
        kt = predict_only_kec_kel_in(alamat, data_kota)

    return kt

def normalisasi_gender(gender):
    hasil = 'Undefined'
    if "female" not in gender.lower() or "laki-laki" in gender.lower() or "cowok" in gender.lower() or \
                    "pria" in gender.lower():
        hasil = "male"
    elif "female" in gender.lower() or "perempuan" in gender.lower() or "cewek" in gender.lower() or\
            "wanita" in gender.lower():
        hasil = "female"
    return hasil

app = Flask(__name__)
@app.route("/normalisasi_v2/location=<alamat>", methods=["GET"])
def location(alamat):
    return jsonify(predict_kota(alamat,data_kota))

@app.route("/normalisasi_v2/gender=<gender>", methods=["GET"])
def genders(gender):
    return normalisasi_gender(gender)

if __name__ == '__main__':
    app.run(debug=True)