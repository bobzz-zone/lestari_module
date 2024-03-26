import csv
import pandas as pd
import frappe
from datetime import datetime, date # from python std library
from frappe.utils import add_to_date

# Fungsi untuk membaca file CSV dan menggunakan baris pertama sebagai key
def read_csv_with_header_as_key(file_path):
    with open(file_path, 'r', newline='', encoding='utf-8') as file:
        reader = csv.reader(file)
        
        # Membaca baris pertama sebagai header
        header = next(reader)

        # Membaca sisa baris sebagai data
        data = list(reader)

    # Membuat variabel untuk menyimpan hasil akhir
    result_data = []

    # Iterasi melalui data untuk mengelompokkan berdasarkan kolom 2 dan 3
    current_group = []
    for row in data:
        if current_group and (row[1], row[2]) != current_group[-1][1:3]:
            # Jika group berubah, tambahkan ke result_data
            result_data.append(current_group)
            current_group = []

        current_group.append(row[4:16])

    # Menambahkan group terakhir
    result_data.append(current_group)

    # Membuat DataFrame dari hasil akhir
    df = pd.DataFrame()

    for group in result_data[1:]:
        df = pd.concat([df, pd.DataFrame(group, columns=header[4:16])], ignore_index=True)

    # Menyimpan DataFrame ke dalam file CSV
    df.to_csv("/home/frappe/frappe-bench/apps/lestari/lestari/filtered_data2.csv", index=False)


# # Menggunakan contoh file CSV
# file_path = "/home/frappe/frappe-bench/apps/lestari/lestari/Transfer_Barang_Jadi.csv"
# result = read_csv_with_header_as_key(file_path)

# # Menampilkan hasil
# print((result))

@frappe.whitelist()
def read_csv_arik():
# Read and store content 
# of an excel file
    read_file = pd.read_csv('/home/frappe/frappe-bench/apps/lestari/lestari/Transfer_Barang_Jadi.csv')

    df = read_file.head()

    header = []

    for data in read_file.values:
        baris_baru = {
            'no_spk':data[9],
            'no_fo':data[10],
            'sub_kategori':data[11],
            'kadar':data[12],
            'qty':data[13],
            'berat':data[14]
        }
        dataku = {
            "tanggal":data[2],
            "kadar":data[3],
            "item":1,
            "id":""
        }
        
        if len(header) == 0:
            # Nggawe sek
            tbj = frappe.new_doc('Transfer Barang Jadi')
            datep = datetime.strptime(data[4], '%d/%m/%Y')
            tbj.posting_date = datep.strftime('%Y-%m-%d')
            tbj.posting_time = data[5]
            tbj.penerima = data[1]
            tbj.employee = data[7]
            tbj.kadar = data[3]
            print(tbj.name)
            tbj.append('items',baris_baru)
            tbj.flags.ignore_permissions = True
            tbj.save()
            # oleh id
            dataku['id'] = tbj.name
            header.append(dataku)
            continue

        for index,data2 in enumerate(header):
            if data2["tanggal"] == dataku["tanggal"] and data2["kadar"] == dataku['kadar']:
                tbj = frappe.get_doc('Transfer Barang Jadi', header[index]['id'])
                # baris_baru = {
                #     'no_spk':data[9],
                #     'no_fo':data[10],
                #     'sub_kategori':data[11],
                #     'kadar':data[12],
                #     'qty':data[13],
                #     'berat':data[14]
                # }
                tbj.append('items',baris_baru)
                tbj.flags.ignore_permissions = True
                tbj.save()
                header[index]["item"] = header[index]["item"] + 1
                break
        else:
             # Nggawe sek
            tbj = frappe.new_doc('Transfer Barang Jadi')
            datep = datetime.strptime(data[4], '%d/%m/%Y')
            tbj.posting_date = datep.strftime('%Y-%m-%d')
            tbj.posting_time = data[5]
            tbj.penerima = data[1]
            tbj.employee = data[7]
            tbj.kadar = data[3]
            tbj.append('items',baris_baru)
            tbj.flags.ignore_permissions = True
            tbj.save()
            print(tbj.name)
            # oleh id
            dataku['id'] = tbj.name
            header.append(dataku)

    print(header)
    # loop read_file to check date
    # for i in read_file.rows:
    #     print(i)