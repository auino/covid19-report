# covid19-report

*This project is supposed to be used for Italian users. Therefore, the whole content of the generated documents, including the README file, is in Italian language.*

### Introduzione ###

Questo progetto ha lo scopo di raggruppare i dati disponibili pubblicamente da diverse fonti e fornire un report unificato che analizzi e processi i dati per fornire una visione complessiva relativamente all'andamento del Covid-19 in Italia.

L'ultima versione del report è [disponibile online](https://bit.ly/covid19-report-italy).
Indicativamente, questo file viene aggiornato quasi quotidianamente.

### Caratteristiche del software ###

* Report a livello nazionale, regionale e provinciale
* Report generato a partire da un documento Latex
* Integrazione con i dati della protezione civile (grazie a [@pcm-dpc](https://github.com/pcm-dpc/COVID-19))
* Integrazione con i dati relativi alla somministrazione dei vaccini (grazie a [@italia](https://github.com/italia))
* Integrazione con i dati relativi all'indice Rt (grazie a [@CloudItaly](https://github.com/CloudItaly/Indice-RT))
* Integrazione con [Google News](http://news.google.com)
* Supporto ad una visualizzazione specifica delle diverse ondate che caratterizzano la diffusione del virus

### Sorgenti dati utilizzate ###

* [pcm-dpc/COVID-19](https://github.com/pcm-dpc/COVID-19) per il recupero di dati a livello nazionale, regionale e provinciale
* [italia/covid19-opendata-vaccini](https://github.com/italia/covid19-opendata-vaccini)] per il recupero dei dati relativi alla somministrazione dei vaccini
* [CloudItaly/Indice-RT](https://github.com/CloudItaly/Indice-RT) per il recupero dei dati regionali relativi all'indice Rt misurato
* [Google News](http://news.google.com) per ricerca di notizie in tema Covid-19

### Utilizzo del software ###

* Clonare il repository:
```
git clone https://github.com/auino/covid19-report.git
```
* Accedere alla directory del programma:
```
cd covid19-report
```
* Opzionalmente, nel caso in cui il software debba essere eseguito su un dispositivo quale ad esempio il Raspberry PI, sostituire la riga `FROM` all'interno del `Dockerfile` con la seguente:
```
FROM balenalib/rpi-raspbian:latest
```
* Compilare il container Docker:
```
docker build -t covid19-report .
```
* Opzionalmente, salvare l'immagine Docker su file:
```
docker save covid19-report:latest|gzip > covid19-report.tar.gz
```
* Eseguire il container Docker:
```
docker run -v `pwd`:/app -w /app covid19-report:latest
```

Il container terminerà l'esecuzione una volta generato il nuovo report.
E' pertanto possibile avviare il container automaticamente ad un orario prestabilito, utilizzando ad esempio `cron`.

### TODO ###

A seguire un elenco tentativo di miglioramenti da apportare (ogni aiuto è ben accetto):

* Miglioramento della presentazione del codice del software Python, migliorando i commenti e rendendolo più modulare al fine di agevolare eventuali estensioni
* Miglioramento del report generato, aggiungendo fonti, bibliografia e migliorando i contenuti e la loro esposizione
* Migliore supporto ai dati relativi alle vaccinazioni
* Supporto a dati provenienti da altri paesi (ad esempio, sulla base dei dati disponibili su [CSSEGISandData/COVID-19](https://github.com/CSSEGISandData/COVID-19) o integrando link ai report disponibili sul [sito ISS](https://www.epicentro.iss.it/coronavirus/sars-cov-2-sorveglianza-dati))

### Contatti ###

E' possibile trovarmi su [Twitter](https://twitter.com) come [@auino](https://twitter.com/auino).
