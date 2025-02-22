# SafeChat


## Predstavitev
Jaz sem Samo Borzatta, dijak 4. letnika Gimnazije Vič. Moj profesor za informatiko je Klemen Bajec.


## Opis programa

SafeChat je program, ki sem ga ustvaril kot projektno delo za maturo. Podroben opis programa se nahaja v word dokumentu, ki je poročilo programa.


## Navodila za testiranje

Program je v takem stanju, ki omogoča boljšo testiranje. Potrebno je zagnati različne programe, da prične delovati.

### 1. Nastavitev paketov

Za delovanje potrebujemo več pythonovih knjižnic.
```
pip install socket
pip install cryptography
```

### 2. Ustvarjanje strežnika

Za začetek se premaknemo v mapo SafeChat `cd SafeChat`. Vse programe je potrebno zagnati iz te lokacije da se izognem ne delovanju poti.
Da stržežnik lahko prične z delovanjem, moramo najprej ustvariti njegov javni in zasebni ključ, da lahko pošljem podatke enkriptirane. Program bo vprašal po geslu, ki si ga je potrbno zapomniti, ker je to kasneje geslo za zagon strežnika.

**Zaradi uporabe krajšega javnega ključa je najdaljša dolžina enkriptiranega sporočila 256 mest!**
```
python server/keys/generate_keys.py
```

Nato ustvarimo sqlite bazo, ki bo shranila uporabniške podatke. Baza bo prav tako vnesla uporabnika _test_ z geslom _1234_, katerega podatki so tudi shranjeni v mapi `client`.
```
python server/Database/baza.py
```
Nazadnje zaženemo strežnik.

```
python server/server.py
```

### 3. Prijava uporabnikov

En uporabnik je bil že ustvarjen v testne namene. Zaženemo ga z naslednjim ukazom.
```
python client/client.py
```

Drugi uporabnik pa je še neregistriran zato je potrebna še registracija. Najprej ustvarimo ključa za asimetrično enkripcijo.
```
python client2/keys/generate_keys.py
```
Nato pa zaženemo drugega uporabnika in sledimo navodilom.
```
python client2/client.py
```