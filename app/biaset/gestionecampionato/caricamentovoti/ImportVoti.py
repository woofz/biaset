import pandas as pd
import wget
import csv
import os
import requests
from bs4 import BeautifulSoup
from gestionecampionato.models import Voto


class ImportVoti:

    def __init__(self, giornata: int):
        self._giornata = giornata

    def vote_download(self) -> None:
        print(f"Downloading data for day number {self._giornata} ...")
        giornata = str(self._giornata)
        marks_url = 'https://www.fantacalcio.it/voti-fantacalcio-serie-a/2021-22/' + giornata
        token = self.get_token(marks_url)
        url = 'http://www.fantacalcio.it/Servizi/Excel.ashx?type=1&g=' + giornata + '&t=' + token + '&s=2021-22'
        file_loc = 'voti_giornata_' + giornata + '.xlsx'
        wget.download(url, file_loc)

        df = pd.read_excel(file_loc, index_col=None, na_values=['6*'], skiprows=5)
        df.fillna('-100', inplace=True)

        file_name = 'def_' + giornata + '.csv'
        df.to_csv(file_name, index=False, header=False)
        print("\nDownload completed... ")
        self.import_into_db(fileName=file_name, giornata=self._giornata)
        os.remove(file_loc)

    @staticmethod
    def import_into_db(fileName: str, giornata: int) -> None:
        print("Importing data into db...")

        allData = csv.reader(open(fileName, 'r'), delimiter=',', quotechar='|')
        lista_voti = []
        for row in allData:
            print(row)
            lista_voti.append(
                Voto(id_voti=row[0],
                     ruolo=row[1],
                     nome_giocatore=row[2],
                     voto=row[3],
                     gf=row[4],
                     gs=row[5],
                     rp=row[6],
                     rs=row[7],
                     rf=row[8],
                     au=row[9],
                     amm=row[10],
                     esp=row[11],
                     ass=row[12],
                     gdv=row[13],
                     gdp=row[14],
                     giornata=giornata)
            )
        Voto.objects.bulk_create(lista_voti)
        Voto.objects.filter(ruolo='-100').delete()
        Voto.objects.filter(ruolo='ALL').delete()
        Voto.objects.filter(ruolo='Ruolo').delete()
        print("Procedure finished successfully!")
        os.remove(fileName)

    @staticmethod
    def get_token(url: str) -> str:
        response = requests.get(url)
        soup = BeautifulSoup(response.text, features="html.parser")
        token = soup.find(id='tvstamp').get('value')
        return token
