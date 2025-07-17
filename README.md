# Gestiune Downloads - Organizator Automat de Fisiere

## Descriere

**Gestiune Downloads** este o aplicatie Python gandita sa te ajute sa-ti pastrezi fisierele descarcate in ordine, fara sa mai faci asta manual. Cand descarci ceva, fie ca e film, muzica, un document sau un program, aplicatia le muta automat in foldere bine structurate. Se uita la extensia si numele fisierului, iar pentru filme cauta pe internet anul aparitiei.

Foloseste serviciul **OMDb API** pentru a obtine informatii despre filme (cum ar fi anul lansarii) si organizeaza fisierele astfel:

```
Media/
├── Movies/
│   └── 2010/
│       └── Inception/
│           └── Inception.mp4
├── Series/
│   └── Breaking Bad/
│       └── Season_1/
│           └── Episode_1/
├── Music/
│   └── Eminem/
│       └── Lose Yourself.mp3
Documents/
Executables/
```

Toate mutarile sunt inregistrate intr-un fisier de log: `logs/log.txt`, asa ca poti vedea ce s-a intamplat oricand.

---

## Ce face aplicatia

* Muta automat fisierele in foldere potrivite
* Recunoaste tipul fisierului chiar si daca nu are extensie
* Pentru filme, cauta anul aparitiei online
* Creeaza structuri de foldere clare si usor de urmarit
* Poti porni scriptul manual sau sa-l faci sa ruleze automat la fiecare pornire a calculatorului


---

## Cum o folosesti

1. Instaleaza ce ai nevoie:

```bash
pip install requests
```

2. Ruleaza scriptul:

```bash
python gestiune_downloaduri.py
```

3. Sau, daca vrei sa se porneasca singur:

* Adauga scriptul in `shell:startup`
* Sau programeaza-l cu Task Scheduler

---

## OMDb API – pentru filme

Fa-ti un cont gratuit pe [https://www.omdbapi.com/](https://www.omdbapi.com/) si ia o cheie API. Dupa ce o ai, pune-o in cod:

```python
OMDB_API_KEY = "cheia_ta_omdb"
```

---



## Exemplu de log

```
2025-07-17 12:32:10 - INFO - [Film] Mutat: Inception.mp4 -> Media/Movies/2010/Inception
2025-07-17 12:32:11 - INFO - [Muzica] Mutat: Eminem - Lose Yourself.mp3 -> Media/Music/Eminem
2025-07-17 12:32:12 - INFO - [Serial] Mutat: Breaking.Bad.S01E01.mkv -> Media/Series/Breaking Bad/Season_1/Episode_1
```

---

Aplicatia este utila in special pentru:

mentinerea ordinii si claritatii in sistemul de fisiere;

economisirea timpului si efortului atunci cand se descarca multe fisiere diverse;

organizarea media (filme, muzica, seriale) intr-un mod coerent si accesibil;

asigurarea ca fisierele importante (documente sau executabile) nu raman uitate in folderul Downloads.



---

