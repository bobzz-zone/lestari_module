import openpyxl
import frappe

def importdata():
    wb = openpyxl.load_workbook('/home/frappe/lestari-bench/apps/lestari/lestari/lestari/doctype/pemakaian_bahan_pembantu_per_bulan/data.xlsx')
    sheet = wb['Pemakaian Per Bulan 2023']

    data = []
    for row in sheet.iter_rows(values_only=True):
        data.append(row)

    wb.close()

    header = data[0]
    del data[0]

    for row in data:
        if row[0] != None:
            for i in range(0,13):
                if i == 0:
                    pemakaian = str(row[0])
                else:
                    if ((row[i] != None)&(row[i] != 0)):
                        print(pemakaian+' Bulan '+str(i)+' '+str(row[i]))
                        new_doc = frappe.get_doc({
                            'doctype': 'Pemakaian Bahan Pembantu Per Bulan',
                            'pemakaian_bahan_pembantu': pemakaian,
                            'bulan': i,
                            'pemakaian': row[i],
                            'tahun': 2023
                        })
                        new_doc.save()
                        print(new_doc.name)
    frappe.db.commit()

